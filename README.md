# 阿里云短信查询导出工具

一个简单易用的 Python CLI 工具，用于查询阿里云短信服务中指定手机号在某个时间段内的发送明细，并导出为 CSV 文件。

## 功能特性

- ✅ 查询指定手机号的短信发送记录
- ✅ 支持自定义时间范围查询
- ✅ 自动分页获取所有记录
- ✅ 导出为 CSV 格式（UTF-8-BOM 编码，Excel 兼容）
- ✅ 文件名自动添加时间戳，避免覆盖
- ✅ 多线程并发查询，大幅提升速度
- ✅ 详细的统计信息和进度显示

## 快速开始

### 1. 安装依赖

建议使用虚拟环境：

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
```

### 2. 配置阿里云访问密钥

#### 获取 AccessKey

1. 登录 [阿里云控制台](https://ram.console.aliyun.com/manage/ak)
2. 在右上角头像处选择 "AccessKey管理"
3. 创建 AccessKey（如果还没有）
4. 记录 AccessKey ID 和 AccessKey Secret

⚠️ **安全提示**：请妥善保管您的 AccessKey，不要泄露给他人或提交到代码仓库。

#### 配置环境变量

```bash
# 复制配置示例文件
cp env.example .env

# 编辑 .env 文件，填入您的配置
nano .env
```

`.env` 文件内容：

```bash
ALIYUN_ACCESS_KEY_ID=your_access_key_id_here
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret_here
ALIYUN_REGION=cn-hangzhou
```

### 3. 基本使用

```bash
# 查询今天的短信记录
python main.py -p 13800138000

# 查询指定日期
python main.py -p 13800138000 -s 20231103

# 查询时间段
python main.py -p 13800138000 -s 20231101 -e 20231103
```

## 使用指南

### 参数说明

| 参数 | 简写 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `--phone` | `-p` | ✅ | 要查询的手机号码 | 13800138000 |
| `--start-date` | `-s` | ❌ | 开始日期（格式：YYYYMMDD），默认为今天 | 20231101 |
| `--end-date` | `-e` | ❌ | 结束日期（格式：YYYYMMDD），默认为开始日期 | 20231103 |
| `--output` | `-o` | ❌ | 输出文件名（自动添加时间戳和 .csv 扩展名） | report |
| `--workers` | `-w` | ❌ | 并发查询线程数（1-20），默认为 10 | 15 |

### 使用示例

#### 查询今天的记录

```bash
python main.py -p 13800138000
# 输出：sms_details_20231103_143022.csv
```

#### 查询指定时间段并自定义文件名

```bash
python main.py -p 13800138000 -s 20231101 -e 20231103 -o report
# 输出：report_20231103_143022.csv
```

#### 使用高并发查询大时间跨度

```bash
# 查询全年数据，使用 15 个线程
python main.py -p 13800138000 -s 20240101 -e 20241231 -w 15
```

### 输出说明

#### 命令行输出

```
============================================================
阿里云短信查询导出工具
============================================================
手机号码: 13800138000
开始日期: 2023-11-01
结束日期: 2023-11-03
并发线程: 10
输出文件: sms_details_20231103_143022.csv
============================================================

正在查询手机号 13800138000 从 20231101 到 20231103 的短信记录...
共需查询 3 天的数据
使用 10 个并发线程加速查询...

[1/3] ✓ 20231101 找到 25 条记录
[2/3] ✓ 20231102 找到 30 条记录
[3/3] ✓ 20231103 找到 25 条记录

查询完成，共获取 80 条记录

统计信息:
  总记录数: 80
  发送成功: 75
  发送失败: 3
  等待回执: 2

成功导出 80 条记录到文件: sms_details_20231103_143022.csv
✓ 任务完成!
```

#### CSV 文件格式

导出的 CSV 文件包含以下列：

| 列名 | 说明 |
|------|------|
| 手机号 | 接收短信的手机号码 |
| 发送时间 | 短信发送的具体时间 |
| 发送状态 | 发送状态（发送成功/发送失败/等待回执） |
| 短信内容 | 短信的实际内容 |

- 使用 UTF-8-BOM 编码，Excel 可直接打开无乱码
- 文件名自动添加时间戳（格式：YYYYMMDD_HHMMSS）

## 打包部署

将程序打包成独立的可执行文件，无需 Python 环境即可使用。

### 🚀 快速打包（3 步）

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 运行打包脚本
python build.py

# 3. 完成！在 release/ 目录查看结果
```

