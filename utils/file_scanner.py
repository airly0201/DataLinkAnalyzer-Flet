"""
文件扫描工具
负责扫描文件夹、查找Excel文件等
"""

import os
import re
from typing import List, Dict, Any, Optional

EXCEL_EXTENSIONS = ['.xlsx', '.xls']


def scan_folder(folder_path: str) -> List[Dict[str, Any]]:
    """扫描文件夹，返回Excel文件列表"""
    files = []
    
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return files
    
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        
        if not os.path.isfile(filepath):
            continue
        
        ext = os.path.splitext(filename)[1].lower()
        if ext not in EXCEL_EXTENSIONS:
            continue
        
        try:
            stat = os.stat(filepath)
            files.append({
                'name': filename,
                'path': filepath,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified_time': stat.st_mtime
            })
        except Exception:
            continue
    
    files.sort(key=lambda x: x['modified_time'], reverse=True)
    return files


def is_large_file(file_path: str, threshold_mb: int = 50) -> bool:
    """判断是否是大文件"""
    try:
        size = os.path.getsize(file_path)
        size_mb = size / (1024 * 1024)
        return size_mb > threshold_mb
    except Exception:
        return False


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"