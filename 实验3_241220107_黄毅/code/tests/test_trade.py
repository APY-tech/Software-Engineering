"""交易用例（REQ-001 / REQ-006 / REQ-007 / REQ-008 / REQ-015）。"""

# 用例名即文档：此处不对每个 test_ 函数再写 docstring。
# pylint: disable=missing-function-docstring

from __future__ import annotations

import threading
from datetime import datetime, timedelta

import pytest

from campustrade.errors import Conflict, PermissionDenied, ValidationError
from campustrade.models import ItemStatus, ReservationStatus


def test_reserve_is_idempotent(app, data, listed):
    first = app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    again = app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    assert first.reservation_id == again.reservation_id
    assert len(app.store.reservations) == 1


def test_only_one_effective_reservation(app, data, listed):
    app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    with pytest.raises(Conflict):
        app.trade.reserve(data.other_token, listed.item_id, "req-2")


def test_request_id_cannot_be_shared(app, data, listed):
    app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    with pytest.raises(Conflict):
        app.trade.reserve(data.other_token, listed.item_id, "req-1")


def test_cannot_reserve_own_item(app, data, listed):
    with pytest.raises(Conflict):
        app.trade.reserve(data.seller_token, listed.item_id, "req-1")


def test_empty_request_id_rejected(app, data, listed):
    with pytest.raises(ValidationError):
        app.trade.reserve(data.buyer_token, listed.item_id, " ")


def test_cancel_restores_published(app, data, listed):
    app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    app.trade.cancel(data.seller_token, listed.item_id)
    shown = app.items.get_item(listed.item_id, data.seller_token)
    assert shown.status is ItemStatus.PUBLISHED
    again = app.trade.reserve(data.other_token, listed.item_id, "req-2")
    assert again.status is ReservationStatus.EFFECTIVE


def test_buyer_cannot_cancel(app, data, listed):
    app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    with pytest.raises(PermissionDenied):
        app.trade.cancel(data.buyer_token, listed.item_id)


def test_confirm_and_finish_flow(app, data, listed):
    app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    with pytest.raises(PermissionDenied):
        app.trade.confirm(data.buyer_token, listed.item_id)
    app.trade.confirm(data.seller_token, listed.item_id)
    shown = app.items.get_item(listed.item_id, data.seller_token)
    assert shown.status is ItemStatus.CONFIRMED
    with pytest.raises(PermissionDenied):
        app.trade.finish(data.other_token, listed.item_id)
    app.trade.finish(data.buyer_token, listed.item_id)
    shown = app.items.get_item(listed.item_id, data.seller_token)
    assert shown.status is ItemStatus.FINISHED
    with pytest.raises(Conflict):
        app.trade.finish(data.buyer_token, listed.item_id)


def test_confirm_requires_reserved_state(app, data, listed):
    with pytest.raises(Conflict):
        app.trade.confirm(data.seller_token, listed.item_id)


def test_auto_finish_after_seven_days(app, data, listed):
    app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    reservation = app.trade.confirm(data.seller_token, listed.item_id)
    reservation.confirm_at = datetime.now() - timedelta(days=7, hours=1)
    app.store.reservations.update(reservation)
    done = app.trade.auto_finish_due()
    assert len(done) == 1
    shown = app.items.get_item(listed.item_id, data.seller_token)
    assert shown.status is ItemStatus.FINISHED
    notices = app.journal.inbox(app.auth.authenticate(data.buyer_token))
    assert any("已完成" in row.content or "完成" in row.content
               for row in notices)


def test_auto_finish_not_triggered_before_deadline(app, data, listed):
    app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    app.trade.confirm(data.seller_token, listed.item_id)
    assert app.trade.auto_finish_due() == []


def test_dispute_pauses_auto_finish(app, data, listed):
    app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    reservation = app.trade.confirm(data.seller_token, listed.item_id)
    app.trade.raise_dispute(data.buyer_token, listed.item_id, "商品与描述不符")
    reservation.confirm_at = datetime.now() - timedelta(days=9)
    app.store.reservations.update(reservation)
    assert app.trade.auto_finish_due() == []
    app.trade.resume_auto_finish(data.admin_token, listed.item_id, "协商一致")
    assert len(app.trade.auto_finish_due()) == 1


def test_concurrent_reservation_has_single_winner(app, listed):
    tokens = []
    for index in range(4):
        student_no = f"24122050{index}"
        app.auth.register(student_no, "Campus#2026")
        tokens.append(app.auth.login(student_no, "Campus#2026"))
    gate = threading.Barrier(len(tokens))
    outcomes: list[bool] = []
    guard = threading.Lock()

    def worker(token: str, index: int) -> None:
        gate.wait()
        try:
            app.trade.reserve(token, listed.item_id, f"race-{index}")
            ok = True
        except Conflict:
            ok = False
        with guard:
            outcomes.append(ok)

    threads = [threading.Thread(target=worker, args=(token, index))
               for index, token in enumerate(tokens)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert outcomes.count(True) == 1
    effective = app.store.reservations.find(
        lambda row: row.item_id == listed.item_id
        and row.status is ReservationStatus.EFFECTIVE)
    assert len(effective) == 1
