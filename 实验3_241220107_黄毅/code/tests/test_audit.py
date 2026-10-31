"""审核用例（REQ-003 / REQ-017 / REQ-019）。"""

# 用例名即文档：此处不对每个 test_ 函数再写 docstring。
# pylint: disable=missing-function-docstring

from __future__ import annotations

import pytest

from campustrade.errors import Conflict, PermissionDenied, ValidationError
from campustrade.models import AuditResult, ItemDraft, ItemEdit, ItemStatus
from campustrade.models import normalize_price
from campustrade.state import status_text


def _draft(app, data, title="二手显示器"):
    item = app.items.create_draft(data.seller_token, ItemDraft(
        category_id=data.categories["数码电子"].category_id,
        title=title,
        description="自用一年，无坏点",
        price=normalize_price("300"),
    ))
    app.items.submit_audit(data.seller_token, item.item_id)
    return item


def test_approve_publishes(app, data):
    item = _draft(app, data)
    approved = app.audit.approve(data.admin_token, item.item_id)
    assert approved.status is ItemStatus.PUBLISHED
    assert approved.published_at is not None


def test_reject_returns_to_draft(app, data):
    item = _draft(app, data)
    rejected = app.audit.reject(data.admin_token, item.item_id, "图片模糊")
    assert rejected.status is ItemStatus.DRAFT
    assert status_text(rejected.status) == "草稿"


def test_reject_requires_reason(app, data):
    item = _draft(app, data)
    with pytest.raises(ValidationError):
        app.audit.reject(data.admin_token, item.item_id, "   ")


def test_only_admin_can_audit(app, data):
    item = _draft(app, data)
    with pytest.raises(PermissionDenied):
        app.audit.approve(data.seller_token, item.item_id)
    with pytest.raises(PermissionDenied):
        app.audit.reject(data.seller_token, item.item_id, "自己批自己")


def test_revision_keeps_old_price_until_approved(app, data, listed):
    old_price = listed.price
    app.items.update_item(data.seller_token, listed.item_id,
                          ItemEdit(price=normalize_price("18")))
    shown = app.items.get_item(listed.item_id, data.seller_token)
    assert shown.price == old_price
    assert shown.status is ItemStatus.PUBLISHED
    assert app.items.revision_of(listed.item_id) is not None

    app.audit.approve(data.admin_token, listed.item_id)
    shown = app.items.get_item(listed.item_id, data.seller_token)
    assert shown.price == normalize_price("18")
    assert app.items.revision_of(listed.item_id) is None


def test_rejected_revision_is_discarded(app, data, listed):
    old_price = listed.price
    app.items.update_item(data.seller_token, listed.item_id,
                          ItemEdit(price=normalize_price("1")))
    app.audit.reject(data.admin_token, listed.item_id, "价格明显异常")
    shown = app.items.get_item(listed.item_id, data.seller_token)
    assert shown.status is ItemStatus.PUBLISHED
    assert shown.price == old_price
    assert app.items.revision_of(listed.item_id) is None


def test_revision_can_be_approved_after_reservation(app, data, listed):
    app.items.update_item(data.seller_token, listed.item_id,
                          ItemEdit(title="概率论与数理统计 第五版"))
    app.trade.reserve(data.buyer_token, listed.item_id, "req-r1")
    app.audit.approve(data.admin_token, listed.item_id)
    shown = app.items.get_item(listed.item_id, data.seller_token)
    assert shown.title == "概率论与数理统计 第五版"
    assert shown.status is ItemStatus.RESERVED


def test_stale_version_is_rejected(app, data, listed):
    stale = listed.version
    app.items.update_item(data.seller_token, listed.item_id,
                          ItemEdit(price=normalize_price("20")))
    with pytest.raises(Conflict):
        app.audit.approve(data.admin_token, listed.item_id,
                          expected_version=stale)


def test_history_records_every_round(app, data):
    item = _draft(app, data)
    app.audit.reject(data.admin_token, item.item_id, "缺少实拍图")
    app.items.update_item(data.seller_token, item.item_id,
                          ItemEdit(description="已补实拍图"))
    app.items.submit_audit(data.seller_token, item.item_id)
    app.audit.approve(data.admin_token, item.item_id)
    records = app.audit.history(data.seller_token, item.item_id)
    assert [row.result for row in records] == [AuditResult.APPROVED,
                                               AuditResult.REJECTED]
    with pytest.raises(PermissionDenied):
        app.audit.history(data.buyer_token, item.item_id)
    assert len(app.audit.history(data.admin_token, item.item_id)) == 2


def test_pending_lists_both_kinds(app, data, listed):
    fresh = _draft(app, data, title="待审的新商品")
    app.items.update_item(data.seller_token, listed.item_id,
                          ItemEdit(price=normalize_price("21")))
    pending = [row.item_id for row in app.audit.pending(data.admin_token)]
    assert fresh.item_id in pending
    assert listed.item_id in pending
