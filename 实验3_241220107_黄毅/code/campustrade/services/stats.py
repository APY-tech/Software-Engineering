"""统计汇总（REQ-018）。

卖家看本人维度，管理员看全站维度，两者都支持时间范围筛选。时间范围
按"这段时间内发生的事"统计：发布数看商品的创建时间，完成数看交易的
完成时间，而不是看记录当前的状态，避免把旧数据算进新周期。
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from campustrade.errors import ValidationError
from campustrade.models import ItemStatus, ReportState, ReservationStatus
from campustrade.services.base import ServiceBase


class StatsService(ServiceBase):
    """卖家统计与全站统计。"""

    def seller_summary(
        self,
        token: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> dict[str, object]:
        """本人商品的发布数、预约数、完成数与交易总额。"""
        actor = self._actor(token)
        self._check_range(start, end)
        items = self._store.items.find(
            lambda row: row.seller_id == actor.user_id)
        published = sum(
            1 for item in items if self._within(item.created_at, start, end))
        reservations = self._store.reservations.find(
            lambda row: any(item.item_id == row.item_id for item in items))
        reserved = sum(
            1 for row in reservations
            if self._within(row.create_at, start, end))
        amount = Decimal("0.00")
        finished = 0
        for row in reservations:
            if row.status is not ReservationStatus.FINISHED:
                continue
            if not self._within(row.finish_at, start, end):
                continue
            finished += 1
            item = self._store.items.get(row.item_id)
            if item is not None:
                amount += item.price
        return {
            "item_published": published,
            "item_reserved": reserved,
            "item_finished": finished,
            "trade_amount": amount,
        }

    def site_summary(
        self,
        token: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> dict[str, object]:
        """全站统计，仅管理员可见。"""
        actor = self._actor(token)
        self._require_admin(actor)
        self._check_range(start, end)
        items = self._store.items.all()
        users = self._store.users.all()
        reservations = self._store.reservations.all()
        reports = self._store.reports.all()
        return {
            "item_total": sum(
                1 for row in items
                if self._within(row.created_at, start, end)),
            "item_online": sum(
                1 for row in items if row.status is ItemStatus.PUBLISHED),
            "user_total": sum(
                1 for row in users
                if self._within(row.created_at, start, end)),
            "trade_finished": sum(
                1 for row in reservations
                if row.status is ReservationStatus.FINISHED
                and self._within(row.finish_at, start, end)),
            "report_handled": sum(
                1 for row in reports
                if row.state is not ReportState.PENDING
                and self._within(row.handled_at, start, end)),
            "report_pending": sum(
                1 for row in reports if row.state is ReportState.PENDING),
        }

    @staticmethod
    def _check_range(start: datetime | None, end: datetime | None) -> None:
        if start is not None and end is not None and start > end:
            raise ValidationError("开始时间不能晚于结束时间")

    @staticmethod
    def _within(moment: datetime | None, start: datetime | None,
                end: datetime | None) -> bool:
        if moment is None:
            return False
        if start is not None and moment < start:
            return False
        if end is not None and moment > end:
            return False
        return True