### 三种打包方式

#### 方式 1：自动脚本（推荐 ⭐⭐⭐）

```bash
python build.py
```

**特点**：
- ✅ 自动检查和安装 PyInstaller
- ✅ 自动清理旧文件
- ✅ 自动创建发布包
- ✅ 包含使用说明
- ✅ 友好的进度提示

#### 方式 2：Make 命令（⭐⭐）

```bash
# 查看所有命令
make help

# 首次使用：安装依赖
make install

# 打包
make build

# 清理并重新打包
make release

# 清理构建文件
make clean
```

#### 方式 3：手动打包（⭐）

```bash
# 安装 PyInstaller
pip install pyinstaller

# 执行打包
pyinstaller \
  --name=query-sms \
  --onefile \
  --console \
  --clean \
  --noconfirm \
  --hidden-import=alibabacloud_dysmsapi20170525 \
  --hidden-import=dotenv \
  --hidden-import=click \
  main.py

# 手动创建发布目录
mkdir -p release
cp dist/query-sms release/
cp env.example release/
chmod +x release/query-sms
```

### 打包后的文件结构

```
release/
├── query-sms           # ⭐ 可执行文件（约 40-50MB）
├── env.example         # 配置文件示例
└── 使用说明.txt        # 快速使用指南
```

### 使用打包后的程序

#### 1. 配置环境

```bash
cd release

# 创建配置文件
cp env.example .env

# 编辑配置（使用你喜欢的编辑器）
nano .env
# 或
vi .env
```

填入阿里云凭证：

```bash
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_REGION=cn-hangzhou
```

#### 2. 运行程序

```bash
# 查询今天的记录
./query-sms -p 13800138000

# 查询指定日期
./query-sms -p 13800138000 -s 20231103

# 查询时间段
./query-sms -p 13800138000 -s 20231101 -e 20231103

# 查看帮助
./query-sms --help
```

#### 3. 添加到系统路径（可选）

如果希望在任何目录下都能使用：

```bash
# 复制到系统路径
sudo cp query-sms /usr/local/bin/

# 验证
query-sms --help

# 使用
query-sms -p 13800138000 -s 20231103
```

> ⚠️ **注意**：`.env` 配置文件需要在执行命令的当前目录下。

### 分发给他人

#### 创建压缩包

```bash
cd release

# 方式 1：创建 tar.gz 压缩包
tar -czf query-sms-macos-$(date +%Y%m%d).tar.gz *

# 方式 2：创建 zip 压缩包
zip -r query-sms-macos-$(date +%Y%m%d).zip *
```

#### 使用方法（接收者）

```bash
# 解压（tar.gz）
tar -xzf query-sms-macos-*.tar.gz

# 或解压（zip）
unzip query-sms-macos-*.zip

# 配置
cp env.example .env
nano .env  # 填入阿里云凭证

# 使用
./query-sms -p 手机号 -s 日期
```

### Make 命令参考

```bash
make help      # 查看所有可用命令
make install   # 安装依赖
make build     # 打包可执行文件
make clean     # 清理构建文件
make release   # 清理并重新打包
```

### 打包常见问题

#### 1. macOS 安全提示

**问题**：提示"无法验证开发者"

**解决方法 1**：

```bash
xattr -cr query-sms
```

**解决方法 2**：
1. 系统偏好设置 > 安全性与隐私
2. 点击"仍要打开"

#### 2. 没有执行权限

**问题**：提示权限被拒绝

**解决**：

```bash
chmod +x query-sms
```

#### 3. 打包失败

**问题**：打包过程中出错

**检查清单**：
- [ ] 是否已激活虚拟环境
- [ ] 是否安装了所有依赖：`pip install -r requirements.txt`
- [ ] PyInstaller 是否安装：`pip install pyinstaller`
- [ ] Python 版本是否 3.7+

**重试**：

```bash
# 清理后重试
make clean
make build
```

