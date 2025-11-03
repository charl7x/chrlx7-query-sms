#!/usr/bin/env python3
"""
阿里云短信查询导出工具
主程序入口
"""
import sys
import os
from datetime import datetime, timedelta
import click

from config import get_config
from sms_query import SMSQueryClient
from excel_export import export_to_excel


@click.command()
@click.option(
    '--phone',
    '-p',
    required=True,
    help='要查询的手机号码'
)
@click.option(
    '--start-date',
    '-s',
    help='开始日期，格式：YYYYMMDD（如：20231103）。默认为今天'
)
@click.option(
    '--end-date',
    '-e',
    help='结束日期，格式：YYYYMMDD（如：20231105）。默认为开始日期'
)
@click.option(
    '--output',
    '-o',
    default='sms_details.xlsx',
    help='输出的Excel文件名，默认为 sms_details.xlsx'
)
@click.option(
    '--workers',
    '-w',
    default=10,
    type=int,
    help='并发查询线程数（1-20），默认为 10。数字越大查询越快，但可能触发API限流'
)
def main(phone, start_date, end_date, output, workers):
    """
    阿里云短信查询导出工具
    
    查询指定手机号在某个时间段内的短信发送明细，并导出为Excel文件。
    
    示例：
    
        python main.py --phone 13800138000 --start-date 20231101 --end-date 20231103
        
        python main.py -p 13800138000 -s 20231103 -o my_sms.xlsx
        
        python main.py -p 13800138000 -s 20231101 -e 20231130 -w 15
    """
    try:
        # 验证和格式化日期
        start_date = _validate_and_format_date(start_date, 'start_date')
        
        if end_date:
            end_date = _validate_and_format_date(end_date, 'end_date')
        else:
            end_date = start_date
        
        # 验证日期范围
        if start_date > end_date:
            click.echo("错误: 开始日期不能晚于结束日期", err=True)
            sys.exit(1)
        
        # 验证手机号格式
        if not _validate_phone_number(phone):
            click.echo("错误: 手机号格式不正确", err=True)
            sys.exit(1)
        
        # 验证并发数
        if workers < 1 or workers > 20:
            click.echo("错误: 并发线程数必须在 1-20 之间", err=True)
            sys.exit(1)
        
        # 输出文件路径处理
        if not output.endswith('.xlsx'):
            output = f"{output}.xlsx"
        
        # 显示查询信息
        click.echo("=" * 60)
        click.echo("阿里云短信查询导出工具")
        click.echo("=" * 60)
        click.echo(f"手机号码: {phone}")
        click.echo(f"开始日期: {_format_date_display(start_date)}")
        click.echo(f"结束日期: {_format_date_display(end_date)}")
        click.echo(f"并发线程: {workers}")
        click.echo(f"输出文件: {output}")
        click.echo("=" * 60)
        click.echo()
        
        # 加载配置
        click.echo("正在加载配置...")
        try:
            config = get_config()
            click.echo("✓ 配置加载成功")
        except ValueError as e:
            click.echo(f"✗ 配置错误: {e}", err=True)
            click.echo("\n提示: 请参考 env.example 文件创建 .env 配置文件", err=True)
            sys.exit(1)
        
        # 创建查询客户端
        click.echo("\n正在初始化阿里云客户端...")
        client = SMSQueryClient(config)
        click.echo("✓ 客户端初始化成功")
        
        # 查询短信记录
        click.echo("\n开始查询短信记录...")
        click.echo("-" * 60)
        records = client.query_send_details(
            phone_number=phone,
            start_date=start_date,
            end_date=end_date,
            max_workers=workers
        )
        click.echo("-" * 60)
        
        if not records:
            click.echo("\n未查询到任何记录")
            sys.exit(0)
        
        # 显示统计信息
        _display_statistics(records)
        
        # 导出到Excel
        click.echo(f"\n正在导出到Excel文件: {output}")
        export_to_excel(records, output)
        
        click.echo("\n✓ 任务完成!")
        click.echo("=" * 60)
        
    except KeyboardInterrupt:
        click.echo("\n\n用户中断操作", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n错误: {str(e)}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def _validate_and_format_date(date_str, field_name):
    """
    验证并格式化日期
    
    Args:
        date_str: 日期字符串
        field_name: 字段名称
        
    Returns:
        格式化后的日期字符串 YYYYMMDD
    """
    if not date_str:
        # 默认使用今天
        return datetime.now().strftime('%Y%m%d')
    
    # 验证格式
    if len(date_str) != 8 or not date_str.isdigit():
        raise ValueError(
            f"{field_name} 格式不正确，应为 YYYYMMDD 格式（如：20231103）"
        )
    
    # 验证日期有效性
    try:
        datetime.strptime(date_str, '%Y%m%d')
    except ValueError:
        raise ValueError(f"{field_name} 不是有效的日期")
    
    return date_str


def _validate_phone_number(phone):
    """
    验证手机号格式
    
    Args:
        phone: 手机号字符串
        
    Returns:
        是否有效
    """
    # 简单验证：11位数字
    return phone.isdigit() and len(phone) == 11


def _format_date_display(date_str):
    """
    格式化日期用于显示
    
    Args:
        date_str: 日期字符串 YYYYMMDD
        
    Returns:
        格式化后的日期字符串 YYYY-MM-DD
    """
    try:
        dt = datetime.strptime(date_str, '%Y%m%d')
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str


def _display_statistics(records):
    """
    显示统计信息
    
    Args:
        records: 记录列表
    """
    total = len(records)
    success = sum(1 for r in records if '成功' in r.get('status', ''))
    failed = sum(1 for r in records if '失败' in r.get('status', ''))
    waiting = total - success - failed
    
    click.echo("\n统计信息:")
    click.echo(f"  总记录数: {total}")
    click.echo(f"  发送成功: {success}")
    click.echo(f"  发送失败: {failed}")
    click.echo(f"  等待回执: {waiting}")


if __name__ == '__main__':
    main()

