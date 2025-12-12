"""
CSV导出模块
将短信查询结果导出为CSV文件
"""
import csv
from typing import List, Dict


def export_to_csv(data: List[Dict], output_file: str):
    """
    导出数据到CSV文件

    Args:
        data: 短信记录列表
        output_file: 输出文件路径
    """
    if not data:
        print("没有数据可导出")
        return

    # 使用 UTF-8-BOM 编码确保 Excel 正确识别中文
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)

        # 写入表头
        headers = ['手机号', '发送时间', '发送状态', '短信内容']
        writer.writerow(headers)

        # 写入数据行
        for record in data:
            row = [
                record.get('phone_number', ''),
                record.get('send_time', ''),
                record.get('status', ''),
                record.get('content', '')
            ]
            writer.writerow(row)

    print(f"成功导出 {len(data)} 条记录到文件: {output_file}")
