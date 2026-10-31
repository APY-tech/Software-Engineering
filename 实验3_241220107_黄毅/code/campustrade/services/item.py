"""商品管理：草稿、修改、提交审核、下架、公开查询与分类维护。

对应需求 REQ-002 / REQ-005 / REQ-009 / REQ-014 / REQ-017。商品的写操作
全部集中在本服务，其它模块（审核、交易、举报）要改状态时调用这里的
方法，从而复用同一套状态机校验。
"""

from __future__ import annotations

from datetime import datetime

from campustrade.errors import Conflict, PermissionDenied
from campustrade.errors import ValidationError
from campustrade.models import Category, Item, ItemDraft, ItemEdit, ItemFilter
from campustrade.models import ItemRevision, ItemStatus, Reservation
from campustrade.models import ReservationStatus, User, normalize_price
from campustrade.services.base import ServiceBase
from campustrade.state import apply_status, status_text

_MIN_TITLE = 2
_MAX_TITLE = 40
_MAX_DESCRIPTION = 500
_MAX_IMAGES = 9
_MAX_CATEGORY_NAME = 12
_EDITABLE = (ItemStatus.DRAFT, ItemStatus.PUBLISHED)
_SORT_KEYS = ("newest", "price_asc", "price_desc")


class ItemService(ServiceBase):
    """商品与分类。"""

    def __init__(self, store, auth, journal) -> None:  # noqa: D107
        super().__init__(store, auth, journal)
        self._clock = datetime.now

    # ------------------------------------------------------------------
    # 分类（REQ-009，归入商品模块，避免分类模块反向依赖商品模块）
    # ------------------------------------------------------------------

    def list_categories(self) -> list[Category]:
        """列出全部分类，允许匿名访问。"""
        return sorted(self._store.categories.all(), key=lambda row: row.name)

    def create_category(self, token: str, name: str) -> Category:
        """新增分类，仅管理员可用。"""
        actor = self._actor(token)
        self._require_admin(actor)
        clean = self._clean_category_name(name)
        if self._category_named(clean) is not None:
            raise Conflict(f"分类“{clean}”已存在")
        category = Category(
            category_id=self._store.categories.new_id(),
            name=clean,
            created_at=self._clock(),
        )
        self._store.categories.add(category)
        self._journal.record(
            actor.user_id, "CREATE_CATEGORY", category.category_id, True,
            clean)
        self._commit()
        return category

    def rename_category(self, token: str, category_id: int, name: str) -> None:
        """修改分类名，重名时拒绝。"""
        actor = self._actor(token)
        self._require_admin(actor)
        category = self._store.categories.require(category_id)
        clean = self._clean_category_name(name)
        other = self._category_named(clean)
        if other is not None and other.category_id != category_id:
            raise Conflict(f"分类“{clean}”已存在")
        old = category.name
        category.name = clean
        self._store.categories.update(category)
        self._journal.record(
            actor.user_id, "RENAME_CATEGORY", category_id, True,
            f"{old} -> {clean}")
        self._commit()

    def delete_category(self, token: str, category_id: int) -> None:
        """删除分类；已被商品使用时拒绝（需先迁移商品）。"""
        actor = self._actor(token)
        self._require_admin(actor)
        category = self._store.categories.require(category_id)
        used = self._store.items.find(
            lambda row: row.category_id == category_id)
        if used:
            raise Conflict(
                f"分类“{category.name}”下仍有 {len(used)} 件商品，不能删除")
        self._store.categories.remove(category_id)
        self._journal.record(
            actor.user_id, "DELETE_CATEGORY", category_id, True, category.name)
        self._commit()

    # ------------------------------------------------------------------
    # 商品写入
    # ------------------------------------------------------------------

    def create_draft(self, token: str, draft: ItemDraft) -> Item:
        """保存商品草稿。草稿允许描述留空，提交审核时再强制必填。"""
        actor = self._actor(token)
        values = self._validate_fields(draft, strict=False)
        now = self._clock()
        item = Item(
            item_id=self._store.items.new_id(),
            seller_id=actor.user_id,
            category_id=values.category_id,
            title=values.title,
            description=values.description,
            price=values.price,
            images=list(values.images),
            status=ItemStatus.DRAFT,
            version=1,
            created_at=now,
            updated_at=now,
        )
        self._store.items.add(item)
        self._journal.record(
            actor.user_id, "CREATE_ITEM", item.item_id, True, item.title)
        self._commit()
        return item

    def update_item(self, token: str, item_id: int, edit: ItemEdit) -> Item:
        """修改商品。

        草稿直接保存；已发布商品的修改写入待审内容，公开展示状态保持
        已发布（REQ-017）；已预约、已确认、已完成、已下架的商品不可修改。
        """
        actor = self._actor(token)
        item = self._require_own_item(actor, item_id)
        if item.status is ItemStatus.AUDITING:
            raise Conflict("商品正在审核中，不能修改")
        if item.status not in _EDITABLE:
            raise Conflict(
                f"{status_text(item.status)}的商品不能修改，"
                "请先取消预约或等交易完成")
        merged = ItemDraft(
            category_id=edit.category_id or item.category_id,
            title=item.title if edit.title is None else edit.title,
            description=(item.description if edit.description is None
                         else edit.description),
            price=item.price if edit.price is None else edit.price,
            images=list(item.images) if edit.images is None else edit.images,
        )
        values = self._validate_fields(merged, strict=False)
        now = self._clock()
        if values.category_id != item.category_id and not self._category_ok(
                values.category_id):
            raise ValidationError("分类不存在")
        if item.status is ItemStatus.PUBLISHED:
            self._stage_revision(item, values, now)
        else:
            item.title = values.title
            item.description = values.description
            item.price = values.price
            item.category_id = values.category_id
            item.images = list(values.images)
            item.updated_at = now
            item.version += 1
            self._store.items.update(item)
        action = ("MODIFY_PUBLISHED" if item.status is ItemStatus.PUBLISHED
                  else "MODIFY_DRAFT")
        self._journal.record(
            actor.user_id, action, item.item_id, True, item.title)
        self._commit()
        return item

    def submit_audit(self, token: str, item_id: int) -> Item:
        """把草稿提交审核，必填字段缺失时拒绝（REQ-002）。"""
        actor = self._actor(token)
        item = self._require_own_item(actor, item_id)
        if item.status is not ItemStatus.DRAFT:
            raise Conflict(f"只有草稿可以提交审核，当前为{status_text(item.status)}")
        missing = self._missing_fields(item)
        if missing:
            raise ValidationError("必填字段未填写：" + "、".join(missing))
        apply_status(item, ItemStatus.AUDITING)
        item.updated_at = self._clock()
        self._store.items.update(item)
        self._journal.record(
            actor.user_id, "SUBMIT_AUDIT", item.item_id, True,
            f"version={item.version}")
        self._commit()
        return item

    def off_shelf(self, token: str, item_id: int, reason: str = "") -> Item:
        """下架商品。卖家只能下架本人已发布的商品（REQ-014）。"""
        actor = self._actor(token)
        item = self._store.items.require(item_id)
        if not actor.is_admin() and item.seller_id != actor.user_id:
            raise PermissionDenied("只能下架本人的商品")
        apply_status(item, ItemStatus.OFF_SHELF)
        item.off_shelf_reason = (reason or "").strip()[:60]
        item.updated_at = self._clock()
        self._store.items.update(item)
        self._journal.record(
            actor.user_id, "OFF_SHELF", item.item_id, True,
            item.off_shelf_reason or "无原因")
        if actor.user_id != item.seller_id:
            self._journal.notify(
                item.seller_id, "OFF_SHELF",
                f"你的商品《{item.title}》已被管理员下架："
                f"{item.off_shelf_reason or '未说明'}")
        self._commit()
        return item

    def restore(self, token: str, item_id: int) -> Item:
        """管理员解除下架，商品恢复为已发布（卖家不能自行恢复）。"""
        actor = self._actor(token)
        self._require_admin(actor)
        item = self._store.items.require(item_id)
        apply_status(item, ItemStatus.PUBLISHED)
        item.off_shelf_reason = ""
        item.updated_at = self._clock()
        self._store.items.update(item)
        self._journal.record(
            actor.user_id, "RESTORE_ITEM", item.item_id, True, item.title)
        self._journal.notify(
            item.seller_id, "RESTORE", f"你的商品《{item.title}》已恢复上架")
        self._commit()
        return item

    # ------------------------------------------------------------------
    # 商品读取
    # ------------------------------------------------------------------

    def get_item(self, item_id: int, token: str | None = None) -> Item:
        """查看商品详情。非公开状态的商品只有卖家本人和管理员可见。"""
        item = self._store.items.require(item_id)
        if item.is_public():
            return item
        if token:
            actor = self._auth.authenticate(token)
            if actor.is_admin() or actor.user_id == item.seller_id:
                return item
        raise PermissionDenied("该商品当前不对其他用户展示")

    def my_items(self, token: str) -> list[Item]:
        """本人发布的商品，按最近更新排序。"""
        actor = self._actor(token)
        rows = self._store.items.find(
            lambda row: row.seller_id == actor.user_id)
        rows.sort(key=lambda row: row.updated_at, reverse=True)
        return rows

    def search(self, cond: ItemFilter, sort: str = "newest") -> list[Item]:
        """公开查询，只返回已发布商品（REQ-005）。

        ``cond.status`` 传已发布以外的合法状态时返回空列表：那些商品按
        需求不得出现在公开结果里；传入非法状态名请在界面层用
        ``state.parse_status`` 拦截。
        """
        if sort not in _SORT_KEYS:
            raise ValidationError(f"不支持的排序方式：{sort}")
        if (cond.min_price is not None and cond.max_price is not None
                and cond.min_price > cond.max_price):
            raise ValidationError("价格下限不能高于上限")
        if cond.status is not None and cond.status is not ItemStatus.PUBLISHED:
            return []
        rows = [row for row in self._store.items.all() if row.is_public()]
        rows = [row for row in rows if self._match(row, cond)]
        return self._sort(rows, sort)

    def revision_of(self, item_id: int) -> ItemRevision | None:
        """返回商品当前的待审修改，没有则返回 None。"""
        return self._store.revisions.first(lambda row: row.item_id == item_id)

    def active_reservation(self, item_id: int) -> Reservation | None:
        """返回商品当前的有效预约，没有则返回 None。"""
        return self._store.reservations.first(
            lambda row: row.item_id == item_id
            and row.status is ReservationStatus.EFFECTIVE
        )

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    def _stage_revision(self, item: Item, values: ItemDraft,
                        now: datetime) -> None:
        """把已发布商品的新内容写入待审表，商品本身仍展示旧信息。"""
        revision = self.revision_of(item.item_id)
        if revision is None:
            revision = ItemRevision(
                revision_id=self._store.revisions.new_id(),
                item_id=item.item_id,
                category_id=values.category_id,
                title=values.title,
                description=values.description,
                price=values.price,
                images=list(values.images),
                submit_at=now,
            )
            self._store.revisions.add(revision)
        else:
            revision.category_id = values.category_id
            revision.title = values.title
            revision.description = values.description
            revision.price = values.price
            revision.images = list(values.images)
            revision.submit_at = now
            self._store.revisions.update(revision)
        item.updated_at = now
        item.version += 1
        self._store.items.update(item)

    def _match(self, item: Item, cond: ItemFilter) -> bool:
        if (cond.category_id is not None
                and item.category_id != cond.category_id):
            return False
        if cond.min_price is not None and item.price < cond.min_price:
            return False
        if cond.max_price is not None and item.price > cond.max_price:
            return False
        keyword = cond.keyword.strip().lower()
        if keyword:
            haystack = f"{item.title} {item.description}".lower()
            if keyword not in haystack:
                return False
        return True

    @staticmethod
    def _sort(rows: list[Item], sort: str) -> list[Item]:
        if sort == "price_asc":
            return sorted(rows, key=lambda row: (row.price, row.item_id))
        if sort == "price_desc":
            return sorted(rows, key=lambda row: (-row.price, row.item_id))
        return sorted(rows, key=lambda row: row.published_at or row.created_at,
                      reverse=True)

    def _require_own_item(self, actor: User, item_id: int) -> Item:
        item = self._store.items.require(item_id)
        if item.seller_id != actor.user_id:
            raise PermissionDenied("只能操作本人发布的商品")
        return item

    def _category_named(self, name: str) -> Category | None:
        lowered = name.lower()
        return self._store.categories.first(
            lambda row: row.name.lower() == lowered)

    def _category_ok(self, category_id: int) -> bool:
        return self._store.categories.get(category_id) is not None

    @staticmethod
    def _clean_category_name(name: str) -> str:
        clean = (name or "").strip()
        if not clean:
            raise ValidationError("分类名不能为空")
        if len(clean) > _MAX_CATEGORY_NAME:
            raise ValidationError(f"分类名不能超过 {_MAX_CATEGORY_NAME} 个字")
        return clean

    def _validate_fields(self, draft: ItemDraft, strict: bool) -> ItemDraft:
        """校验并规范化商品字段，返回新值对象。"""
        title = (draft.title or "").strip()
        description = (draft.description or "").strip()
        if not title:
            raise ValidationError("商品标题不能为空")
        if len(title) < _MIN_TITLE or len(title) > _MAX_TITLE:
            raise ValidationError(
                f"标题长度应在 {_MIN_TITLE}~{_MAX_TITLE} 字之间")
        if len(description) > _MAX_DESCRIPTION:
            raise ValidationError(f"描述不能超过 {_MAX_DESCRIPTION} 字")
        if strict and not description:
            raise ValidationError("商品描述不能为空")
        price = normalize_price(draft.price)
        if not self._category_ok(draft.category_id):
            raise ValidationError("分类不存在")
        images = [str(link).strip() for link in draft.images]
        images = [link for link in images if link]
        if len(images) > _MAX_IMAGES:
            raise ValidationError(f"图片不能超过 {_MAX_IMAGES} 张")
        return ItemDraft(category_id=draft.category_id, title=title,
                         description=description, price=price, images=images)

    @staticmethod
    def _missing_fields(item: Item) -> list[str]:
        missing = []
        if not item.title.strip():
            missing.append("标题")
        if not item.description.strip():
            missing.append("描述")
        if item.price <= 0:
            missing.append("价格")
        return missing
