"""数据关联分析平台 - Flet Android App
使用ft.run()替代ft.app()
"""
import flet as ft
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main(page: ft.Page):
    """Flet 应用入口"""
    # 页面配置
    page.title = "数据关联分析平台"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # 主题
    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.BLUE,
        use_material3=True
    )
    
    # 欢迎文字
    welcome = ft.Column([
        ft.Text(
            "数据关联分析平台",
            size=28,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        ),
        ft.Text(
            "选择Excel文件进行关联分析",
            size=14,
            color=ft.colors.GREY_600,
            text_align=ft.TextAlign.CENTER
        ),
    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    # 状态显示
    status = ft.Text(
        "准备就绪",
        size=14,
        color=ft.colors.GREY_600
    )
    
    # 构建界面
    page.add(
        ft.Container(
            content=welcome,
            padding=30,
            bgcolor=ft.colors.BLUE,
            alignment=ft.alignment.center,
            height=200
        ),
        ft.Container(
            content=status,
            padding=20
        )
    )
    
    # 重要：显式更新页面
    page.update()


if __name__ == "__main__":
    # 使用ft.run()，这是0.80+版本的推荐方式
    ft.run(target=main)