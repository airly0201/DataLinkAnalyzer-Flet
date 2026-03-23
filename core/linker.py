"""
多表关联引擎 - Flet优化版
支持1-5个表的链式关联查询
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from utils.cleaner import clean_dataframe_values, normalize_field_for_link


@dataclass
class LinkConfig:
    """关联配置"""
    table_name: str
    sheet_name: str
    link_field: str
    join_type: str = 'left'


@dataclass
class TableConfig:
    """表配置"""
    name: str
    file_path: str
    sheet_name: str
    fields: List[str] = field(default_factory=list)
    link_config: Optional[LinkConfig] = None


class Linker:
    """多表关联引擎"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.tables: List[TableConfig] = []
        self.dataframes: Dict[str, pd.DataFrame] = {}
    
    def add_table(self, table: TableConfig) -> None:
        """添加表配置"""
        self.tables.append(table)
        self._log(f"添加表: {table.name}")
    
    def remove_table(self, table_name: str) -> None:
        """移除表配置"""
        self.tables = [t for t in self.tables if t.name != table_name]
        self._log(f"移除表: {table_name}")
    
    def set_output_fields(self, table_name: str, fields: List[str]) -> None:
        """设置输出字段"""
        for table in self.tables:
            if table.name == table_name:
                table.fields = fields
                break
    
    def load_dataframe(self, name: str, df: pd.DataFrame) -> None:
        """加载DataFrame"""
        self.dataframes[name] = df
    
    def link_tables(self, 
                    left_table: str, 
                    right_table: str,
                    left_field: str, 
                    right_field: str,
                    join_type: str = 'left') -> pd.DataFrame:
        """关联两个表"""
        df_left = self.dataframes.get(left_table)
        df_right = self.dataframes.get(right_table)
        
        if df_left is None:
            raise ValueError(f"表 {left_table} 未加载")
        if df_right is None:
            raise ValueError(f"表 {right_table} 未加载")
        
        # 预处理：清洗关联字段
        df_left = df_left.copy()
        df_right = df_right.copy()
        
        df_left[left_field] = df_left[left_field].astype(str).str.strip().str.upper()
        df_right[right_field] = df_right[right_field].astype(str).str.strip().str.upper()
        
        # 处理空值
        df_left[left_field] = df_left[left_field].replace('NAN', '__NULL__').replace('NONE', '__NULL__').replace('', '__NULL__')
        df_right[right_field] = df_right[right_field].replace('NAN', '__NULL__').replace('NONE', '__NULL__').replace('', '__NULL__')
        
        # 创建关联键
        df_left['_link_key'] = df_left[left_field]
        df_right['_link_key'] = df_right[right_field]
        
        # 为右表字段添加前缀
        right_fields = [c for c in df_right.columns if c != '_link_key']
        rename_dict = {c: f"{right_table}.{c}" for c in right_fields}
        df_right = df_right.rename(columns=rename_dict)
        
        self._log(f"执行关联: left={left_table}, right={right_table}, join_type={join_type}")
        
        try:
            if join_type == 'left':
                result = pd.merge(df_left, df_right, on='_link_key', how='left')
            elif join_type == 'inner':
                result = pd.merge(df_left, df_right, on='_link_key', how='inner')
            elif join_type == 'outer':
                result = pd.merge(df_left, df_right, on='_link_key', how='outer')
            else:
                raise ValueError(f"不支持的连接类型: {join_type}")
            
            result = result.drop(columns=['_link_key'], errors='ignore')
            self._log(f"关联完成: {left_table} 和 {right_table} -> {len(result)} 行")
            
            return result
            
        except MemoryError:
            self._log("内存不足，使用简化关联")
            left_cols = [left_field] + [c for c in df_left.columns if 'id' in c.lower() or '编号' in c.lower()][:3]
            right_cols = [right_field] + [c for c in df_right.columns if 'id' in c.lower() or '编号' in c.lower()][:3]
            
            df_left_small = df_left[left_cols].copy()
            df_right_small = df_right[right_cols].copy()
            
            df_left_small['_link_key'] = df_left_small[left_field].astype(str).str.upper()
            df_right_small['_link_key'] = df_right_small[right_field].astype(str).str.upper()
            
            result = pd.merge(df_left_small, df_right_small, on='_link_key', how='inner')
            result = result.drop(columns=['_link_key'], errors='ignore')
            
            return result
    
    def execute_chain(self, 
                      links: List[Dict[str, Any]], 
                      output_fields: Optional[Dict[str, List[str]]] = None) -> pd.DataFrame:
        """执行链式关联查询"""
        if not self.tables:
            raise ValueError("没有配置表")
        
        if len(self.tables) == 1:
            # 单表查询
            df = self.dataframes[self.tables[0].name]
            table_name = self.tables[0].name
            
            if output_fields and table_name in output_fields:
                fields = output_fields[table_name]
                available_fields = [c for c in fields if c in df.columns]
                if available_fields:
                    output_cols = []
                    for f in available_fields:
                        if '.' in f:
                            output_cols.append(f)
                        else:
                            output_cols.append(f"{table_name}.{f}")
                    cols = [c for c in df.columns if any(f.endswith(c.split('.')[-1]) for f in output_cols)]
                    if cols:
                        df = df[cols]
            
            return df
        
        # 多表关联
        link_order = []
        processed = set()
        
        first_table = self.tables[0].name
        processed.add(first_table)
        link_order.append({'table': first_table, 'source': 'initial'})
        
        for link in links:
            left = link['left_table']
            right = link['right_table']
            
            if left in processed and right not in processed:
                link_order.append({
                    'table': right,
                    'source': 'link',
                    'left_table': left,
                    'left_field': link['left_field'],
                    'right_field': link['right_field'],
                    'join_type': link.get('join_type', 'left')
                })
                processed.add(right)
            elif right in processed and left not in processed:
                link_order.append({
                    'table': left,
                    'source': 'link',
                    'left_table': right,
                    'left_field': link['right_field'],
                    'right_field': link['left_field'],
                    'join_type': link.get('join_type', 'left')
                })
                processed.add(left)
        
        # 依次关联
        result = self.dataframes[link_order[0]['table']]
        
        for i in range(1, len(link_order)):
            link_info = link_order[i]
            
            if link_info['source'] == 'link':
                result = self.link_tables(
                    link_info['left_table'],
                    link_info['table'],
                    link_info['left_field'],
                    link_info['right_field'],
                    link_info['join_type']
                )
        
        return result
    
    def _log(self, message: str) -> None:
        """输出日志"""
        if self.debug:
            print(f"[Linker] {message}")


def create_linker(debug: bool = False) -> Linker:
    """工厂函数 - 创建Linker实例"""
    return Linker(debug=debug)