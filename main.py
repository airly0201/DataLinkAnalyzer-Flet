"""数据关联分析平台 - Flet Android App 完整版
整合文件选择 → 关联配置 → 字段选择 → 结果展示
"""

import flet as ft
import os
import sys
import asyncio
from typing import Dict, Any, List, Optional

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.excel_reader import create_reader
from core.linker import create_linker, TableConfig
from pages.file_selector import FileSelectorPage
from pages.linker import LinkerPage
from pages.output_fields import OutputFieldsPage
from pages.result import ResultPage


class DataLinkApp:
    """数据关联分析主应用"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page_config()
        
        # 应用状态
        self.state = {
            'files': [],           # 选中的文件列表
            'tables': {},          # 表信息
            'links': [],           # 关联配置
            'output_fields': {},   # 输出字段
        }
        
        # 当前页面
        self.current_page = None
        self.file_selector = None
        self.linker_page = None
        self.output_fields_page = None
        self.result_page = None
        
        # 启动首页
        self.show_file_selector()
    
    def page_config(self):
        """页面配置"""
        self.page.title = "数据关联分析平台"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window_full_screen = False
        self.page.window_width = 400
        self.page.window_height = 700
        
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.colors.BLUE,
            use_material3=True
        )
    
    def clear_page(self):
        """清空页面"""
        self.page.controls.clear()
    
    def show_file_selector(self):
        """显示文件选择页面"""
        self.clear_page()
        
        def on_files_selected(files):
            self.state['files'] = files
            self.show_linker_page()
        
        self.file_selector = FileSelectorPage(on_files_selected)
        
        # 设置默认路径
        default_path = os.path.expanduser("~/storage/documents/input")
        if os.path.exists(default_path):
            self.file_selector.set_folder_path(default_path)
        
        self.current_page = self.file_selector.get_container()
        self.page.add(self.current_page)
        self.page.update()
    
    def show_linker_page(self):
        """显示关联配置页面"""
        self.clear_page()
        
        def on_links_configured(data):
            self.state['tables'] = data['tables']
            self.state['links'] = data['links']
            self.show_output_fields_page()
        
        self.linker_page = LinkerPage(
            self.state['files'],
            on_links_configured
        )
        
        # 添加返回回调
        self.linker_page.on_go_back = self.show_file_selector
        
        self.current_page = self.linker_page.get_container()
        self.page.add(self.current_page)
        self.page.update()
        
        # 异步加载表信息
        asyncio.create_task(self.linker_page.load_tables(self.page))
    
    def show_output_fields_page(self):
        """显示字段选择页面"""
        self.clear_page()
        
        def on_fields_selected(data):
            self.state['output_fields'] = data['output_fields']
            self.show_result_page()
        
        self.output_fields_page = OutputFieldsPage(
            self.state['tables'],
            self.state['links'],
            on_fields_selected
        )
        
        # 添加返回回调
        self.output_fields_page.on_go_back = self.show_linker_page
        
        self.output_fields_page.initialize()
        
        self.current_page = self.output_fields_page.get_container()
        self.page.add(self.current_page)
        self.page.update()
    
    def show_result_page(self):
        """显示结果页面"""
        self.clear_page()
        
        def on_restart():
            self.state = {
                'files': [],
                'tables': {},
                'links': [],
                'output_fields': {},
            }
            self.show_file_selector()
        
        self.result_page = ResultPage(
            self.state['tables'],
            self.state['links'],
            self.state['output_fields'],
            on_restart
        )
        
        self.current_page = self.result_page.get_container()
        self.page.add(self.current_page)
        self.page.update()
        
        # 异步执行查询
        asyncio.create_task(self.result_page.execute_query(self.page))


def main(page: ft.Page):
    """Flet 应用入口"""
    app = DataLinkApp(page)


if __name__ == "__main__":
    # 使用ft.run()，这是0.80+版本的推荐方式
    ft.run(target=main)