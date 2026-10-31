"""操作日志与站内通知。

日志与通知是横切能力：任何业务动作结束后都写一条日志，任何需要告知
对方的结果都发一条通知。服务层通过构造注入拿到本服务，不自己拼 SQL
或直接改表，保证"只追加"的约束只有一处实现（REQ-013）。
"""

from __future__ import annotations

from datetime import datetime

from campustrade.errors import PermissionDenied, ValidationError
from campustrade.models import Notification, OperationLog, User
from campustrade.storage import Store


class JournalService:
    """操作日志与通知的写入口。"""

    def __init__(self, store: Store) -> None:
        self._store = store
        self._clock = datetime.now

    def record(
        self,
        operator_id: int,
        action_type: str,
        target_id: int,
        result: bool = True,
        detail: str = "",
    ) -> OperationLog:
        """追加一条日志。失败的操作同样记录，并写明原因。"""
        log = OperationLog(
            log_id=self._store.logs.new_id(),
            operator_id=operator_id,
            action_type=action_type,
            target_id=target_id,
            result=result,
            detail=detail,
            log_at=self._clock(),
        )
        self._store.logs.add(log)
        return log

    def query(
        self,
        actor: User,
        operator_id: int | None = None,
        action_type: str = "",
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[OperationLog]:
        """按操作人、类型与时间范围查询日志，仅管理员可用。"""
        if not actor.is_admin():
            raise PermissionDenied("只有管理员可以查询操作日志")
        if start and end and start > end:
            raise ValidationError("开始时间不能晚于结束时间")
        rows = self._store.logs.all()
        if operator_id is not None:
            rows = [row for row in rows if row.operator_id == operator_id]
        if action_type:
            rows = [row for row in rows if row.action_type == action_type]
        if start is not None:
            rows = [row for row in rows if row.log_at >= start]
        if end is not None:
            rows = [row for row in rows if row.log_at <= end]
        rows.sort(key=lambda row: row.log_at, reverse=True)
        return rows

    def notify(self, receiver_id: int, kind: str,
               content: str) -> Notification:
        """给指定用户发一条站内通知。"""
        notice = Notification(
            notify_id=self._store.notifications.new_id(),
            receiver_id=receiver_id,
            kind=kind,
            content=content,
            created_at=self._clock(),
        )
        self._store.notifications.add(notice)
        return notice

    def inbox(self, actor: User,
              unread_only: bool = False) -> list[Notification]:
        """查看本人通知，按时间倒序。"""
        rows = self._store.notifications.find(
            lambda row: row.receiver_id == actor.user_id
        )
        if unread_only:
            rows = [row for row in rows if not row.read]
        rows.sort(key=lambda row: row.created_at, reverse=True)
        return rows

    def mark_read(self, actor: User, notify_id: int) -> Notification:
        """把本人的一条通知标记为已读。"""
        notice = self._store.notifications.require(notify_id)
        if notice.receiver_id != actor.user_id:
            raise PermissionDenied("不能操作他人的通知")
        notice.read = True
        self._store.notifications.update(notice)
        return notice
