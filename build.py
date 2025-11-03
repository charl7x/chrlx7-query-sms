#!/usr/bin/env python3
"""
自动化打包脚本
使用 PyInstaller 将项目打包成独立可执行文件
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """运行命令并显示进度"""
    print(f"\n{'='*60}")
    print(f"正在{description}...")
    print(f"{'='*60}")
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=False,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ {description}失败")
        sys.exit(1)
    
    print(f"✅ {description}完成")
    return True


def check_pyinstaller():
    """检查是否安装了 PyInstaller"""
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
        return True
    except ImportError:
        print("⚠️  未安装 PyInstaller")
        response = input("是否现在安装? (y/n): ")
        if response.lower() == 'y':
            run_command("pip install pyinstaller", "安装 PyInstaller")
            return True
        else:
            print("❌ 需要 PyInstaller 才能打包，退出...")
            sys.exit(1)


def clean_build():
    """清理旧的构建文件"""
    print("\n正在清理旧的构建文件...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已删除: {dir_name}/")
    
    # 清理 .spec 文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"  已删除: {spec_file}")
    
    print("✓ 清理完成")


def build_executable():
    """使用 PyInstaller 构建可执行文件"""
    
    # PyInstaller 命令
    cmd = [
        "pyinstaller",
        "--name=query-sms",              # 可执行文件名称
        "--onefile",                      # 打包成单个文件
        "--console",                      # 控制台应用
        "--clean",                        # 清理临时文件
        "--noconfirm",                    # 不询问确认
        # 添加所需的模块
        "--hidden-import=alibabacloud_dysmsapi20170525",
        "--hidden-import=openpyxl",
        "--hidden-import=dotenv",
        "--hidden-import=click",
        # 主程序入口
        "main.py"
    ]
    
    run_command(' '.join(cmd), "打包可执行文件")


def create_release_package():
    """创建发布包"""
    print("\n正在创建发布包...")
    
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # 复制可执行文件
    exe_path = Path("dist/query-sms")
    if exe_path.exists():
        shutil.copy(exe_path, release_dir / "query-sms")
        # 添加执行权限
        os.chmod(release_dir / "query-sms", 0o755)
        print(f"  ✓ 已复制可执行文件")
    else:
        print("  ❌ 找不到可执行文件")
        sys.exit(1)
    
    # 复制配置文件示例
    shutil.copy("env.example", release_dir / "env.example")
    print(f"  ✓ 已复制配置示例")
    
    # 创建使用说明
    create_usage_guide(release_dir)
    print(f"  ✓ 已创建使用说明")
    
    print(f"\n✅ 发布包已创建在 release/ 目录")
    print(f"\n📦 发布包包含:")
    print(f"  - query-sms          (可执行文件)")
    print(f"  - env.example        (配置文件示例)")
    print(f"  - 使用说明.txt       (快速上手指南)")


def create_usage_guide(release_dir):
    """创建使用说明文件"""
    
    guide_content = """
========================================
阿里云短信查询工具 - 快速使用指南
========================================

一、首次配置
------------

1. 创建配置文件
   复制 env.example 为 .env:
   
   cp env.example .env
   
2. 编辑配置文件
   使用文本编辑器打开 .env 文件，填入您的阿里云凭证：
   
   ALIYUN_ACCESS_KEY_ID=您的AccessKey ID
   ALIYUN_ACCESS_KEY_SECRET=您的AccessKey Secret
   ALIYUN_REGION=cn-hangzhou
   
   ⚠️  注意：请妄善保管 .env 文件，不要泄露给他人


二、使用方法
------------

### 基本用法

./query-sms --phone 手机号 --start-date 开始日期 --end-date 结束日期


### 参数说明

--phone, -p       手机号码（必填）
--start-date, -s  开始日期，格式：YYYYMMDD（默认为今天）
--end-date, -e    结束日期，格式：YYYYMMDD（默认为开始日期）
--output, -o      输出文件名（默认：sms_details.xlsx）
--workers, -w     并发线程数 1-20（默认：10）


### 使用示例

1. 查询今天的短信记录
   ./query-sms -p 13800138000

2. 查询指定日期
   ./query-sms -p 13800138000 -s 20231103

3. 查询时间段
   ./query-sms -p 13800138000 -s 20231101 -e 20231103

4. 自定义输出文件
   ./query-sms -p 13800138000 -s 20231101 -o report.xlsx

5. 查询大时间跨度（使用更高并发）
   ./query-sms -p 13800138000 -s 20240101 -e 20241231 -w 15


三、输出说明
------------

程序会在当前目录生成 Excel 文件，包含以下信息：
- 手机号
- 发送时间
- 发送状态（颜色标记：绿色=成功，红色=失败）
- 短信内容


四、常见问题
------------

Q: 提示找不到配置？
A: 确保已创建 .env 文件并填入正确的阿里云凭证。

Q: 查询不到记录？
A: 检查日期格式（YYYYMMDD）和手机号是否正确。

Q: API调用失败？
A: 检查网络连接和阿里云凭证是否有效。


五、添加到系统路径（可选）
--------------------------

如果想在任何目录下都能使用，可以：

1. 将 query-sms 复制到 /usr/local/bin/
   
   sudo cp query-sms /usr/local/bin/
   
2. 确保配置文件在家目录
   
   mkdir -p ~/.config/query-sms
   cp .env ~/.config/query-sms/
   
   然后修改程序查找配置的路径，或在使用时通过环境变量指定。


========================================
祝您使用愉快！
========================================
"""
    
    guide_path = release_dir / "使用说明.txt"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content.strip())


def main():
    """主函数"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           阿里云短信查询工具 - 自动打包脚本                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # 检查是否在虚拟环境中
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  建议在虚拟环境中运行此脚本")
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            print("已取消")
            sys.exit(0)
    
    try:
        # 1. 检查 PyInstaller
        check_pyinstaller()
        
        # 2. 清理旧文件
        clean_build()
        
        # 3. 构建可执行文件
        build_executable()
        
        # 4. 创建发布包
        create_release_package()
        
        # 5. 清理临时文件
        print("\n正在清理临时文件...")
        if os.path.exists('build'):
            shutil.rmtree('build')
        print("✓ 清理完成")
        
        print("\n" + "="*60)
        print("🎉 打包完成！")
        print("="*60)
        print("\n📦 发布包位置: ./release/")
        print("\n使用方法:")
        print("  cd release")
        print("  cp env.example .env")
        print("  # 编辑 .env 填入阿里云凭证")
        print("  ./query-sms -p 13800138000 -s 20231103")
        print("\n" + "="*60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
