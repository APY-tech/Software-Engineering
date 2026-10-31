"""应用装配。

界面层（命令行）只依赖本模块产出的 ``Application``，内部各服务之间
的依赖顺序也在这里一次写清：日志与仓储在最底层，认证依赖日志，其余
业务服务依赖认证与商品服务。这样服务之间不会互相 import 造成循环。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from campustrade.services.audit import AuditService
from campustrade.services.auth import AuthService
from campustrade.services.item import ItemService
from campustrade.services.journal import JournalService
from campustrade.services.moderation import ModerationService
from campustrade.services.stats import StatsService
from campustrade.services.trade import TradeService
from campustrade.storage import Store

DEFAULT_DB = Path("data") / "campustrade.json"


@dataclass
class Application:
    """一组装配好的服务，等价于后端的"容器"。"""

    store: Store
    journal: JournalService
    auth: AuthService
    items: ItemService
    audit: AuditService
    trade: TradeService
    moderation: ModerationService
    stats: StatsService

    def flush(self) -> None:
        """把内存改动落盘，退出前调用。"""
        self.store.commit()


def build_application(
    db_path: str | Path | None = DEFAULT_DB,
    session_ttl_minutes: int = 120,
) -> Application:
    """按依赖顺序装配全部服务。

    Args:
        db_path: 数据文件路径；传 None 使用纯内存库。
        session_ttl_minutes: 会话有效分钟数，测试里可调小以验证过期。
    """
    path = None if db_path is None else Path(db_path)
    store = Store(path)
    journal = JournalService(store)
    auth = AuthService(store, journal, ttl_minutes=session_ttl_minutes)
    items = ItemService(store, auth, journal)
    audit = AuditService(store, auth, journal, items)
    trade = TradeService(store, auth, journal, items)
    moderation = ModerationService(store, auth, journal, items)
    stats = StatsService(store, auth, journal)
    return Application(
        store=store,
        journal=journal,
        auth=auth,
        items=items,
        audit=audit,
        trade=trade,
        moderation=moderation,
        stats=stats,
    )
