"""程序入口。

用法::

    python run.py               # 交互式运行，数据保存在 data/campustrade.json
    python run.py --seed        # 首次运行先铺演示数据
    python run.py --demo        # 跑一遍端到端演示（内存库，不影响数据文件）
    python run.py --memory      # 只使用内存库，退出即清空
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from campustrade.cli.shell import Shell
from campustrade.context import DEFAULT_DB, build_application
from campustrade.demo import run_demo
from campustrade.seed import seed, seed_items


def main(argv: Sequence[str] | None = None) -> int:
    """解析参数并启动。返回进程退出码。"""
    parser = argparse.ArgumentParser(
        description="校园二手交易系统（命令行版）")
    parser.add_argument("--db", default=str(DEFAULT_DB),
                        help="数据文件路径，默认 data/campustrade.json")
    parser.add_argument("--memory", action="store_true",
                        help="只使用内存库，退出后不保留数据")
    parser.add_argument("--seed", action="store_true",
                        help="库为空时先写入演示数据")
    parser.add_argument("--demo", action="store_true",
                        help="运行端到端演示后退出")
    args = parser.parse_args(argv)

    if args.demo:
        run_demo()
        return 0

    app = build_application(None if args.memory else args.db)
    if args.seed and not app.store.users.all():
        data = seed(app)
        seed_items(app, data)
        print("已初始化演示数据：管理员 900000001，密码 Campus#2026")
    Shell(app).run()
    app.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
