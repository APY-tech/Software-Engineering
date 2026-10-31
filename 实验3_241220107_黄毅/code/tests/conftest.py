"""测试夹具：每个用例一套干净的内存库，互不影响。

夹具之间互相引用是 pytest 的常规写法，会触发 redefined-outer-name，
这里显式关闭。
"""

# pylint: disable=redefined-outer-name

from __future__ import annotations

import pytest

from campustrade.context import build_application
from campustrade.models import Item, ItemDraft, normalize_price
from campustrade.seed import SeedData, seed


@pytest.fixture()
def app():
    """内存库上的完整应用。"""
    return build_application(None)


@pytest.fixture()
def data(app) -> SeedData:
    """带演示账号与分类的数据。"""
    return seed(app)


@pytest.fixture()
def listed(app, data) -> Item:
    """一件已发布的商品，供交易类用例复用。"""
    item = app.items.create_draft(data.seller_token, ItemDraft(
        category_id=data.categories["教材书籍"].category_id,
        title="概率论与数理统计",
        description="九成新，无笔记",
        price=normalize_price("22"),
    ))
    app.items.submit_audit(data.seller_token, item.item_id)
    app.audit.approve(data.admin_token, item.item_id)
    return item
