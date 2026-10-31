"""仓储与统计用例（REQ-018 / REQ-013，含 JSON 快照往返）。"""

# 用例名即文档：此处不对每个 test_ 函数再写 docstring。
# pylint: disable=missing-function-docstring

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from campustrade.context import build_application
from campustrade.errors import AuthError, PermissionDenied, ValidationError
from campustrade.models import ItemDraft, ItemStatus
from campustrade.seed import seed


def test_json_roundtrip(tmp_path):
    path = tmp_path / "db.json"
    app = build_application(path)
    data = seed(app)
    item = app.items.create_draft(data.seller_token, ItemDraft(
        category_id=data.categories["教材书籍"].category_id,
        title="持久化测试",
        description="写入文件后重新加载",
        price=Decimal("12.34"),
    ))
    app.items.submit_audit(data.seller_token, item.item_id)
    app.audit.approve(data.admin_token, item.item_id)
    app.flush()

    again = build_application(path)
    loaded = again.store.items.require(item.item_id)
    assert loaded.title == "持久化测试"
    assert loaded.price == Decimal("12.34")
    assert loaded.status is ItemStatus.PUBLISHED
    assert again.store.users.first(
        lambda row: row.student_no == "241220101") is not None
    assert again.auth.authenticate(data.buyer_token).student_no == "241220102"


def test_memory_mode_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app = build_application(None)
    seed(app)
    app.flush()
    assert not list(tmp_path.iterdir())


def test_clear_empties_tables(app):
    seed(app)
    assert app.store.counts()["users"] > 0
    app.store.clear()
    assert app.store.counts()["users"] == 0


def test_seller_summary_counts_finished_trade(app, data, listed):
    app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    app.trade.confirm(data.seller_token, listed.item_id)
    app.trade.finish(data.buyer_token, listed.item_id)
    summary = app.stats.seller_summary(data.seller_token)
    assert summary["item_finished"] == 1
    assert summary["trade_amount"] == listed.price
    assert summary["item_published"] >= 1


def test_seller_summary_respects_time_range(app, data):
    future = datetime.now() + timedelta(days=1)
    summary = app.stats.seller_summary(data.seller_token, start=future)
    assert summary["item_published"] == 0
    assert summary["trade_amount"] == Decimal("0")


def test_site_summary_is_admin_only(app, data):
    with pytest.raises(PermissionDenied):
        app.stats.site_summary(data.buyer_token)
    summary = app.stats.site_summary(data.admin_token)
    assert summary["user_total"] == app.store.counts()["users"]


def test_invalid_time_range(app, data):
    start = datetime.now()
    end = start - timedelta(days=3)
    with pytest.raises(ValidationError):
        app.stats.seller_summary(data.seller_token, start, end)


def test_operation_log_is_append_only(app, data, listed):
    admin = app.auth.authenticate(data.admin_token)
    before = len(app.journal.query(admin))
    app.trade.reserve(data.buyer_token, listed.item_id, "req-1")
    after = app.journal.query(admin)
    assert len(after) == before + 1
    assert after[0].action_type == "RESERVE"
    with pytest.raises(PermissionDenied):
        app.journal.query(app.auth.authenticate(data.buyer_token))


def test_failed_login_is_logged(app, data):
    admin = app.auth.authenticate(data.admin_token)
    with pytest.raises(AuthError):
        app.auth.login("241220101", "bad-password")
    logs = app.journal.query(admin, action_type="LOGIN")
    assert any(not row.result for row in logs)


def test_corrupted_file_raises(tmp_path):
    path = tmp_path / "db.json"
    path.write_text('{"version": 99, "tables": {}}', encoding="utf-8")
    with pytest.raises(ValueError):
        build_application(path)
