#!/bin/bash
# 启动 Flet 应用的脚本

cd "$(dirname "$0")"

# 检查依赖
python3 -c "import flet" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip install flet pandas openpyxl
fi

# 启动应用（使用 Web 模式便于测试）
echo "启动数据关联分析平台..."
python3 -c "
import flet as ft
from main import main
ft.app(target=main, view=ft.WEB_BROWSER, port=8550)
"