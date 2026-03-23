"""
数据清洗工具
负责字段名标准化、去重、空值处理等
"""

import re
import pandas as pd
from typing import List, Dict, Any, Optional


def clean_field_name(field_name: Any) -> str:
    """清洗字段名"""
    if field_name is None:
        return ""
    
    field_str = str(field_name)
    field_str = field_str.strip()
    field_str = field_str.replace('\n', '').replace('\r', '')
    field_str = re.sub(r'\s+', ' ', field_str)
    
    return field_str


def clean_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """清洗DataFrame的列名"""
    df.columns = [clean_field_name(col) for col in df.columns]
    return df


def clean_dataframe_values(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """清洗DataFrame指定列的值"""
    df = df.copy()
    
    if columns is None:
        columns = df.columns.tolist()
    
    for col in columns:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: clean_field_name(x) if isinstance(x, str) else x)
    
    return df


def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """去除重复行"""
    return df.drop_duplicates(subset=subset)


def handle_null_values(df: pd.DataFrame, strategy: str = 'keep') -> pd.DataFrame:
    """处理空值"""
    df = df.copy()
    
    if strategy == 'drop':
        df = df.dropna()
    elif strategy == 'fill_empty':
        df = df.fillna('')
    elif strategy == 'fill_na':
        df = df.fillna(pd.NA)
    
    return df


def normalize_field_for_link(field_value: Any) -> str:
    """标准化关联字段值"""
    if pd.isna(field_value) or field_value is None:
        return '__NULL__'
    return clean_field_name(str(field_value)).upper()


def build_field_mapping(field_names: List[str]) -> Dict[str, str]:
    """建立字段名映射"""
    mapping = {}
    seen = {}
    
    for name in field_names:
        cleaned = clean_field_name(name)
        if cleaned:
            if cleaned in seen:
                seen[cleaned] += 1
                mapping[f"{cleaned}_{seen[cleaned]}"] = name
            else:
                seen[cleaned] = 0
                mapping[cleaned] = name
    
    return mapping