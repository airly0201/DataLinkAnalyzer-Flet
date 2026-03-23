"""
关联配置页面 - Flet 移动端优化版
"""

import flet as ft
from typing import List, Dict, Any, Callable, Optional

from core.excel_reader import create_reader
from core.linker import TableConfig


class LinkerPage:
    """多表关联配置页面"""
    
    def __init__(self, 
                 files: List[Dict[str, Any]], 
                 on_links_configured: Callable):
        self.files = files
        self.on_links_configured = on_links_configured
        
        # 表数据 {file_path: {filename, sheets, headers, fields}}
        self.tables: Dict[str, Dict[str, Any]] = {}
        
        # 关联配置
        self.links: List[Dict[str, Any]] = []
        
        # 主表选择
        self.main_table_dropdown = ft.Dropdown(
            label="主表",
            hint_text="选择主表",
            options=[],
            on_change=self.on_main_table_changed,
            expand=True
        )
        
        # 关联表选择
        self.link_table_dropdown = ft.Dropdown(
            label="关联表",
            hint_text="选择要关联的表",
            options=[],
            on_change=self.on_link_table_changed,
            expand=True
        )
        
        # 关联字段选择
        self.main_field_dropdown = ft.Dropdown(
            label="主表字段",
            hint_text="选择关联字段",
            options=[],
            expand=True
        )
        
        self.link_field_dropdown = ft.Dropdown(
            label="关联表字段",
            hint_text="选择关联字段",
            options=[],
            expand=True
        )
        
        # 连接类型
        self.join_type_dropdown = ft.Dropdown(
            label="连接方式",
            options=[
                ft.dropdown.Option("inner", "内连接 (inner)"),
                ft.dropdown.Option("left", "左连接 (left)"),
                ft.dropdown.Option("outer", "全连接 (outer)"),
            ],
            value="inner",
            expand=True
        )
        
        # 添加关联按钮
        self.add_link_button = ft.ElevatedButton(
            "➕ 添加关联",
            icon=ft.icons.ADD,
            on_click=self.add_link
        )
        
        # 关联列表显示
        self.links_view = ft.ListView(
            expand=True,
            spacing=5,
            padding=10
        )
        
        self.status_text = ft.Text(
            "正在加载表信息...",
            size=14,
            color=ft.colors.BLUE
        )
        
        self.loading = ft.ProgressBar(visible=False)
    
    def get_container(self) -> ft.Container:
        """获取页面容器"""
        return ft.Container(
            content=ft.Column([
                # 标题
                ft.Container(
                    content=ft.Text(
                        "🔗 配置多表关联",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    padding=15
                ),
                
                # 状态
                self.status_text,
                self.loading,
                
                # 关联配置区域
                ft.Container(
                    content=ft.Column([
                        ft.Text("📌 关联配置", size=16, weight=ft.FontWeight.BOLD),
                        self.main_table_dropdown,
                        self.link_table_dropdown,
                        ft.Row([self.main_field_dropdown, self.link_field_dropdown]),
                        self.join_type_dropdown,
                        self.add_link_button
                    ], spacing=10),
                    border_radius=10,
                    bgcolor=ft.colors.WHITE,
                    padding=15
                ),
                
                # 已添加的关联
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 已配置的关联", size=16, weight=ft.FontWeight.BOLD),
                        self.links_view
                    ], spacing=5),
                    border_radius=10,
                    bgcolor=ft.colors.BLUE_50,
                    padding=10,
                    expand=True
                ),
                
                # 底部按钮
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            "← 上一步",
                            icon=ft.icons.ARROW_BACK,
                            on_click=self.go_back
                        ),
                        ft.ElevatedButton(
                            "下一步: 选择输出字段 →",
                            icon=ft.icons.ARROW_FORWARD,
                            on_click=self.confirm_links,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE,
                                color=ft.colors.WHITE
                            )
                        )
                    ], spacing=10),
                    padding=10
                )
            ]),
            bgcolor=ft.colors.GREY_100,
            expand=True
        )
    
    async def load_tables(self, page: ft.Page):
        """加载表信息"""
        self.loading.visible = True
        self.status_text.value = "🔄 加载表信息中..."
        
        for file_info in self.files:
            file_path = file_info['path']
            try:
                reader = create_reader(file_path)
                sheets = reader.get_sheets()
                headers = {}
                fields = {}
                
                for sheet in sheets:
                    sheet_name = sheet['name']
                    headers[sheet_name] = reader.get_headers(sheet_name)
                    fields[sheet_name] = reader.get_field_info(sheet_name)
                
                self.tables[file_path] = {
                    'filename': file_info['name'],
                    'sheets': sheets,
                    'headers': headers,
                    'fields': fields
                }
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        self.loading.visible = False
        self.status_text.value = f"✅ 已加载 {len(self.tables)} 个表的信息"
        
        # 更新下拉框
        self._update_dropdowns()
    
    def _update_dropdowns(self):
        """更新下拉框选项"""
        options = []
        for path, info in self.tables.items():
            options.append(ft.dropdown.Option(path, info['filename']))
        
        self.main_table_dropdown.options = options
        self.link_table_dropdown.options = options
    
    def on_main_table_changed(self, e):
        """主表变更"""
        file_path = e.control.value
        if not file_path or file_path not in self.tables:
            return
        
        table_info = self.tables[file_path]
        headers = table_info['headers']
        
        # 获取第一个sheet的表头
        first_sheet = list(headers.keys())[0] if headers else ""
        if first_sheet:
            field_options = [
                ft.dropdown.Option(h, h) 
                for h in headers[first_sheet]
            ]
            self.main_field_dropdown.options = field_options
    
    def on_link_table_changed(self, e):
        """关联表变更"""
        file_path = e.control.value
        if not file_path or file_path not in self.tables:
            return
        
        table_info = self.tables[file_path]
        headers = table_info['headers']
        
        first_sheet = list(headers.keys())[0] if headers else ""
        if first_sheet:
            field_options = [
                ft.dropdown.Option(h, h) 
                for h in headers[first_sheet]
            ]
            self.link_field_dropdown.options = field_options
    
    def add_link(self, e):
        """添加关联"""
        main_table = self.main_table_dropdown.value
        link_table = self.link_table_dropdown.value
        main_field = self.main_field_dropdown.value
        link_field = self.link_field_dropdown.value
        join_type = self.join_type_dropdown.value
        
        if not all([main_table, link_table, main_field, link_field]):
            self.status_text.value = "⚠️ 请完整填写关联配置"
            self.status_text.color = ft.colors.ORANGE
            return
        
        if main_table == link_table:
            self.status_text.value = "⚠️ 不能关联同一个表"
            self.status_text.color = ft.colors.ORANGE
            return
        
        main_name = self.tables[main_table]['filename']
        link_name = self.tables[link_table]['filename']
        
        link_info = {
            'left_table': main_table,
            'right_table': link_table,
            'left_field': main_field,
            'right_field': link_field,
            'join_type': join_type,
            'left_name': main_name,
            'right_name': link_name
        }
        
        self.links.append(link_info)
        self._update_links_view()
        
        self.status_text.value = f"✅ 已添加关联: {main_name}.{main_field} = {link_name}.{link_field}"
        self.status_text.color = ft.colors.GREEN
        
        # 重置关联表选择
        self.link_table_dropdown.value = None
        self.link_field_dropdown.options = []
    
    def _update_links_view(self):
        """更新关联列表显示"""
        self.links_view.controls.clear()
        
        if not self.links:
            self.links_view.controls.append(
                ft.Text("未配置关联（可执行单表查询）", color=ft.colors.GREY_500)
            )
            return
        
        for i, link in enumerate(self.links):
            card = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(
                            f"{link['left_name']}.{link['left_field']} = {link['right_name']}.{link['right_field']}",
                            size=14,
                            weight=ft.FontWeight.W_500
                        ),
                        ft.Text(
                            f"连接方式: {link['join_type']}",
                            size=12,
                            color=ft.colors.GREY_600
                        )
                    ], spacing=2, expand=True),
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        on_click=lambda e, idx=i: self.remove_link(idx)
                    )
                ]),
                bgcolor=ft.colors.WHITE,
                border_radius=8,
                padding=10
            )
            self.links_view.controls.append(card)
    
    def remove_link(self, index: int):
        """移除关联"""
        if 0 <= index < len(self.links):
            self.links.pop(index)
            self._update_links_view()
            self.status_text.value = f"已移除关联 #{index + 1}"
            self.status_text.color =ft.colors.GREY_600
    
    def go_back(self, e):
        """返回上一步"""
        # 这里通过回调通知主程序返回
        pass
    
    def confirm_links(self, e):
        """确认关联配置"""
        # 返回表信息和关联配置
        self.on_links_configured({
            'tables': self.tables,
            'links': self.links
        })