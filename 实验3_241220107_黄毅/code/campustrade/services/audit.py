"""商品审核（REQ-003 / REQ-019）。

审核对象有两种形态，本服务用同一套接口处理：

* 首次提交：商品状态为 ``AUDITING``，通过后变为已发布；
* 已发布商品改内容：商品状态可能仍是 ``PUBLISHED``，也可能在审核期间
  被买家预约成 ``RESERVED``（REQ-017 允许），新内容在待审表里。通过后
  一次性替换（原子更新），驳回则丢弃待审内容、继续展示旧信息。
"""

from __future__ import annotations

from datetime import datetime

from campustrade.errors import Conflict, PermissionDenied, ValidationError
from campustrade.models import AuditRecord, AuditResult, Item, ItemRevision
from campustrade.models import ItemStatus
from campustrade.services.base import ServiceBase
from campustrade.services.item import ItemService
from campustrade.state import apply_status, status_text

# 待审内容可以挂在这些状态上：商品仍在对外展示，只是内容待替换。
_REVISION_HOLDERS = (
    ItemStatus.PUBLISHED,
    ItemStatus.RESERVED,
    ItemStatus.CONFIRMED,
)


class AuditService(ServiceBase):
    """审核队列与审核历史。"""

    def __init__(self, store, auth, journal, items: ItemService) -> None:
        super().__init__(store, auth, journal)
        self._items = items
        self._clock = datetime.now

    def pending(self, token: str) -> list[Item]:
        """待审核商品：首次送审的商品，以及带待审修改的在线商品。"""
        actor = self._actor(token)
        self._require_admin(actor)
        rows = []
        for item in self._store.items.all():
            if item.status is ItemStatus.AUDITING:
                rows.append(item)
            elif (item.status in _REVISION_HOLDERS
                  and self._items.revision_of(item.item_id) is not None):
                rows.append(item)
        rows.sort(key=lambda row: row.updated_at)
        return rows

    def approve(
        self,
        token: str,
        item_id: int,
        expected_version: int | None = None,
    ) -> Item:
        """审核通过。``expected_version`` 用于防止并发错判（REQ-003）。"""
        actor = self._actor(token)
        self._require_admin(actor)
        item = self._store.items.require(item_id)
        self._check_version(item, expected_version)
        revision = self._items.revision_of(item_id)
        now = self._clock()
        if item.status is ItemStatus.AUDITING:
            apply_status(item, ItemStatus.PUBLISHED)
            item.published_at = now
        elif revision is not None and item.status in _REVISION_HOLDERS:
            self._apply_revision(item, revision, now)
        else:
            raise Conflict(
                f"商品当前为{status_text(item.status)}，不在待审核状态")
        item.updated_at = now
        self._store.items.update(item)
        record = self._record(item, actor.user_id, AuditResult.APPROVED, "",
                              revision)
        self._journal.notify(
            item.seller_id, "AUDIT", f"商品《{item.title}》审核通过")
        self._journal.record(
            actor.user_id, "AUDIT_APPROVE", item.item_id, True,
            f"audit_id={record.audit_id}")
        self._commit()
        return item

    def reject(
        self,
        token: str,
        item_id: int,
        reason: str,
        expected_version: int | None = None,
    ) -> Item:
        """审核驳回。在线商品被驳回时保留旧信息，只丢弃待审内容。"""
        actor = self._actor(token)
        self._require_admin(actor)
        text = (reason or "").strip()
        if not text:
            raise ValidationError("驳回必须填写原因")
        item = self._store.items.require(item_id)
        self._check_version(item, expected_version)
        revision = self._items.revision_of(item_id)
        now = self._clock()
        if item.status is ItemStatus.AUDITING:
            apply_status(item, ItemStatus.DRAFT)
        elif revision is not None and item.status in _REVISION_HOLDERS:
            item.version += 1
        else:
            raise Conflict(
                f"商品当前为{status_text(item.status)}，不在待审核状态")
        if revision is not None:
            self._store.revisions.remove(revision.revision_id)
        item.updated_at = now
        self._store.items.update(item)
        record = self._record(item, actor.user_id, AuditResult.REJECTED, text,
                              revision)
        self._journal.notify(
            item.seller_id, "AUDIT", f"商品《{item.title}》审核被驳回：{text}")
        self._journal.record(
            actor.user_id, "AUDIT_REJECT", item.item_id, True,
            f"audit_id={record.audit_id}")
        self._commit()
        return item

    def history(self, token: str, item_id: int) -> list[AuditRecord]:
        """审核历史，按时间倒序。卖家只能查看本人商品（REQ-019）。"""
        actor = self._actor(token)
        item = self._store.items.require(item_id)
        if not actor.is_admin() and item.seller_id != actor.user_id:
            raise PermissionDenied("只能查看本人商品的审核历史")
        rows = self._store.audits.find(lambda row: row.item_id == item_id)
        rows.sort(key=lambda row: (row.audit_at, row.audit_id), reverse=True)
        return rows

    def _apply_revision(self, item: Item, revision: ItemRevision,
                        now: datetime) -> None:
        """把待审内容原子写入商品，并清除待审记录。"""
        item.category_id = revision.category_id
        item.title = revision.title
        item.description = revision.description
        item.price = revision.price
        item.images = list(revision.images)
        item.updated_at = now
        item.version += 1
        self._store.revisions.remove(revision.revision_id)

    @staticmethod
    def _check_version(item: Item, expected: int | None) -> None:
        if expected is not None and item.version != expected:
            raise Conflict("商品在审核期间被修改，请刷新后重新操作",
                           f"期望版本 {expected}，当前 {item.version}")

    def _record(self, item: Item, admin_id: int, result: AuditResult,
                reason: str, revision: ItemRevision | None) -> AuditRecord:
        record = AuditRecord(
            audit_id=self._store.audits.new_id(),
            item_id=item.item_id,
            admin_id=admin_id,
            result=result,
            reason=reason,
            audit_at=self._clock(),
            revision_id=None if revision is None else revision.revision_id,
        )
        self._store.audits.add(record)
        return record
