"""
结果展示页面 - Flet 移动端优化版
"""

import flet as ft
import os
import pandas as pd
from typing import Any, Callable, Optional, Dict, List
from datetime import datetime

from core.excel_reader import create_reader
from core.linker import create_linker


class ResultPage:
    """结果展示页面"""
    
    def __init__(self, 
                 tables: Dict[str, Dict[str, Any]], 
                 links: List[Dict[str, Any]],
                 output_fields: Dict[str, List[str]],
                 on_restart: Callable):
        self.tables = tables
        self.links = links
        self.output_fields = output_fields
        self.on_restart = on_restart
        
        self.result_df: Optional[pd.DataFrame] = None
        self.output_path = ""
        
        # 状态
        self.status_text = ft.Text(
            "准备执行查询...",
            size=14,
            color=ft.colors.GREY_600
        )
        
        self.loading = ft.ProgressBar(visible=False)
        
        # 结果信息
        self.result_info = ft.Column(spacing=10)
        
        # 结果表格预览
        self.preview_table = ft.DataTable(
            columns=[],
            rows=[],
            heading_row_color=ft.colors.BLUE_GREY,
            data_row_color=ft.colors.WHITE
        )
        
        self.preview_container = ft.Container(
            content=ft.ListView([
                ft.Text("暂无数据预览", color=ft.colors.GREY_500)
            ]),
            border_radius=10,
            bgcolor=ft.colors.WHITE,
            padding=10,
            expand=True
        )
    
    def get_container(self) -> ft.Container:
        """获取页面容器"""
        return ft.Container(
            content=ft.Column([
                # 标题
                ft.Container(
                    content=ft.Text(
                        "📊 查询结果",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    padding=15
                ),
                
                # 状态
                self.status_text,
                self.loading,
                
                # 结果信息
                ft.Container(
                    content=self.result_info,
                    border_radius=10,
                    bgcolor=ft.colors.WHITE,
                    padding=15
                ),
                
                # 数据预览
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 数据预览 (前10行)", size=16, weight=ft.FontWeight.BOLD),
                        self.preview_container
                    ]),
                    border_radius=10,
                    bgcolor=ft.colors.WHITE,
                    padding=10,
                    expand=True
                ),
                
                # 操作按钮
                ft.Container(
                    content=ft.Column([
                        ft.ElevatedButton(
                            "📥 导出Excel",
                            icon=ft.icons.DOWNLOAD,
                            on_click=self.export_excel,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.GREEN,
                                color=ft.colors.WHITE
                            ),
                            expand=True
                        ),
                        ft.ElevatedButton(
                            "🔄 重新开始",
                            icon=ft.icons.REFRESH,
                            on_click=self.restart,
                            expand=True
                        )
                    ], spacing=10),
                    padding=10
                )
            ]),
            bgcolor=ft.colors.GREY_100,
            expand=True
        )
    
    async def execute_query(self, page: ft.Page):
        """执行查询"""
        self.loading.visible = True
        self.status_text.value = "🔄 正在执行查询..."
        self.status_text.color = ft.colors.BLUE
        
        try:
            # 创建关联器
            linker = create_linker(debug=True)
            
            # 读取并加载表数据
            for file_path, table_info in self.tables.items():
                sheet_name = table_info['sheets'][0]['name']
                
                # 获取需要读取的字段
                needed_fields = self.output_fields.get(file_path, [])
                
                # 如果有关联，添加关联字段
                for link in self.links:
                    if link['left_table'] == file_path:
                        if link['left_field'] not in needed_fields:
                            needed_fields.append(link['left_field'])
                    if link['right_table'] == file_path:
                        if link['right_field'] not in needed_fields:
                            needed_fields.append(link['right_field'])
                
                # 读取数据
                reader = create_reader(file_path)
                df = reader.read_sheet(sheet_name, usecols=needed_fields if needed_fields else None)
                
                table_name = table_info['filename']
                linker.load_dataframe(table_name, df)
                
                # 添加表配置
                from core.linker import TableConfig
                linker.add_table(TableConfig(
                    name=table_name,
                    file_path=file_path,
                    sheet_name=sheet_name,
                    fields=needed_fields
                ))
            
            # 执行链式关联
            self.status_text.value = "🔄 正在关联表..."
            
            if not self.links:
                # 单表查询
                table_name = list(self.tables.values())[0]['filename']
                self.result_df = linker.dataframes[table_name]
            else:
                # 多表关联
                self.result_df = linker.execute_chain(self.links, self.output_fields)
            
            # 处理输出字段
            if self.output_fields:
                output_cols = []
                for table_key, fields in self.output_fields.items():
                    table_name = self.tables[table_key]['filename']
                    for f in fields:
                        matching = [c for c in self.result_df.columns 
                                   if c == f 
                                   or c == f'{table_name}.{f}'
                                   or ('.' in c and c.split('.')[-1] == f)]
                        output_cols.extend(matching)
                
                if output_cols:
                    # 去重保持顺序
                    seen = set()
                    unique_cols = []
                    for c in output_cols:
                        if c not in seen:
                            seen.add(c)
                            unique_cols.append(c)
                    self.result_df = self.result_df[unique_cols]
            
            # 显示结果
            self._display_result()
            
            self.loading.visible = False
            self.status_text.value = f"✅ 查询完成: {len(self.result_df)} 行, {len(self.result_df.columns)} 列"
            self.status_text.color = ft.colors.GREEN
            
        except Exception as e:
            self.loading.visible = False
            self.status_text.value = f"❌ 查询失败: {str(e)}"
            self.status_text.color = ft.colors.RED
            import traceback
            traceback.print_exc()
    
    def _display_result(self):
        """显示结果"""
        if self.result_df is None or len(self.result_df) == 0:
            self.result_info.controls = [
                ft.Text("⚠️ 查询结果为空", size=16, color=ft.colors.ORANGE)
            ]
            return
        
        # 结果信息
        rows = len(self.result_df)
        cols = len(self.result_df.columns)
        
        self.result_info.controls = [
            ft.Row([
                ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN, size=30),
                ft.Column([
                    ft.Text("查询成功!", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"📊 结果: {rows} 行 × {cols} 列", size=14),
                    ft.Text(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", size=12, color=ft.colors.GREY_600)
                ], spacing=2)
            ], spacing=10)
        ]
        
        # 数据预览
        preview_df = self.result_df.head(10)
        
        # 构建表格
        columns = []
        for col in preview_df.columns:
            columns.append(
                ft.DataColumn(ft.Text(col, size=12, weight=ft.FontWeight.BOLD))
            )
        
        rows_data = []
        for _, row in preview_df.iterrows():
            cells = []
            for val in row:
                cell_val = str(val)[:20] if pd.notna(val) else "NULL"
                cells.append(ft.DataCell(ft.Text(cell_val, size=11)))
            rows_data.append(ft.DataRow(cells=cells))
        
        # 限制列数（太多列显示不下）
        if len(columns) > 6:
            columns = columns[:6]
            rows_data = [ft.DataRow(cells=r.cells[:6]) for r in rows_data]
        
        self.preview_table = ft.DataTable(
            columns=columns,
            rows=rows_data,
            heading_row_color=ft.colors.BLUE_GREY,
            data_row_color=ft.colors.WHITE,
            horizontal_lines=ft.BorderSide(1, ft.colors.GREY_300),
            vertical_lines=ft.BorderSide(1, ft.colors.GREY_300)
        )
        
        scroll_view = ft.SingleChildScrollView(
            scroll_mode=ft.ScrollMode.HORIZONTAL,
            content=self.preview_table
        )
        
        self.preview_container.content = ft.ListView([
            ft.Container(
                content=scroll_view,
                expand=True
            )
        ])
    
    def export_excel(self, e):
        """导出Excel"""
        if self.result_df is None or len(self.result_df) == 0:
            self.status_text.value = "⚠️ 没有可导出的数据"
            self.status_text.color = ft.colors.ORANGE
            return
        
        try:
            # 生成输出路径
            output_dir = os.path.expanduser("~/Download")
            if not os.path.exists(output_dir):
                output_dir = os.path.expanduser("~")
            
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_path = os.path.join(output_dir, f"query_result_{timestamp}.xlsx")
            
            self.result_df.to_excel(self.output_path, index=False)
            
            self.status_text.value = f"✅ 已导出: {self.output_path}"
            self.status_text.color = ft.colors.GREEN
            
            # 显示导出成功对话框
            pass
            
        except Exception as ex:
            self.status_text.value = f"❌ 导出失败: {str(ex)}"
            self.status_text.color = ft.colors.RED
    
    def restart(self, e):
        """重新开始"""
        self.on_restart()