"""交易：预约、取消、确认、完成与超时自动完成。

对应需求 REQ-001 / REQ-006 / REQ-007 / REQ-008 / REQ-015。三条硬约束：

1. 同一商品至多一条有效预约 —— 临界区加锁，检查与写入不可分割；
2. 同一请求重发返回原结果 —— 以客户端生成的 ``requestId`` 为幂等键；
3. 状态迁移必须合法 —— 统一走 ``state.apply_status``。
"""

from __future__ import annotations

from datetime import datetime, timedelta

from campustrade.errors import Conflict, PermissionDenied, ValidationError
from campustrade.models import AUTO_FINISH_DAYS, Item, ItemStatus
from campustrade.models import Reservation, ReservationStatus
from campustrade.services.base import ServiceBase
from campustrade.services.item import ItemService
from campustrade.state import apply_status, status_text

_MAX_REQUEST_ID = 64


class TradeService(ServiceBase):
    """一项商品对应一条交易线：预约 -> 确认 -> 完成。"""

    def __init__(self, store, auth, journal, items: ItemService) -> None:
        super().__init__(store, auth, journal)
        self._items = items
        self._clock = datetime.now

    def reserve(self, token: str, item_id: int,
                request_id: str) -> Reservation:
        """预约商品。重发同一 ``requestId`` 直接返回首次结果（REQ-001）。"""
        actor = self._actor(token)
        key = (request_id or "").strip()
        if not key:
            raise ValidationError("缺少幂等键 requestId")
        if len(key) > _MAX_REQUEST_ID:
            raise ValidationError("requestId 过长")
        with self._store.lock:
            replay = self._by_request(item_id, key)
            if replay is not None:
                if replay.buyer_id != actor.user_id:
                    raise Conflict("该 requestId 已被其他用户使用")
                return replay
            item = self._store.items.require(item_id)
            if item.seller_id == actor.user_id:
                raise Conflict("不能预约本人发布的商品")
            if item.status is not ItemStatus.PUBLISHED:
                raise Conflict(
                    f"商品当前为{status_text(item.status)}，不能预约")
            if self._items.active_reservation(item_id) is not None:
                raise Conflict("该商品已有有效预约")
            now = self._clock()
            reservation = Reservation(
                reservation_id=self._store.reservations.new_id(),
                item_id=item_id,
                buyer_id=actor.user_id,
                request_id=key,
                status=ReservationStatus.EFFECTIVE,
                create_at=now,
            )
            self._store.reservations.add(reservation)
            self._touch(item, ItemStatus.RESERVED, now)
            self._journal.record(
                actor.user_id, "RESERVE", item_id, True,
                f"reservation_id={reservation.reservation_id}")
            self._journal.notify(
                item.seller_id, "RESERVE",
                f"你的商品《{item.title}》被预约，请及时确认交易")
            self._commit()
            return reservation

    def cancel(self, token: str, item_id: int) -> Reservation:
        """卖家取消预约，商品恢复已发布（REQ-008）。"""
        actor = self._actor(token)
        with self._store.lock:
            item = self._store.items.require(item_id)
            if item.seller_id != actor.user_id:
                raise PermissionDenied("只有卖家可以取消预约")
            reservation = self._require_effective(item)
            now = self._clock()
            reservation.status = ReservationStatus.CANCELLED
            reservation.cancel_at = now
            self._store.reservations.update(reservation)
            self._touch(item, ItemStatus.PUBLISHED, now)
            self._journal.record(
                actor.user_id, "CANCEL_RESERVE", item_id, True,
                f"reservation_id={reservation.reservation_id}")
            self._journal.notify(
                reservation.buyer_id, "CANCEL",
                f"卖家取消了《{item.title}》的预约，商品重新上架")
            self._commit()
            return reservation

    def confirm(self, token: str, item_id: int) -> Reservation:
        """卖家确认交易，进入线下交付（REQ-006）。"""
        actor = self._actor(token)
        with self._store.lock:
            item = self._store.items.require(item_id)
            if item.seller_id != actor.user_id:
                raise PermissionDenied("只有卖家可以确认交易")
            reservation = self._require_effective(item)
            if reservation.status is not ReservationStatus.EFFECTIVE:
                raise Conflict("预约已失效，不能确认交易")
            now = self._clock()
            reservation.status = ReservationStatus.CONFIRMED
            reservation.confirm_at = now
            self._store.reservations.update(reservation)
            self._touch(item, ItemStatus.CONFIRMED, now)
            self._journal.record(
                actor.user_id, "CONFIRM_TRADE", item_id, True,
                f"reservation_id={reservation.reservation_id}")
            self._journal.notify(
                reservation.buyer_id, "CONFIRM",
                f"卖家已确认《{item.title}》，请联系卖家线下交付")
            self._commit()
            return reservation

    def finish(self, token: str, item_id: int) -> Reservation:
        """买家确认收到商品，交易完成（REQ-007）。"""
        actor = self._actor(token)
        with self._store.lock:
            item = self._store.items.require(item_id)
            if item.status is not ItemStatus.CONFIRMED:
                raise Conflict(
                    f"商品当前为{status_text(item.status)}，不能确认完成")
            reservation = self._confirmed_reservation(item)
            if reservation.buyer_id != actor.user_id:
                raise PermissionDenied("只有预约买家可以确认完成")
            return self._finish(item, reservation, actor.user_id,
                                "FINISH_TRADE")

    def raise_dispute(self, token: str, item_id: int,
                      note: str) -> Reservation:
        """买家提出异议，暂停自动完成计时（REQ-015 边界情况）。"""
        actor = self._actor(token)
        item = self._store.items.require(item_id)
        reservation = self._confirmed_reservation(item)
        if reservation.buyer_id != actor.user_id:
            raise PermissionDenied("只有预约买家可以提出异议")
        if reservation.disputed:
            raise Conflict("该交易已处于异议状态")
        reservation.disputed = True
        reservation.dispute_note = (note or "").strip()[:100]
        self._store.reservations.update(reservation)
        self._journal.record(
            actor.user_id, "DISPUTE", item_id, True, reservation.dispute_note)
        self._journal.notify(
            item.seller_id, "DISPUTE",
            f"《{item.title}》的买家提出异议，自动完成计时已暂停")
        self._commit()
        return reservation

    def resume_auto_finish(self, token: str, item_id: int,
                           note: str = "") -> Reservation:
        """管理员处理完异议后恢复自动完成计时。"""
        actor = self._actor(token)
        self._require_admin(actor)
        item = self._store.items.require(item_id)
        reservation = self._confirmed_reservation(item)
        if not reservation.disputed:
            raise Conflict("该交易没有被暂停")
        reservation.disputed = False
        reservation.dispute_note = (note or "").strip()[:100]
        self._store.reservations.update(reservation)
        self._journal.record(
            actor.user_id, "RESUME_AUTO_FINISH", item_id, True,
            reservation.dispute_note)
        self._commit()
        return reservation

    def auto_finish_due(self,
                        now: datetime | None = None) -> list[Reservation]:
        """把已确认满 7 天且无异议的交易自动完成，返回本次完成的记录。

        由界面启动时或定时任务调用，不依赖用户操作，因此操作人记为 0。
        """
        moment = now or self._clock()
        deadline = timedelta(days=AUTO_FINISH_DAYS)
        finished: list[Reservation] = []
        for reservation in self._store.reservations.all():
            if reservation.status is not ReservationStatus.CONFIRMED:
                continue
            if reservation.disputed or reservation.confirm_at is None:
                continue
            if moment - reservation.confirm_at < deadline:
                continue
            item = self._store.items.get(reservation.item_id)
            if item is None or item.status is not ItemStatus.CONFIRMED:
                continue
            finished.append(self._finish(item, reservation, 0, "AUTO_FINISH"))
        return finished

    def my_reservations(self, token: str) -> list[Reservation]:
        """我作为买家产生的预约记录，按时间倒序。"""
        actor = self._actor(token)
        rows = self._store.reservations.find(
            lambda row: row.buyer_id == actor.user_id)
        rows.sort(key=lambda row: row.create_at, reverse=True)
        return rows

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    def _finish(self, item: Item, reservation: Reservation, operator_id: int,
                action: str) -> Reservation:
        now = self._clock()
        reservation.status = ReservationStatus.FINISHED
        reservation.finish_at = now
        self._store.reservations.update(reservation)
        self._touch(item, ItemStatus.FINISHED, now)
        self._journal.record(
            operator_id, action, item.item_id, True,
            f"reservation_id={reservation.reservation_id}")
        self._journal.notify(
            item.seller_id, "FINISH",
            f"《{item.title}》交易已完成，金额 {item.price} 元")
        self._journal.notify(
            reservation.buyer_id, "FINISH",
            f"《{item.title}》交易已完成，可在我的预约中查看")
        self._commit()
        return reservation

    def _touch(self, item: Item, status: ItemStatus, now: datetime) -> None:
        """迁移商品状态并刷新时间戳。状态不合法时抛 Conflict。"""
        apply_status(item, status)
        item.updated_at = now
        self._store.items.update(item)

    def _by_request(self, item_id: int, request_id: str) -> Reservation | None:
        return self._store.reservations.first(
            lambda row: row.item_id == item_id
            and row.request_id == request_id)

    def _require_effective(self, item: Item) -> Reservation:
        if item.status is not ItemStatus.RESERVED:
            raise Conflict(
                f"商品当前为{status_text(item.status)}，不是已预约状态")
        reservation = self._items.active_reservation(item.item_id)
        if reservation is None:
            raise Conflict("该商品没有有效预约")
        return reservation

    def _confirmed_reservation(self, item: Item) -> Reservation:
        reservation = self._store.reservations.first(
            lambda row: row.item_id == item.item_id
            and row.status is ReservationStatus.CONFIRMED)
        if reservation is None:
            raise Conflict("该商品没有已确认的交易")
        return reservation
