"""举报与治理（REQ-010 / REQ-014）。

举报只做两件事：登记线索、由管理员处置。处置结果复用商品模块的下架
方法，所以"已预约不能直接下架"这条规则不会因为走举报通道而被绕过。
"""

from __future__ import annotations

from datetime import datetime

from campustrade.errors import Conflict, ValidationError
from campustrade.models import ItemStatus, Report, ReportState
from campustrade.services.base import ServiceBase
from campustrade.services.item import ItemService

ACTION_OFF_SHELF = "OFF_SHELF"
ACTION_REJECT = "REJECT"
_ACTIONS = (ACTION_OFF_SHELF, ACTION_REJECT)
_MAX_REASON = 200


class ModerationService(ServiceBase):
    """举报登记与处置。"""

    def __init__(self, store, auth, journal, items: ItemService) -> None:
        super().__init__(store, auth, journal)
        self._items = items
        self._clock = datetime.now

    def submit_report(
        self,
        token: str,
        item_id: int,
        reason_type: str,
        reason_text: str = "",
    ) -> Report:
        """提交举报。同一用户对同一商品重复提交时返回原记录。"""
        actor = self._actor(token)
        item = self._store.items.require(item_id)
        if item.seller_id == actor.user_id:
            raise Conflict("不能举报本人发布的商品")
        if item.status not in (ItemStatus.PUBLISHED, ItemStatus.RESERVED):
            raise Conflict("只能举报已发布或已预约的商品")
        kind = (reason_type or "").strip()
        if not kind:
            raise ValidationError("请选择举报类型")
        text = (reason_text or "").strip()
        if len(text) > _MAX_REASON:
            raise ValidationError(f"举报说明不能超过 {_MAX_REASON} 字")
        existing = self._pending_of(actor.user_id, item_id)
        if existing is not None:
            return existing
        report = Report(
            report_id=self._store.reports.new_id(),
            item_id=item_id,
            reporter_id=actor.user_id,
            reason_type=kind,
            reason_text=text,
            state=ReportState.PENDING,
            created_at=self._clock(),
        )
        self._store.reports.add(report)
        self._journal.record(
            actor.user_id, "REPORT", item_id, True, kind)
        self._commit()
        return report

    def pending_reports(self, token: str) -> list[Report]:
        """待处理举报，按提交时间正序（先来先处理）。"""
        actor = self._actor(token)
        self._require_admin(actor)
        rows = self._store.reports.find(
            lambda row: row.state is ReportState.PENDING)
        rows.sort(key=lambda row: row.created_at)
        return rows

    def handle(self, token: str, report_id: int, action: str,
               note: str = "") -> Report:
        """处置举报：下架商品或驳回举报。已处理的举报不能重复处理。"""
        actor = self._actor(token)
        self._require_admin(actor)
        if action not in _ACTIONS:
            raise ValidationError(f"不支持的处置动作：{action}")
        report = self._store.reports.require(report_id)
        if report.state is not ReportState.PENDING:
            raise Conflict("该举报已处理，不能重复处理")
        item = self._store.items.require(report.item_id)
        if action == ACTION_OFF_SHELF:
            self._items.off_shelf(token, item.item_id,
                                  f"举报成立：{report.reason_type}")
            report.state = ReportState.OFF_SHELF
        else:
            report.state = ReportState.REJECTED
        report.handler_id = actor.user_id
        report.handled_at = self._clock()
        self._store.reports.update(report)
        self._journal.record(
            actor.user_id, "HANDLE_REPORT", report_id, True,
            f"{action} {note}".strip())
        self._journal.notify(
            report.reporter_id, "REPORT",
            f"你对《{item.title}》的举报已处理："
            f"{'商品已下架' if action == ACTION_OFF_SHELF else '举报未成立'}")
        self._commit()
        return report

    def reports_of_item(self, item_id: int) -> list[Report]:
        """某商品的全部举报，供详情页展示处理进度。"""
        rows = self._store.reports.find(lambda row: row.item_id == item_id)
        rows.sort(key=lambda row: row.created_at, reverse=True)
        return rows

    def _pending_of(self, reporter_id: int, item_id: int) -> Report | None:
        return self._store.reports.first(
            lambda row: row.reporter_id == reporter_id
            and row.item_id == item_id
            and row.state is ReportState.PENDING
        )
