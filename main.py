"""
数据关联分析平台 - Flet 原生 Android App
主入口文件
"""

import flet as ft
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pages.file_selector import FileSelectorPage
from pages.linker import LinkerPage
from pages.output_fields import OutputFieldsPage
from pages.result import ResultPage


class DataLinkAnalyzerApp:
    """数据关联分析平台 App"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "🔗 数据关联分析平台"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        
        # 应用主题
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.colors.BLUE,
            use_material3=True
        )
        
        # 状态数据
        self.files = []              # 选中的文件列表
        self.tables = {}             # 表信息
        self.links = []              # 关联配置
        self.output_fields = {}      # 输出字段
        
        # 页面索引 (0: 文件选择, 1: 关联配置, 2: 输出字段, 3: 结果)
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
        """构建导航点"""
        is_active = index == self.current_page
        return ft.Container(
            width=12,
            height=12,
            border_radius=6,
            bgcolor=ft.colors.BLUE if is_active else ft.colors.GREY_300
        )
    
    def _build_ui(self):
        """构建UI"""
        # 初始显示文件选择页
        self._show_file_selector()
        
        # 页面内容
        content = ft.Column([
            # 顶部标题
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "🔗 数据关联分析平台",
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
            
            # 导航指示
            ft.Container(
                content=self.nav_indicator,
                padding=10
            ),
            
            # 页面内容
            self.page_container,
            
            # 底部提示
            ft.Container(
                content=ft.Text(
                    "步骤: 选文件 → 配关联 → 选字段 → 查结果",
                    size=12,
                    color=ft.colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=10
            )
        ], spacing=0)
        
        self.page.add(content)
    
    def _show_file_selector(self):
        """显示文件选择页"""
        def on_files_selected(files):
            self.files = files
            self._go_to_page(1)
        
        page = FileSelectorPage(on_files_selected)
        
        # 设置默认路径
        default_paths = [
            os.path.expanduser("~/Download"),
            "/storage/emulated/0/Download",
            "/sdcard/Download"
        ]
        for path in default_paths:
            if os.path.exists(path):
                page.set_folder_path(path)
                break
        
        self.page_container.content = page.get_container()
        self._update_nav_indicator(0)
        self.page.update()
    
    async def _on_files_loaded(self, files):
        """文件选择完成回调"""
        self.files = files
        await self._show_linker_page()
    
    async def _show_linker_page(self):
        """显示关联配置页"""
        self._go_to_page(1)
        
        # 显示加载中
        self.page_container.content = ft.Container(
            content=ft.Column([
                ft.Text("正在加载表信息...", size=16),
                ft.ProgressBar()
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
        self.page.update()
        
        # 创建关联页
        def on_links_configured(data):
            self.tables = data['tables']
            self.links = data['links']
            self._show_output_fields_page()
        
        linker_page = LinkerPage(self.files, on_links_configured)
        self.page_container.content = linker_page.get_container()
        
        # 加载表信息
        await linker_page.load_tables(self.page)
        
        self._update_nav_indicator(1)
        self.page.update()
    
    def _show_output_fields_page(self):
        """显示输出字段选择页"""
        self._go_to_page(2)
        
        def on_fields_selected(data):
            self.output_fields = data['output_fields']
            self._show_result_page()
        
        page = OutputFieldsPage(self.tables, self.links, on_fields_selected)
        page.initialize()
        
        self.page_container.content = page.get_container()
        self._update_nav_indicator(2)
        self.page.update()
    
    async def _show_result_page(self):
        """显示结果页"""
        self._go_to_page(3)
        
        # 显示加载中
        self.page_container.content = ft.Container(
            content=ft.Column([
                ft.Text("正在执行查询...", size=16),
                ft.ProgressBar()
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
        self.page.update()
        
        def on_restart():
            self._reset_and_go_home()
        
        result_page = ResultPage(self.tables, self.links, self.output_fields, on_restart)
        self.page_container.content = result_page.get_container()
        
        # 执行查询
        await result_page.execute_query(self.page)
        
        self._update_nav_indicator(3)
        self.page.update()
    
    def _go_to_page(self, index: int):
        """跳转到指定页面"""
        self.current_page = index
        self._update_nav_indicator(index)
    
    def _update_nav_indicator(self, active_index: int):
        """更新导航指示器"""
        for i, container in enumerate(self.nav_indicator.controls):
            container.bgcolor = ft.colors.BLUE if i == active_index else ft.colors.GREY_300
    
    def _reset_and_go_home(self):
        """重置并返回首页"""
        self.files = []
        self.tables = {}
        self.links = []
        self.output_fields = {}
        self.current_page = 0
        self._show_file_selector()


def main(page: ft.Page):
    """Flet 应用入口"""
    app = DataLinkAnalyzerApp(page)


if __name__ == "__main__":
    # 启动 Flet 应用
    # 在 Android 上使用 ft.app()
    # 在桌面调试时可以使用 ft.app(target=main, view=ft.WEB_BROWSER)
    ft.app(target=main)