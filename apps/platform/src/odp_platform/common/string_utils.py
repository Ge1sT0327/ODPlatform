import unicodedata
from typing import List, Optional

def _char_width(ch: str) -> int:
    """单字符显示宽度：CJK 字符返回 2，其余 1。"""
    code = ord(ch)
    # CJK Unified Ideographs + CJK Compatibility + fullwidth forms
    if (0x1100 <= code <= 0x115F or 0x2329 <= code <= 0x232A or
        0x2E80 <= code <= 0xA4CF or 0xA960 <= code <= 0xA97C or
        0xAC00 <= code <= 0xD7A3 or 0xF900 <= code <= 0xFAFF or
        0xFE10 <= code <= 0xFE19 or 0xFE30 <= code <= 0xFE6F or
        0xFF01 <= code <= 0xFF60 or 0xFFE0 <= code <= 0xFFE6 or
        0x1F300 <= code <= 0x1FAD6 or
        unicodedata.east_asian_width(ch) in ('F', 'W')):
        return 2
    return 1

def display_width(text: str) -> int:
    """计算字符串的显示宽度（CJK 字符=2, ASCII=1）。"""
    return sum(_char_width(c) for c in text)

def pad_to_width(text: str, target_width: int, align: str = "left") -> str:
    """
    将 text 填充到 target_width 显示宽度。
    align: "left" → 右侧补空格, "right" → 左侧补空格, "center" → 两侧均分。
    """
    current = display_width(text)
    if current >= target_width:
        return text
    diff = target_width - current
    if align == "left":
        return text + " " * diff
    elif align == "right":
        return " " * diff + text
    elif align == "center":
        left = diff // 2
        return " " * left + text + " " * (diff - left)
    return text

def format_table_row(
    columns: List[str],
    widths: List[int],
    aligns: Optional[List[str]] = None,
    separator: str = "|",
    padding: int = 1,
) -> str:
    """
    格式化表格行。columns 长度等于 widths 长度。
    aligns 默认全左对齐。
    返回: "| col1  | col2  | col3  |"
    """
    if aligns is None:
        aligns = ["left"] * len(columns)
    sp = " " * padding
    cells = []
    for i, col in enumerate(columns):
        cells.append(pad_to_width(col, widths[i], aligns[i]))
    return separator + sp + (sp + separator + sp).join(cells) + sp + separator

def format_table_separator(
    widths: List[int],
    char: str = "-",
    separator: str = "|",
    padding: int = 1,
) -> str:
    """格式化表格分隔线: "|--------|--------|--------|" """
    sp = " " * padding
    cells = [char * w for w in widths]
    return separator + sp + (sp + separator + sp).join(cells) + sp + separator
