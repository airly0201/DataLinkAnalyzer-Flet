"""
数据关联分析平台 - Flet 原生 Android App
主入口文件 v2.0
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
    
    # 检查文件路径
    storage_path = "/storage/emulated/0/Download"
    if not os.path.exists(storage_path):
        storage_path = "/sdcard/Download"
    
    # 简单的测试 - 显示欢迎界面
    def on_scan_click(e):
        """扫描按钮点击"""
        folder = folder_input.value.strip() or storage_path
        if not os.path.exists(folder):
            status.value = f"路径不存在: {folder}"
            status.color = ft.colors.RED
            page.update()
            return
        
        # 扫描文件
        from utils.file_scanner import scan_folder
        files = scan_folder(folder)
        
        if not files:
            status.value = "未找到Excel文件"
            status.color = ft.colors.ORANGE
        else:
            status.value = f"找到 {len(files)} 个Excel文件"
            status.color = ft.colors.GREEN
            file_list.controls.clear()
            for f in files:
                file_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(f["name"]),
                        subtitle=ft.Text(f"{f['size_mb']:.2f} MB"),
                        leading=ft.Icon(ft.icons.TABLE_CHART),
                    )
                )
        
        page.update()
    
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
    
    # 文件夹输入
    folder_input = ft.TextField(
        label="文件夹路径",
        value=storage_path,
        hint_text="输入Excel文件目录",
        prefix_icon=ft.icons.FOLDER,
    )
    
    # 扫描按钮
    scan_btn = ft.ElevatedButton(
        "扫描文件",
        icon=ft.icons.SEARCH,
        on_click=on_scan_click,
        style=ft.ButtonStyle(bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)
    )
    
    # 状态显示
    status = ft.Text(
        "点击扫描按钮查找Excel文件",
        size=14,
        color=ft.colors.GREY_600
    )
    
    # 文件列表
    file_list = ft.ListView(
        expand=True,
        spacing=2,
        padding=10
    )
    
    # 构建界面
    page.add(
        ft.Container(
            content=welcome,
            padding=30,
            bgcolor=ft.colors.BLUE,
            alignment=ft.alignment.center
        ),
        ft.Container(
            content=ft.Column([
                folder_input,
                ft.Row([scan_btn], alignment=ft.MainAxisAlignment.CENTER),
                status,
            ], spacing=15),
            padding=20
        ),
        ft.Container(
            content=file_list,
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            padding=10,
            expand=True
        )
    )


if __name__ == "__main__":
    # 使用 run() 替代 app()
    ft.run(target=main)
