.PHONY: help build clean install test release

help:
	@echo "阿里云短信查询工具 - 构建命令"
	@echo ""
	@echo "可用命令："
	@echo "  make install    - 安装项目依赖"
	@echo "  make build      - 打包成可执行文件"
	@echo "  make clean      - 清理构建文件"
	@echo "  make test       - 运行测试（查看帮助信息）"
	@echo "  make release    - 创建完整的发布包"
	@echo ""

install:
	@echo "正在安装依赖..."
	pip install -r requirements.txt
	pip install pyinstaller
	@echo "✅ 依赖安装完成"

build:
	@echo "正在打包可执行文件..."
	python build.py
	@echo "✅ 打包完成，文件位于 release/ 目录"

clean:
	@echo "正在清理构建文件..."
	rm -rf build dist release *.spec __pycache__
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

test:
	@echo "运行程序帮助信息测试..."
	python main.py --help

release: clean build
	@echo "✅ 发布包已准备就绪！"
	@echo "📦 位置: ./release/"
	@echo ""
	@echo "发布包包含："
	@ls -lh release/
