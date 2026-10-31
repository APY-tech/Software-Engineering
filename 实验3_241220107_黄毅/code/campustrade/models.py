"""领域模型：枚举、实体与值对象。

模型只表达数据与实体自身的局部判断（例如商品是否可以公开查看），
跨实体的业务规则集中在 ``campustrade.services`` 中。每个实体都提供
``ident`` 属性，仓储层据此统一按主键存取，无需为每张表写一遍代码。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from enum import Enum

from campustrade.errors import ValidationError

# 商品价格上限，用于拦截明显的误输入（REQ-002 必填字段校验的一部分）。
MAX_PRICE = Decimal("999999.00")

# 自动完成交易的等待时长（REQ-015）。
AUTO_FINISH_DAYS = 7


class Role(str, Enum):
    """账号角色。普通用户兼具买家与卖家两种身份。"""

    USER = "USER"
    ADMIN = "ADMIN"


class AccountState(str, Enum):
    """账号状态。管理员可停用账号，停用后不能登录。"""

    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class ItemStatus(str, Enum):
    """商品状态，对应实验二状态图的 7 个状态。"""

    DRAFT = "DRAFT"
    AUDITING = "AUDITING"
    PUBLISHED = "PUBLISHED"
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    FINISHED = "FINISHED"
    OFF_SHELF = "OFF_SHELF"


class ReservationStatus(str, Enum):
    """预约记录状态。"""

    EFFECTIVE = "EFFECTIVE"
    CANCELLED = "CANCELLED"
    CONFIRMED = "CONFIRMED"
    FINISHED = "FINISHED"


class ReportState(str, Enum):
    """举报处理状态。"""

    PENDING = "PENDING"
    OFF_SHELF = "OFF_SHELF"
    REJECTED = "REJECTED"


class AuditResult(str, Enum):
    """审核结论。"""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class User:
    """用户。密码只保存派生值，不保存明文（REQ-012）。"""

    user_id: int
    student_no: str
    password_hash: str
    role: Role
    account_state: AccountState
    created_at: datetime

    @property
    def ident(self) -> int:
        """返回主键。"""
        return self.user_id

    def is_admin(self) -> bool:
        """是否为管理员。"""
        return self.role is Role.ADMIN

    def is_active(self) -> bool:
        """账号是否可用。"""
        return self.account_state is AccountState.ACTIVE


@dataclass
class Session:
    """登录会话。令牌由服务端随机生成，带过期时间。"""

    token: str
    user_id: int
    expire_at: datetime

    @property
    def ident(self) -> str:
        """返回主键（令牌本身即主键）。"""
        return self.token

    def is_valid(self, now: datetime) -> bool:
        """判断会话在给定时刻是否仍有效。"""
        return now < self.expire_at


@dataclass
class Category:
    """商品分类。分类是商品属性，因此归属商品模块（REQ-009 回改）。"""

    category_id: int
    name: str
    created_at: datetime

    @property
    def ident(self) -> int:
        """返回主键。"""
        return self.category_id


@dataclass
class Item:
    """商品。``status`` 是唯一的状态字段，写入只允许经由商品服务。"""

    item_id: int
    seller_id: int
    category_id: int
    title: str
    description: str
    price: Decimal
    images: list[str]
    status: ItemStatus
    version: int
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None
    off_shelf_reason: str = ""

    @property
    def ident(self) -> int:
        """返回主键。"""
        return self.item_id

    @property
    def has_published_version(self) -> bool:
        """是否曾经通过审核并有对外展示的版本。

        REQ-017 用该标记区分"驳回后回草稿"与"驳回后继续展示旧信息"。
        """
        return self.published_at is not None

    def is_public(self) -> bool:
        """是否出现在公开查询结果中。"""
        return self.status is ItemStatus.PUBLISHED


@dataclass
class ItemRevision:
    """已发布商品的待审修改内容（组合状态的载体，REQ-017）。"""

    revision_id: int
    item_id: int
    category_id: int
    title: str
    description: str
    price: Decimal
    images: list[str]
    submit_at: datetime

    @property
    def ident(self) -> int:
        """返回主键。"""
        return self.revision_id


@dataclass
class AuditRecord:
    """审核记录，只追加不修改（REQ-019）。"""

    audit_id: int
    item_id: int
    admin_id: int
    result: AuditResult
    reason: str
    audit_at: datetime
    revision_id: int | None = None

    @property
    def ident(self) -> int:
        """返回主键。"""
        return self.audit_id


@dataclass
class Reservation:
    """预约记录。``request_id`` 为幂等键（REQ-001）。"""

    reservation_id: int
    item_id: int
    buyer_id: int
    request_id: str
    status: ReservationStatus
    create_at: datetime
    confirm_at: datetime | None = None
    finish_at: datetime | None = None
    cancel_at: datetime | None = None
    disputed: bool = False
    dispute_note: str = ""

    @property
    def ident(self) -> int:
        """返回主键。"""
        return self.reservation_id


@dataclass
class Report:
    """举报记录。同一用户对同一商品至多一条待处理举报（REQ-010）。"""

    report_id: int
    item_id: int
    reporter_id: int
    reason_type: str
    reason_text: str
    state: ReportState
    created_at: datetime
    handler_id: int | None = None
    handled_at: datetime | None = None

    @property
    def ident(self) -> int:
        """返回主键。"""
        return self.report_id


@dataclass
class OperationLog:
    """操作日志。只追加，不提供修改与删除接口（REQ-013）。"""

    log_id: int
    operator_id: int
    action_type: str
    target_id: int
    result: bool
    detail: str
    log_at: datetime

    @property
    def ident(self) -> int:
        """返回主键。"""
        return self.log_id


@dataclass
class Notification:
    """站内通知。由审核、交易等业务动作产生。"""

    notify_id: int
    receiver_id: int
    kind: str
    content: str
    created_at: datetime
    read: bool = False

    @property
    def ident(self) -> int:
        """返回主键。"""
        return self.notify_id


@dataclass
class ItemDraft:
    """新建草稿的入参。用值对象代替一长串位置参数，避免调用方传错顺序。"""

    category_id: int
    title: str
    description: str
    price: Decimal
    images: list[str] = field(default_factory=list)


@dataclass
class ItemEdit:
    """修改商品的入参。字段为 None 表示该字段不修改。"""

    title: str | None = None
    description: str | None = None
    price: Decimal | None = None
    category_id: int | None = None
    images: list[str] | None = None


@dataclass
class ItemFilter:
    """商品查询条件（REQ-005）。空字段表示不限制该维度。"""

    keyword: str = ""
    category_id: int | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    status: ItemStatus | None = None


def normalize_price(value: object) -> Decimal:
    """把入参转成两位小数的金额，并做上下界校验。"""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"价格格式不正确：{value!r}") from exc
    if not amount.is_finite():
        raise ValidationError("价格必须是有限的数字")
    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if amount <= 0:
        raise ValidationError("价格必须大于 0")
    if amount > MAX_PRICE:
        raise ValidationError(f"价格不能超过 {MAX_PRICE}")
    return amount
