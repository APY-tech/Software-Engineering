"""举报与治理用例（REQ-010 / REQ-014）。"""

# 用例名即文档：此处不对每个 test_ 函数再写 docstring。
# pylint: disable=missing-function-docstring

from __future__ import annotations

import pytest

from campustrade.errors import Conflict, PermissionDenied
from campustrade.models import ItemStatus, ReportState
from campustrade.services.moderation import ACTION_OFF_SHELF, ACTION_REJECT


def test_report_is_deduplicated(app, data, listed):
    first = app.moderation.submit_report(data.buyer_token, listed.item_id,
                                         "虚假描述")
    again = app.moderation.submit_report(data.buyer_token, listed.item_id,
                                         "虚假描述", "重复")
    assert first.report_id == again.report_id
    assert len(app.store.reports) == 1


def test_cannot_report_own_item(app, data, listed):
    with pytest.raises(Conflict):
        app.moderation.submit_report(data.seller_token, listed.item_id,
                                     "自己举报自己")


def test_off_shelf_action(app, data, listed):
    report = app.moderation.submit_report(data.buyer_token, listed.item_id,
                                          "违禁物品", "疑似违禁")
    app.moderation.handle(data.admin_token, report.report_id, ACTION_OFF_SHELF)
    shown = app.items.get_item(listed.item_id, data.seller_token)
    assert shown.status is ItemStatus.OFF_SHELF
    stored = app.store.reports.require(report.report_id)
    assert stored.state is ReportState.OFF_SHELF
    assert stored.handler_id is not None


def test_reject_action_keeps_item(app, data, listed):
    report = app.moderation.submit_report(data.buyer_token, listed.item_id,
                                          "其他")
    app.moderation.handle(data.admin_token, report.report_id, ACTION_REJECT)
    shown = app.items.get_item(listed.item_id, data.seller_token)
    assert shown.status is ItemStatus.PUBLISHED
    stored = app.store.reports.require(report.report_id)
    assert stored.state is ReportState.REJECTED


def test_report_cannot_be_handled_twice(app, data, listed):
    report = app.moderation.submit_report(data.buyer_token, listed.item_id,
                                          "其他")
    app.moderation.handle(data.admin_token, report.report_id, ACTION_REJECT)
    with pytest.raises(Conflict):
        app.moderation.handle(data.admin_token, report.report_id,
                              ACTION_OFF_SHELF)


def test_only_admin_can_handle(app, data, listed):
    report = app.moderation.submit_report(data.buyer_token, listed.item_id,
                                          "其他")
    with pytest.raises(PermissionDenied):
        app.moderation.handle(data.buyer_token, report.report_id,
                              ACTION_OFF_SHELF)


def test_reserved_item_cannot_be_off_shelved(app, data, listed):
    app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    report = app.moderation.submit_report(data.other_token, listed.item_id,
                                          "虚假描述")
    with pytest.raises(Conflict):
        app.moderation.handle(data.admin_token, report.report_id,
                              ACTION_OFF_SHELF)


def test_reporter_is_notified(app, data, listed):
    report = app.moderation.submit_report(data.buyer_token, listed.item_id,
                                          "虚假描述")
    app.moderation.handle(data.admin_token, report.report_id, ACTION_REJECT)
    notices = app.journal.inbox(app.auth.authenticate(data.buyer_token))
    assert any(row.kind == "REPORT" for row in notices)
