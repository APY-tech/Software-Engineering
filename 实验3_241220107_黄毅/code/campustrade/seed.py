"""演示数据。

交互式运行时用它铺一份可浏览的初始数据；端到端演示脚本也复用同一份
数据，保证报告里贴出的运行结果与仓库里能跑出来的结果一致。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from campustrade.context import Application
from campustrade.models import Category, Item, ItemDraft, normalize_price

ADMIN_NO = "900000001"
SELLER_NO = "241220101"
BUYER_NO = "241220102"
OTHER_NO = "241220103"
DEMO_PASSWORD = "Campus#2026"
CATEGORY_NAMES = ("教材书籍", "数码电子", "生活用品", "运动器材")


@dataclass
class SeedData:
    """记录演示账号的令牌与分类，便于脚本继续操作。"""

    admin_token: str
    seller_token: str
    buyer_token: str
    other_token: str
    categories: dict[str, Category] = field(default_factory=dict)


def seed(app: Application) -> SeedData:
    """创建分类与三个普通账号，并返回各自的登录令牌。"""
    app.auth.bootstrap_admin(ADMIN_NO, DEMO_PASSWORD)
    for student_no in (SELLER_NO, BUYER_NO, OTHER_NO):
        app.auth.register(student_no, DEMO_PASSWORD)
    data = SeedData(
        admin_token=app.auth.login(ADMIN_NO, DEMO_PASSWORD),
        seller_token=app.auth.login(SELLER_NO, DEMO_PASSWORD),
        buyer_token=app.auth.login(BUYER_NO, DEMO_PASSWORD),
        other_token=app.auth.login(OTHER_NO, DEMO_PASSWORD),
    )
    for name in CATEGORY_NAMES:
        data.categories[name] = app.items.create_category(
            data.admin_token, name)
    return data


def seed_items(app: Application, data: SeedData) -> list[Item]:
    """铺几件商品：两件已发布、一件待审核、一件草稿。"""
    books = data.categories["教材书籍"]
    digital = data.categories["数码电子"]
    drafts = [
        ItemDraft(category_id=books.category_id, title="高等数学 第七版 上册",
                  description="有少量笔记，无缺页", price=normalize_price("18"),
                  images=["math.jpg"]),
        ItemDraft(category_id=digital.category_id, title="罗技 M590 静音鼠标",
                  description="自用半年，功能正常", price=normalize_price("89")),
        ItemDraft(category_id=books.category_id, title="考研英语真题 2010-2024",
                  description="全新未拆封", price=normalize_price("45")),
        ItemDraft(category_id=books.category_id, title="待补图的书架",
                  description="", price=normalize_price("60")),
    ]
    items = []
    for index, draft in enumerate(drafts):
        item = app.items.create_draft(data.seller_token, draft)
        items.append(item)
        if index < 3:
            app.items.submit_audit(data.seller_token, item.item_id)
    for item in items[:2]:
        app.audit.approve(data.admin_token, item.item_id)
    return items
