"""
阿里云短信查询模块
调用阿里云短信API查询发送明细
"""
from datetime import datetime, timedelta
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models

from config import Config


class SMSQueryClient:
    """短信查询客户端"""
    
    def __init__(self, config: Config):
        """
        初始化客户端
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.client = self._create_client()
    
    def _create_client(self) -> Dysmsapi20170525Client:
        """创建阿里云短信客户端"""
        config = open_api_models.Config(
            access_key_id=self.config.access_key_id,
            access_key_secret=self.config.access_key_secret
        )
        # 短信服务的endpoint
        config.endpoint = f'dysmsapi.aliyuncs.com'
        return Dysmsapi20170525Client(config)
    
    def query_send_details(
        self,
        phone_number: str,
        start_date: str,
        end_date: str = None,
        page_size: int = 50,
        max_workers: int = 10
    ) -> List[Dict]:
        """
        查询短信发送明细（并行版本）
        
        Args:
            phone_number: 手机号码
            start_date: 开始日期，格式：YYYYMMDD
            end_date: 结束日期，格式：YYYYMMDD，默认为开始日期
            page_size: 每页记录数，最多50
            max_workers: 最大并发线程数，默认10
            
        Returns:
            短信发送记录列表
        """
        if end_date is None:
            end_date = start_date
        
        all_records = []
        lock = threading.Lock()  # 用于线程安全地更新记录列表
        
        # 生成日期列表（阿里云API只支持单天查询）
        date_list = self._generate_date_list(start_date, end_date)
        
        print(f"正在查询手机号 {phone_number} 从 {start_date} 到 {end_date} 的短信记录...")
        print(f"共需查询 {len(date_list)} 天的数据")
        print(f"使用 {max_workers} 个并发线程加速查询...\n")
        
        completed_count = 0
        total_count = len(date_list)
        
        # 使用线程池并行查询
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_date = {
                executor.submit(
                    self._query_single_day,
                    phone_number,
                    query_date,
                    page_size
                ): query_date
                for query_date in date_list
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_date):
                query_date = future_to_date[future]
                completed_count += 1
                
                try:
                    day_records = future.result()
                    
                    if day_records:
                        with lock:
                            all_records.extend(day_records)
                        print(f"[{completed_count}/{total_count}] ✓ {query_date} 找到 {len(day_records)} 条记录")
                    else:
                        print(f"[{completed_count}/{total_count}] - {query_date} 无记录")
                        
                except Exception as e:
                    print(f"[{completed_count}/{total_count}] ✗ {query_date} 查询失败: {str(e)}")
        
        # 按时间排序
        all_records.sort(key=lambda x: x['send_time'])
        
        print(f"\n查询完成，共获取 {len(all_records)} 条记录")
        return all_records
    
    def _generate_date_list(self, start_date: str, end_date: str) -> List[str]:
        """
        生成日期列表
        
        Args:
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            
        Returns:
            日期字符串列表
        """
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        
        date_list = []
        current_dt = start_dt
        
        while current_dt <= end_dt:
            date_list.append(current_dt.strftime('%Y%m%d'))
            current_dt += timedelta(days=1)
        
        return date_list
    
    def _query_single_day(
        self,
        phone_number: str,
        query_date: str,
        page_size: int = 50
    ) -> List[Dict]:
        """
        查询单天的短信记录
        
        Args:
            phone_number: 手机号码
            query_date: 查询日期 YYYYMMDD
            page_size: 每页记录数
            
        Returns:
            当天的记录列表
        """
        day_records = []
        current_page = 1
        
        while True:
            request = dysmsapi_20170525_models.QuerySendDetailsRequest(
                phone_number=phone_number,
                send_date=query_date,
                page_size=page_size,
                current_page=current_page
            )
            
            runtime = util_models.RuntimeOptions()
            
            try:
                response = self.client.query_send_details_with_options(
                    request, 
                    runtime
                )
                
                if response.status_code != 200:
                    print(f"  ✗ API调用失败，状态码: {response.status_code}")
                    break
                
                body = response.body
                
                if body.code != 'OK':
                    # 如果是没有记录，不打印错误
                    if body.code != 'isv.MOBILE_NUMBER_ILLEGAL' and 'no result' not in str(body.message).lower():
                        print(f"  ✗ 查询失败: {body.message}")
                    break
                
                # 解析发送记录
                if body.sms_send_detail_dtos and body.sms_send_detail_dtos.sms_send_detail_dto:
                    records = body.sms_send_detail_dtos.sms_send_detail_dto
                    
                    for record in records:
                        # 解析发送时间
                        send_time = self._parse_send_time(record.send_date)
                        
                        day_records.append({
                            'phone_number': record.phone_num,
                            'send_time': send_time,
                            'status': self._parse_status(record.send_status),
                            'content': record.content or '',
                            'template_code': record.template_code or ''
                        })
                    
                    # 检查是否还有更多页
                    if len(records) < page_size:
                        break
                    
                    current_page += 1
                    print(f"    获取第 {current_page-1} 页...")
                else:
                    # 没有更多记录
                    break
                    
            except Exception as e:
                print(f"  ✗ 查询出错: {str(e)}")
                break
        
        return day_records
    
    def _parse_send_time(self, send_date: str) -> str:
        """
        解析发送时间
        
        Args:
            send_date: 发送日期时间字符串
            
        Returns:
            格式化的时间字符串
        """
        if not send_date:
            return ''
        
        try:
            # 阿里云返回的时间格式通常为：2023-11-03 15:30:00
            dt = datetime.strptime(send_date, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return send_date
    
    def _parse_status(self, status: int) -> str:
        """
        解析发送状态
        
        Args:
            status: 状态码
            
        Returns:
            状态描述
        """
        status_map = {
            1: '等待回执',
            2: '发送失败',
            3: '发送成功'
        }
        return status_map.get(status, f'未知状态({status})')
    
