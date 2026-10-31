"""包初始化：对外暴露应用装配入口。"""

from __future__ import annotations

from campustrade.context import Application, build_application

__all__ = ["Application", "build_application"]
__version__ = "1.0.0"
