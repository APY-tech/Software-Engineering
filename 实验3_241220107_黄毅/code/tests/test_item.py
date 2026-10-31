"""商品与查询用例（REQ-002 / REQ-005 / REQ-009 / REQ-014）。"""

# 用例名即文档：此处不对每个 test_ 函数再写 docstring。
# pylint: disable=missing-function-docstring

from __future__ import annotations

from decimal import Decimal

import pytest

from campustrade.errors import Conflict, PermissionDenied, ValidationError
from campustrade.models import ItemDraft, ItemEdit, ItemFilter, ItemStatus
from campustrade.models import normalize_price
from campustrade.state import parse_status, status_text


def _draft(app, data, title="线性代数", price="25", description="九成新"):
    return app.items.create_draft(data.seller_token, ItemDraft(
        category_id=data.categories["教材书籍"].category_id,
        title=title,
        description=description,
        price=normalize_price(price),
    ))


def test_search_only_returns_published(app, data):
    _draft(app, data)
    hits = app.items.search(ItemFilter())
    assert hits == []


def test_search_matches_keyword_and_price(app, listed):
    assert [row.item_id for row in app.items.search(
        ItemFilter(keyword="概率"))] == [listed.item_id]
    assert app.items.search(ItemFilter(keyword="不存在的词")) == []
    assert app.items.search(ItemFilter(
        max_price=normalize_price("10"))) == []


def test_search_sort_by_price(app, data):
    cheap = _draft(app, data, title="二手台灯", price="5")
    app.items.submit_audit(data.seller_token, cheap.item_id)
    app.audit.approve(data.admin_token, cheap.item_id)
    asc = app.items.search(ItemFilter(), "price_asc")
    assert [row.price for row in asc] == sorted(row.price for row in asc)
    desc = app.items.search(ItemFilter(), "price_desc")
    assert desc[0].price == max(row.price for row in desc)


def test_search_rejects_bad_sort(app):
    with pytest.raises(ValidationError):
        app.items.search(ItemFilter(), "cheapest")


def test_search_rejects_inverted_price_range(app):
    with pytest.raises(ValidationError):
        app.items.search(ItemFilter(
            min_price=Decimal("50.00"), max_price=Decimal("10.00")))


def test_invalid_status_text():
    with pytest.raises(ValidationError):
        parse_status("已删除")
    assert parse_status("已发布") is ItemStatus.PUBLISHED
    assert status_text(ItemStatus.OFF_SHELF) == "已下架"


def test_submit_requires_description(app, data):
    item = _draft(app, data, description="")
    with pytest.raises(ValidationError):
        app.items.submit_audit(data.seller_token, item.item_id)


def test_price_must_be_positive():
    for bad in ("0", "-3", "abc"):
        with pytest.raises(ValidationError):
            normalize_price(bad)


def test_draft_edit_is_direct(app, data):
    item = _draft(app, data)
    updated = app.items.update_item(data.seller_token, item.item_id,
                                    ItemEdit(title="线性代数 第七版"))
    assert updated.status is ItemStatus.DRAFT
    assert updated.title == "线性代数 第七版"
    assert updated.version == 2


def test_others_cannot_view_draft(app, data):
    item = _draft(app, data)
    with pytest.raises(PermissionDenied):
        app.items.get_item(item.item_id, data.buyer_token)
    with pytest.raises(PermissionDenied):
        app.items.get_item(item.item_id)


def test_off_shelf_blocks_reservation(app, data, listed):
    app.items.off_shelf(data.seller_token, listed.item_id, "自己不想卖了")
    assert app.items.get_item(listed.item_id, data.seller_token).status is ItemStatus.OFF_SHELF
    with pytest.raises(Conflict):
        app.trade.reserve(data.buyer_token, listed.item_id, "req-1")


def test_seller_cannot_restore_but_admin_can(app, data, listed):
    app.items.off_shelf(data.seller_token, listed.item_id, "临时下架")
    with pytest.raises(PermissionDenied):
        app.items.restore(data.seller_token, listed.item_id)
    app.items.restore(data.admin_token, listed.item_id)
    shown = app.items.get_item(listed.item_id, data.seller_token)
    assert shown.status is ItemStatus.PUBLISHED


def test_categories_are_unique(app, data):
    with pytest.raises(Conflict):
        app.items.create_category(data.admin_token, "教材书籍")


def test_used_category_cannot_be_deleted(app, data, listed):
    category_id = listed.category_id
    with pytest.raises(Conflict):
        app.items.delete_category(data.admin_token, category_id)
    spare = app.items.create_category(data.admin_token, "临时分类")
    app.items.delete_category(data.admin_token, spare.category_id)
    assert spare.category_id not in [
        row.category_id for row in app.items.list_categories()]


def test_category_requires_admin(app, data):
    with pytest.raises(PermissionDenied):
        app.items.create_category(data.buyer_token, "违规分类")
