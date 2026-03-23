"""
文件选择页面 - Flet 移动端优化版
"""

import flet as ft
import os
from typing import List, Dict, Any, Callable, Optional

from core.excel_reader import create_reader
from utils.file_scanner import scan_folder


class FileSelectorPage:
    """文件选择页面"""
    
    def __init__(self, on_files_selected: Callable):
        self.on_files_selected = on_files_selected
        self.files: List[Dict[str, Any]] = []
        self.selected_files: List[Dict[str, Any]] = []
        self.folder_path = ""
        
        # UI 组件
        self.folder_input = ft.TextField(
            label="文件夹路径",
            hint_text="输入Excel文件所在目录",
            expand=True,
            on_submit=self.scan_folder
        )
        
        self.scan_button = ft.ElevatedButton(
            "🔍 扫描",
            icon=ft.icons.SEARCH,
            on_click=lambda e: self.scan_folder(None)
        )
        
        self.file_list_view = ft.ListView(
            expand=True,
            spacing=5,
            padding=10
        )
        
        self.status_text = ft.Text(
            "请输入文件夹路径后点击扫描",
            size=14,
            color=ft.colors.GREY_600
        )
        
        self.loading = ft.ProgressBar(visible=False)
    
    def get_container(self) -> ft.Container:
        """获取页面容器"""
        return ft.Container(
            content=ft.Column([
                # 路径输入区
                ft.Container(
                    content=ft.Row([
                        self.folder_input,
                        self.scan_button
                    ]),
                    padding=10
                ),
                
                # 状态显示
                self.status_text,
                self.loading,
                
                # 文件列表
                ft.Container(
                    content=ft.Column([
                        ft.Text("📁 文件列表", size=16, weight=ft.FontWeight.BOLD),
                        self.file_list_view
                    ]),
                    border_radius=10,
                    bgcolor=ft.colors.WHITE,
                    padding=10,
                    expand=True
                ),
                
                # 已选文件显示
                ft.Container(
                    content=ft.Column([
                        ft.Text("✅ 已选文件", size=16, weight=ft.FontWeight.BOLD),
                        self._build_selected_view()
                    ]),
                    border_radius=10,
                    bgcolor=ft.colors.BLUE_50,
                    padding=10
                ),
                
                # 确认按钮
                ft.Container(
                    content=ft.ElevatedButton(
                        "下一步: 配置关联 →",
                        icon=ft.icons.ARROW_FORWARD,
                        on_click=self.confirm_selection,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE,
                            color=ft.colors.WHITE,
                            padding=20
                        ),
                        expand=True
                    ),
                    padding=10
                )
            ]),
            bgcolor=ft.colors.GREY_100,
            expand=True
        )
    
    def _build_selected_view(self) -> ft.Column:
        """构建已选文件视图"""
        if not self.selected_files:
            return ft.Column([
                ft.Text("尚未选择文件", size=14, color=ft.colors.GREY_500)
            ])
        
        chips = []
        for f in self.selected_files:
            chips.append(
                ft.Chip(
                    label=ft.Text(f"{f['name']} ({f['size_mb']:.1f}MB)"),
                    on_delete=lambda e, fp=f: self.remove_file(fp)
                )
            )
        
        return ft.Column(chips, spacing=5)
    
    def scan_folder(self, e):
        """扫描文件夹"""
        path = self.folder_input.value.strip()
        if not path:
            self.status_text.value = "⚠️ 请输入文件夹路径"
            self.status_text.color = ft.colors.ORANGE
            return
        
        if not os.path.exists(path):
            self.status_text.value = f"⚠️ 路径不存在: {path}"
            self.status_text.color = ft.colors.RED
            return
        
        self.folder_path = path
        self.loading.visible = True
        self.status_text.value = "🔄 扫描中..."
        self.status_text.color = ft.colors.BLUE
        
        # 扫描文件
        self.files = scan_folder(path)
        self.loading.visible = False
        
        if not self.files:
            self.status_text.value = "📂 未找到Excel文件"
            self.status_text.color = ft.colors.GREY_600
            self.file_list_view.controls.clear()
        else:
            self.status_text.value = f"✅ 找到 {len(self.files)} 个Excel文件"
            self.status_text.color = ft.colors.GREEN
            self._update_file_list()
    
    def _update_file_list(self):
        """更新文件列表显示"""
        self.file_list_view.controls.clear()
        
        for f in self.files:
            is_selected = f in self.selected_files
            
            row = ft.Container(
                content=ft.Row([
                    ft.Checkbox(
                        value=is_selected,
                        on_change=lambda e, fp=f: self.toggle_file(fp)
                    ),
                    ft.Column([
                        ft.Text(f["name"], size=14, weight=ft.FontWeight.W_500),
                        ft.Text(f"{f['size_mb']:.2f} MB", size=12, color=ft.colors.GREY_600)
                    ], spacing=2, expand=True)
                ]),
                bgcolor=ft.colors.WHITE if is_selected else ft.colors.GREY_50,
                border_radius=8,
                padding=5,
                margin=2
            )
            self.file_list_view.controls.append(row)
    
    def toggle_file(self, file_info: Dict[str, Any]):
        """切换文件选中状态"""
        if file_info in self.selected_files:
            self.selected_files.remove(file_info)
        else:
            self.selected_files.append(file_info)
        self._update_file_list()
    
    def remove_file(self, file_info: Dict[str, Any]):
        """移除已选文件"""
        if file_info in self.selected_files:
            self.selected_files.remove(file_info)
            self._update_file_list()
    
    def confirm_selection(self, e):
        """确认文件选择"""
        if not self.selected_files:
            self.status_text.value = "⚠️ 请至少选择一个文件"
            self.status_text.color = ft.colors.ORANGE
            return
        
        # 触发回调
        self.on_files_selected(self.selected_files)
        
        self.status_text.value = f"✅ 已选择 {len(self.selected_files)} 个文件"
        self.status_text.color = ft.colors.GREEN
    
    def set_folder_path(self, path: str):
        """预设文件夹路径"""
        self.folder_input.value = path
        self.folder_path = path