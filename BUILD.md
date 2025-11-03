# 构建打包指南

本文档介绍如何将本项目打包成独立的可执行文件，方便在没有Python环境的系统上使用。

## 方案概述

本项目提供了基于 **PyInstaller** 的打包方案，可以将Python程序打包成单个独立的可执行文件。

### 优点

- ✅ 无需安装Python环境即可运行
- ✅ 单个文件，方便分发和使用
- ✅ 支持macOS、Linux、Windows（在对应平台上打包）
- ✅ 所有依赖都打包在内

## 快速开始

### 方法一：使用自动化打包脚本（推荐）

#### 1. 激活虚拟环境

```bash
cd /Users/bcxy/Workspace/query_sms
source venv/bin/activate
```

#### 2. 安装 PyInstaller（如果还没安装）

```bash
pip install pyinstaller
```

#### 3. 运行打包脚本

```bash
python build.py
```

脚本会自动完成以下操作：
- 检查并安装必要的依赖
- 清理旧的构建文件
- 使用 PyInstaller 打包可执行文件
- 创建包含使用说明的发布包

#### 4. 获取打包结果

打包完成后，在 `release/` 目录下会包含：

```
release/
├── query-sms          # 可执行文件
├── env.example        # 配置文件示例
└── 使用说明.txt       # 快速使用指南
```

### 方法二：手动打包

如果你想要更多控制，可以手动执行打包步骤：

#### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

#### 2. 执行打包命令

```bash
pyinstaller \
  --name=query-sms \
  --onefile \
  --console \
  --clean \
  --noconfirm \
  --hidden-import=alibabacloud_dysmsapi20170525 \
  --hidden-import=openpyxl \
  --hidden-import=dotenv \
  --hidden-import=click \
  main.py
```

#### 3. 查找可执行文件

打包完成后，可执行文件位于：`dist/query-sms`

## 打包参数说明

| 参数 | 说明 |
|------|------|
| `--name` | 指定可执行文件的名称 |
| `--onefile` | 打包成单个文件（而不是一个目录） |
| `--console` | 创建控制台应用（CLI工具） |
| `--clean` | 打包前清理临时文件 |
| `--noconfirm` | 不询问确认，直接覆盖 |
| `--hidden-import` | 显式包含某些模块（PyInstaller可能检测不到） |

## 使用打包后的程序

### 1. 配置环境

将 `release/` 目录复制到目标位置，然后创建配置文件：

```bash
cd release
cp env.example .env
```

编辑 `.env` 文件，填入阿里云凭证：

```bash
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_REGION=cn-hangzhou
```

### 2. 运行程序

```bash
./query-sms -p 13800138000 -s 20231103
```

### 3. 添加到系统路径（可选）

如果希望在任何目录下都能使用，可以将可执行文件复制到系统路径：

```bash
sudo cp query-sms /usr/local/bin/
```

然后就可以直接使用：

```bash
query-sms -p 13800138000 -s 20231103
```

> ⚠️ **注意**：`.env` 配置文件需要在执行命令的当前目录下，或者修改程序使其从固定位置读取配置。

## 文件大小优化

默认打包后的文件大小约为 30-50MB，这是正常的，因为包含了Python解释器和所有依赖库。

如果需要进一步优化大小，可以：

### 1. 使用 UPX 压缩

```bash
# macOS上安装 UPX
brew install upx

# 打包时使用UPX压缩
pyinstaller --name=query-sms --onefile --console --upx-dir=/usr/local/bin main.py
```

### 2. 排除不必要的模块

如果确定某些库没有使用，可以在打包时排除：

```bash
pyinstaller --name=query-sms --onefile --console \
  --exclude-module=matplotlib \
  --exclude-module=numpy \
  main.py
```

## 跨平台打包

### macOS

在macOS上打包会生成macOS可执行文件：

```bash
python build.py
```

生成的文件可以在macOS 10.13+上运行。

### Linux

在Linux上打包：

```bash
python3 build.py
```

生成的文件可以在相同或更高版本的Linux发行版上运行。

### Windows

在Windows上打包：

```bash
python build.py
```

生成的 `.exe` 文件可以在Windows 7+上运行。

> 📝 **注意**：PyInstaller打包是平台特定的，在哪个平台上打包就生成哪个平台的可执行文件。如果需要跨平台分发，需要在各个平台上分别打包。

## 创建 macOS .app 应用（可选）

如果想创建更加"原生"的macOS应用，可以使用 `py2app`：

### 1. 安装 py2app

```bash
pip install py2app
```

### 2. 创建 setup.py

```python
from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['alibabacloud_dysmsapi20170525', 'openpyxl', 'dotenv', 'click'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

### 3. 打包

```bash
python setup.py py2app
```

生成的应用位于 `dist/main.app`。

## 常见问题

### 1. 打包失败：找不到某个模块

**解决**：使用 `--hidden-import` 参数显式包含该模块：

```bash
pyinstaller --hidden-import=模块名 main.py
```

### 2. 运行时提示找不到 .env 文件

**解决**：确保 `.env` 文件在可执行文件的同一目录下，或者修改 `config.py` 使用绝对路径。

### 3. 可执行文件太大

**解决**：
- 使用 UPX 压缩
- 排除不必要的依赖
- 使用 `--onedir` 模式而不是 `--onefile`

### 4. macOS提示"无法打开，因为无法验证开发者"

**解决**：运行以下命令：

```bash
xattr -cr query-sms
```

或者在"系统偏好设置" > "安全性与隐私"中允许运行。

### 5. 打包后运行速度变慢

**解决**：这是正常现象，因为打包后的程序需要先解压临时文件。首次运行会慢一些，后续会快一些。

## 发布清单

在发布给其他用户之前，确保：

- [ ] 可执行文件已测试，能正常运行
- [ ] 包含 `env.example` 配置示例
- [ ] 包含使用说明文档
- [ ] 已移除测试数据和临时文件
- [ ] 文件权限正确（可执行文件需要执行权限）
- [ ] 如果有敏感信息，确保已清理

## 分发建议

### 本地使用

直接使用 `release/` 目录中的内容。

### 分享给他人

创建压缩包：

```bash
cd release
tar -czf query-sms-macos.tar.gz *
```

或者使用 zip：

```bash
zip -r query-sms-macos.zip *
```

### 版本管理

建议在打包时包含版本信息：

```bash
pyinstaller --name=query-sms-v1.0.0 main.py
```

## 更新和维护

当代码更新后，重新打包：

```bash
# 清理旧文件
rm -rf build dist release *.spec

# 重新打包
python build.py
```

## 性能对比

| 运行方式 | 启动时间 | 文件大小 | 依赖要求 |
|----------|----------|----------|----------|
| Python直接运行 | 快速 (~0.5s) | ~50KB源码 | 需要Python环境 |
| PyInstaller打包 | 较慢 (~2s) | ~40MB | 无需Python |
| py2app打包 | 中等 (~1s) | ~45MB | 无需Python |

## 技术支持

如有打包相关问题，请检查：

1. PyInstaller 版本是否最新：`pip install --upgrade pyinstaller`
2. Python 版本是否兼容（建议 3.7+）
3. 依赖包是否都已安装：`pip install -r requirements.txt`

---

更多信息请参考：
- [PyInstaller 官方文档](https://pyinstaller.readthedocs.io/)
- [py2app 官方文档](https://py2app.readthedocs.io/)

