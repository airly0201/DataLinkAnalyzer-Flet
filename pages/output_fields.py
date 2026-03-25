"""
输出字段选择页面 - Flet 移动端优化版
"""

import flet as ft
from typing import List, Dict, Any, Callable, Optional

from core.excel_reader import create_reader


class OutputFieldsPage:
    """输出字段选择页面"""
    
    def __init__(self, 
                 tables: Dict[str, Dict[str, Any]], 
                 links: List[Dict[str, Any]],
                 on_fields_selected: Callable):
        self.tables = tables
        self.links = links
        self.on_fields_selected = on_fields_selected
        
        # 已选输出字段 {file_path: [fields]}
        self.output_fields: Dict[str, List[str]] = {}
        
        # 表选择下拉框
        self.table_dropdown = ft.Dropdown(
            label="选择表",
            hint_text="选择要选择字段的表",
            options=[],
            on_change=self.on_table_changed,
            expand=True
        )
        
        # Sheet选择下拉框
        self.sheet_dropdown = ft.Dropdown(
            label="选择Sheet",
            hint_text="选择Sheet",
            options=[],
            on_change=self.on_sheet_changed,
            expand=True
        )
        
        # 字段复选框区域
        self.fields_view = ft.ListView(
            expand=True,
            spacing=5,
            padding=10
        )
        
        # 已选字段标签显示
        self.selected_tags_view = ft.Column(spacing=5)
        
        self.status_text = ft.Text(
            "请选择要输出哪些字段",
            size=14,
            color=ft.colors.GREY_600
        )
    
    def get_container(self) -> ft.Container:
        """获取页面容器"""
        return ft.Container(
            content=ft.Column([
                # 标题
                ft.Container(
                    content=ft.Text(
                        "📤 选择输出字段",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    padding=15
                ),
                
                # 状态
                self.status_text,
                
                # 表和Sheet选择
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 选择表和Sheet", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([self.table_dropdown, self.sheet_dropdown], spacing=10)
                    ], spacing=10),
                    border_radius=10,
                    bgcolor=ft.colors.WHITE,
                    padding=15
                ),
                
                # 字段选择
                ft.Container(
                    content=ft.Column([
                        ft.Text("☑️ 字段列表", size=16, weight=ft.FontWeight.BOLD),
                        self.fields_view
                    ], spacing=5),
                    border_radius=10,
                    bgcolor=ft.colors.WHITE,
                    padding=10,
                    expand=True
                ),
                
                # 添加字段按钮
                ft.Container(
                    content=ft.ElevatedButton(
                        "➕ 添加选中字段",
                        icon=ft.icons.ADD,
                        on_click=self.add_selected_fields,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.GREEN,
                            color=ft.colors.WHITE
                        ),
                        expand=True
                    ),
                    padding=10
                ),
                
                # 已选字段显示
                ft.Container(
                    content=ft.Column([
                        ft.Text("✅ 已选字段", size=16, weight=ft.FontWeight.BOLD),
                        self.selected_tags_view
                    ], spacing=5),
                    border_radius=10,
                    bgcolor=ft.colors.BLUE_50,
                    padding=10
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
                            "执行查询 →",
                            icon=ft.icons.PLAY_ARROW,
                            on_click=self.execute_query,
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
    
    def initialize(self):
        """初始化页面"""
        # 初始化表下拉框
        options = []
        for path, info in self.tables.items():
            options.append(ft.dropdown.Option(path, info['filename']))
        
        self.table_dropdown.options = options
        
        # 如果只有一个表，自动选中
        if len(self.tables) == 1:
            first_path = list(self.tables.keys())[0]
            self.table_dropdown.value = first_path
            self._update_sheet_dropdown(first_path)
    
    def on_table_changed(self, e):
        """表变更"""
        file_path = e.control.value
        if file_path:
            self._update_sheet_dropdown(file_path)
    
    def _update_sheet_dropdown(self, file_path: str):
        """更新Sheet下拉框"""
        if file_path not in self.tables:
            return
        
        table_info = self.tables[file_path]
        sheets = table_info['sheets']
        
        options = [
            ft.dropdown.Option(s['name'], s['name']) 
            for s in sheets
        ]
        self.sheet_dropdown.options = options
        
        # 自动选中第一个
        if options:
            self.sheet_dropdown.value = options[0].key
            self._update_fields_view(file_path, options[0].key)
    
    def on_sheet_changed(self, e):
        """Sheet变更"""
        file_path = self.table_dropdown.value
        sheet_name = e.control.value
        
        if file_path and sheet_name:
            self._update_fields_view(file_path, sheet_name)
    
    def _update_fields_view(self, file_path: str, sheet_name: str):
        """更新字段列表"""
        self.fields_view.controls.clear()
        
        if file_path not in self.tables:
            return
        
        table_info = self.tables[file_path]
        fields = table_info['fields'].get(sheet_name, [])
        
        if not fields:
            self.fields_view.controls.append(
                ft.Text("没有字段信息", color=ft.colors.GREY_500)
            )
            return
        
        # 已选的字段
        selected = self.output_fields.get(file_path, [])
        
        for field in fields:
            field_name = field['name']
            is_checked = field_name in selected
            
            row = ft.Container(
                content=ft.Checkbox(
                    label=f"{field['name']} ({field['type']})",
                    value=is_checked,
                    data=field_name
                ),
                bgcolor=ft.colors.WHITE if is_checked else ft.colors.GREY_50,
                border_radius=5,
                padding=5
            )
            self.fields_view.controls.append(row)
    
    def add_selected_fields(self, e):
        """添加选中的字段"""
        file_path = self.table_dropdown.value
        sheet_name = self.sheet_dropdown.value
        
        if not file_path or not sheet_name:
            self.status_text.value = "⚠️ 请先选择表和Sheet"
            self.status_text.color = ft.colors.ORANGE
            return
        
        # 获取选中的复选框
        selected_fields = []
        for control in self.fields_view.controls:
            if isinstance(control, ft.Container):
                checkbox = control.content
                if isinstance(checkbox, ft.Checkbox) and checkbox.value:
                    selected_fields.append(checkbox.data)
        
        if not selected_fields:
            self.status_text.value = "⚠️ 请至少选择一个字段"
            self.status_text.color = ft.colors.ORANGE
            return
        
        # 添加到已选
        if file_path not in self.output_fields:
            self.output_fields[file_path] = []
        
        for field in selected_fields:
            if field not in self.output_fields[file_path]:
                self.output_fields[file_path].append(field)
        
        self._update_selected_tags()
        
        self.status_text.value = f"✅ 已添加 {len(selected_fields)} 个字段"
        self.status_text.color = ft.colors.GREEN
        
        # 清除复选框选中状态
        self._update_fields_view(file_path, sheet_name)
    
    def _update_selected_tags(self):
        """更新已选字段标签"""
        self.selected_tags_view.controls.clear()
        
        if not self.output_fields:
            self.selected_tags_view.controls.append(
                ft.Text("未选择任何字段", color=ft.colors.GREY_500)
            )
            return
        
        for path, fields in self.output_fields.items():
            table_name = self.tables[path]['filename']
            
            # 为每个字段创建Chip
            chips = []
            for field in fields:
                chips.append(
                    ft.Chip(
                        label=ft.Text(f"{field}"),
                        on_delete=lambda e, fp=path, fn=field: self.remove_field(fp, fn)
                    )
                )
            
            # 表名标签
            self.selected_tags_view.controls.append(
                ft.Text(f"📁 {table_name}", size=14, weight=ft.FontWeight.W_500)
            )
            
            # 字段Chip行
            self.selected_tags_view.controls.append(
                ft.Wrap(chips, spacing=5)
            )
    
    def remove_field(self, file_path: str, field_name: str):
        """移除字段"""
        if file_path in self.output_fields:
            if field_name in self.output_fields[file_path]:
                self.output_fields[file_path].remove(field_name)
                if not self.output_fields[file_path]:
                    del self.output_fields[file_path]
        
        self._update_selected_tags()
        self.status_text.value = f"已移除字段: {field_name}"
        self.status_text.color = ft.colors.GREY_600
    
    def go_back(self, e):
        """返回上一步 - 通过回调通知主程序"""
        if hasattr(self, 'on_go_back') and callable(self.on_go_back):
            self.on_go_back()
    
    def execute_query(self, e):
        """执行查询"""
        if not self.output_fields:
            self.status_text.value = "⚠️ 请至少选择一个输出字段"
            self.status_text.color = ft.colors.ORANGE
            return
        
        self.on_fields_selected({
            'tables': self.tables,
            'links': self.links,
            'output_fields': self.output_fields
        })