#### 4. 可执行文件太大

**正常现象**：打包后约 40-50MB，因为包含了：
- Python 解释器
- 所有依赖库
- 必要的系统库

**优化方法**（可选）：

```bash
# 安装 UPX 压缩工具
brew install upx

# 修改 build.py，在 pyinstaller 命令中添加：
--upx-dir=/usr/local/bin
```

#### 5. 找不到 .env 文件

**问题**：运行时提示配置错误

**解决**：确保 `.env` 文件在：
- 可执行文件所在目录，或
- 执行命令的当前目录

**验证**：

```bash
ls -la .env
cat .env
```

### 跨平台打包

#### macOS

```bash
python build.py
```

生成的文件可以在 macOS 10.13+ 上运行。

#### Linux

```bash
python3 build.py
```

生成的文件可以在相同或更高版本的 Linux 发行版上运行。

#### Windows

```bash
python build.py
```

生成的 `.exe` 文件可以在 Windows 7+ 上运行。

> 📝 **注意**：PyInstaller 打包是平台特定的，在哪个平台上打包就生成哪个平台的可执行文件。如果需要跨平台分发，需要在各个平台上分别打包。

## 常见问题

### 1. 配置错误

**问题**：提示 "未找到 ALIYUN_ACCESS_KEY_ID 配置"

**解决**：确保已创建 `.env` 文件并填入正确的配置信息。

### 2. 查询不到记录

**原因可能有**：
- 该手机号在指定时间段内确实没有发送记录
- 日期格式不正确（应为 YYYYMMDD）
- AccessKey 权限不足

**解决**：
- 检查日期范围是否正确
- 确认 AccessKey 具有短信服务的查询权限

### 3. API 调用失败

**原因可能有**：
- AccessKey 配置错误
- 网络连接问题
- 阿里云服务异常

**解决**：
- 检查 `.env` 文件中的配置
- 确认网络连接正常
- 查看错误信息中的具体提示

### 4. 日期格式问题

**正确格式**：YYYYMMDD（8 位数字）

示例：
- ✅ 正确：20231103
- ❌ 错误：2023-11-03
- ❌ 错误：2023/11/03
- ❌ 错误：23-11-03

## 注意事项

1. **API 限制**：阿里云短信 API 单次最多返回 50 条记录，本工具会自动分页查询所有记录。

2. **日期范围**：
   - 阿里云 API 每次只能查询单天数据，本工具会自动遍历日期范围
   - 支持并行查询，可大幅提升大时间跨度的查询速度
   - 使用默认 10 线程：查询 1 年数据约需要 1-2 分钟
   - 使用 15-20 线程：查询速度可提升 50% 以上

3. **并发控制**：
   - 默认并发数为 10，适合大多数场景
   - 如果遇到 API 限流错误，可降低并发数（如 `-w 5`）
   - 查询大时间跨度时，可提高并发数（如 `-w 15` 或 `-w 20`）

4. **权限要求**：使用的 AccessKey 需要具有短信服务的查询权限（`QuerySendDetails`）。

5. **数据安全**：
   - `.env` 文件已在 `.gitignore` 中，不会被提交到代码仓库
   - 导出的 CSV 文件也已被忽略，注意不要将其提交到公开仓库
   - 不要分享包含敏感信息的 `.env` 文件

6. **性能优化**：
   - 使用多线程并行查询，大幅提升查询速度
   - 查询结果自动按时间排序
   - 实时显示查询进度

## 技术栈

- Python 3.7+
- 阿里云短信 SDK (alibabacloud-dysmsapi20170525)
- Click (命令行框架)
- python-dotenv (环境变量管理)

## 项目结构

```
query_sms/
├── main.py              # CLI 入口程序
├── config.py            # 配置管理
├── sms_query.py         # 短信查询逻辑
├── csv_export.py        # CSV 导出功能
├── requirements.txt     # Python 依赖
├── env.example          # 环境变量示例
├── .gitignore          # Git 忽略文件
├── build.py            # 自动化打包脚本
├── Makefile            # Make 命令配置
└── README.md           # 本文档
```

## 许可证

本项目仅供学习和个人使用。

## 支持

如有问题或建议，请联系开发者。
