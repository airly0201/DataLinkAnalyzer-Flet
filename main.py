"""
数据关联分析平台 - Flet 原生 Android App
主入口文件
"""

import flet as ft
import os
import sys
import traceback

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 全局错误处理
def handle_error(e):
    """错误处理"""
    print(f"Error: {e}")
    traceback.print_exc()

try:
    from pages.file_selector import FileSelectorPage
    from pages.linker import LinkerPage
    from pages.output_fields import OutputFieldsPage
    from pages.result import ResultPage
except Exception as e:
    handle_error(e)


class DataLinkAnalyzerApp:
    """数据关联分析平台 App"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "数据关联分析平台"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        
        # 应用主题
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.colors.BLUE,
            use_material3=True
        )
        
        # 状态数据
        self.files = []
        self.tables = {}
        self.links = []
        self.output_fields = {}
        self.current_page = 0
        
        # 页面容器
        self.page_container = ft.Container(expand=True)
        
        # 导航指示器
        self.nav_indicator = ft.Row([
            self._build_nav_dot(0),
            self._build_nav_dot(1),
            self._build_nav_dot(2),
            self._build_nav_dot(3)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        
        # 构建UI
        self._build_ui()
    
    def _build_nav_dot(self, index: int) -> ft.Container:
        is_active = index == self.current_page
        return ft.Container(
            width=12,
            height=12,
            border_radius=6,
            bgcolor=ft.colors.BLUE if is_active else ft.colors.GREY_300
        )
    
    def _build_ui(self):
        self._show_file_selector()
        
        content = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "数据关联分析平台",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "支持多表关联、灵活查询",
                        size=14,
                        color=ft.colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    )
                ], spacing=5),
                padding=20,
                bgcolor=ft.colors.BLUE,
                alignment=ft.alignment.center
            ),
            ft.Container(
                content=self.nav_indicator,
                padding=10
            ),
            self.page_container,
            ft.Container(
                content=ft.Text(
                    "步骤: 选文件 -> 配关联 -> 选字段 -> 查结果",
                    size=12,
                    color=ft.colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=10
            )
        ], spacing=0)
        
        self.page.add(content)
    
    def _show_file_selector(self):
        def on_files_selected(files):
            self.files = files
            self._go_to_page(1)
        
        page = FileSelectorPage(on_files_selected)
        
        default_paths = [
            "/storage/emulated/0/Download",
            "/sdcard/Download",
            os.path.expanduser("~/Download")
        ]
        for path in default_paths:
            if os.path.exists(path):
                page.set_folder_path(path)
                break
        
        self.page_container.content = page.get_container()
        self._update_nav_indicator(0)
        self.page.update()
    
    def _go_to_page(self, index: int):
        self.current_page = index
        self._update_nav_indicator(index)
    
    def _update_nav_indicator(self, active_index: int):
        for i, container in enumerate(self.nav_indicator.controls):
            container.bgcolor = ft.colors.BLUE if i == active_index else ft.colors.GREY_300


def main(page: ft.Page):
    """Flet 应用入口"""
    try:
        app = DataLinkAnalyzerApp(page)
    except Exception as e:
        # 显示错误
        page.add(ft.Text(f"Error: {str(e)}", color=ft.colors.RED))
        print(f"Startup error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    ft.app(target=main)
