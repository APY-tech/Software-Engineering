"""把真实运行输出转成报告用的 listing 片段。

做两件事，都是纯排版处理，不改内容：
1. ✓ / ✗ 在等宽字体里缺字形，替换为 √ / ×；
2. 交互会话里每执行一条命令都会重印菜单，去掉这些重复行以免占满版面。
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
DOCS = HERE.parent.parent / "实验3_241220107_黄毅" / "code" / "docs"
OUT = HERE / "listings"

MENU_LINE = re.compile(r"^\s+(\d+\.\s|0\.\s)")
DASH_LINE = re.compile(r"^\s*-{10,}\s*$")


def display_width(text: str) -> int:
    """计算等宽显示的列数（中文占两列）。"""
    return sum(2 if unicodedata.east_asian_width(char) in "WF" else 1
               for char in text)


def wrap(text: str, limit: int = 84) -> str:
    """按显示宽度硬折行，尽量在空格处断开。"""
    result: list[str] = []
    for line in text.splitlines():
        while display_width(line) > limit:
            cut = len(line)
            width = 0
            for index, char in enumerate(line):
                width += 2 if unicodedata.east_asian_width(char) in "WF" else 1
                if width > limit:
                    cut = index
                    break
            space = line.rfind(" ", 0, cut)
            if space > cut // 2:
                cut = space
            result.append(line[:cut].rstrip())
            line = "    " + line[cut:].lstrip()
        result.append(line)
    return "\n".join(result) + "\n"


def polish(text: str) -> str:
    return text.replace("✓", "√").replace("✗", "×")


def condense_menu(text: str) -> str:
    """去掉重复的菜单项与输入提示，只保留每一步的结果。

    原始会话里，一条命令会连带打印整个菜单和"请选择：学号：密码："这类
    提示，占满版面却没什么信息。这里只保留提示链末尾的结果，用 → 标出。
    """
    kept: list[str] = []
    for line in text.splitlines():
        if MENU_LINE.match(line) or DASH_LINE.match(line):
            continue
        if line.strip().startswith("请选择"):
            parts = [part.strip() for part in line.split("：  ")
                     if part.strip()]
            if len(parts) <= 1:
                continue
            tail = parts[-1]
            if tail.count("  ") >= 2:      # 紧跟其后的是表格表头
                kept.append("  " + tail)
            else:
                kept.append("  → " + tail)
            continue
        if not line.strip() and kept and not kept[-1].strip():
            continue
        if (line.strip().startswith("当前身份") and kept
                and kept[-1].strip() == line.strip()):
            continue
        kept.append(line.rstrip())
    return "\n".join(kept).strip("\n") + "\n"


def write(name: str, text: str) -> None:
    (OUT / name).write_text(text, encoding="utf-8")
    print("wrote", name, len(text.splitlines()), "lines")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    demo = (DOCS / "demo_output.txt").read_text(encoding="utf-8")
    write("demo.tex", wrap(polish(demo)))

    cli = (DOCS / "cli_session.txt").read_text(encoding="utf-8")
    write("cli.tex", wrap(polish(condense_menu(cli))))

    pylint_before = (DOCS / "pylint_initial.txt").read_text(encoding="utf-8")
    head = [line for line in pylint_before.splitlines()
            if line.startswith("*****") or ": " in line]
    write("pylint_before.tex", "\n".join(head) + "\n")

    pylint_after = (DOCS / "pylint_final.txt").read_text(encoding="utf-8")
    tail = [line for line in pylint_after.splitlines()
            if line.startswith("Your code") or line.startswith("---")]
    write("pylint_after.tex", "\n".join(tail) + "\n")

    pytest_out = (DOCS / "pytest_output.txt").read_text(encoding="utf-8")
    write("pytest.tex", pytest_out)

    git_log = (DOCS / "git_log.txt").read_text(encoding="utf-8")
    write("git.tex", git_log)


if __name__ == "__main__":
    main()
