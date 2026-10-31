"""服务基类。

约定：面向界面层的方法接收会话令牌，在方法内部换成当前用户再判断权限。
这样权限校验不会遗漏在某个界面分支里，也方便测试直接构造不同角色的
令牌调用同一个方法（REQ-016）。
"""

from __future__ import annotations

from campustrade.errors import PermissionDenied
from campustrade.models import User
from campustrade.services.auth import AuthService
from campustrade.services.journal import JournalService
from campustrade.storage import Store


class ServiceBase:
    """持有仓储、认证与日志三个基础依赖。"""

    def __init__(
        self,
        store: Store,
        auth: AuthService,
        journal: JournalService,
    ) -> None:
        self._store = store
        self._auth = auth
        self._journal = journal

    def _actor(self, token: str) -> User:
        """把令牌换成当前登录用户，令牌无效时抛 AuthError。"""
        return self._auth.authenticate(token)

    def _commit(self) -> None:
        """把本次改动落盘。"""
        self._store.commit()

    @staticmethod
    def _require_admin(actor: User) -> None:
        """要求当前用户是管理员，否则抛 PermissionDenied。"""
        if not actor.is_admin():
            raise PermissionDenied("该操作仅限管理员")
