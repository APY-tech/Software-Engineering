"""控制台表格排版。

中文在终端里占两个字符宽，直接按 ``len()`` 补空格会错位，因此统一用
``display_width`` 计算宽度再补齐。所有列表输出都走这里，保证界面一致。
"""

from __future__ import annotations

import unicodedata


def display_width(text: str) -> int:
    """计算字符串在等宽终端里的显示宽度。"""
    width = 0
    for char in str(text):
        if unicodedata.east_asian_width(char) in ("W", "F"):
            width += 2
        else:
            width += 1
    return width


def pad(text: object, width: int, align: str = "left") -> str:
    """按显示宽度补空格。``align`` 取 left / right / center。"""
    raw = str(text)
    gap = max(0, width - display_width(raw))
    if align == "right":
        return " " * gap + raw
    if align == "center":
        left = gap // 2
        return " " * left + raw + " " * (gap - left)
    return raw + " " * gap


def render_table(
    headers: list[str],
    rows: list[list[object]],
    aligns: list[str] | None = None,
    indent: str = "  ",
) -> str:
    """渲染成对齐的文本表格，空数据时返回一行提示。"""
    if not rows:
        return f"{indent}（无记录）"
    columns = len(headers)
    flags = aligns or ["left"] * columns
    widths = [display_width(header) for header in headers]
    for row in rows:
        for index in range(columns):
            widths[index] = max(widths[index],
                                display_width(row[index]))
    gap = "  "
    lines = [indent + gap.join(
        pad(header, widths[index], flags[index])
        for index, header in enumerate(headers))]
    lines.append(indent + gap.join("-" * width for width in widths))
    for row in rows:
        lines.append(indent + gap.join(
            pad(row[index], widths[index], flags[index])
            for index in range(columns)))
    return "\n".join(lines)


def rule(char: str = "-", width: int = 66) -> str:
    """返回一条分隔线。"""
    return char * width
