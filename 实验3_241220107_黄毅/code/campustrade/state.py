"""商品状态机。

实验二状态图里的每一条箭头在这里有且只有一处实现，服务层改状态前
先调用 ``ensure_transition``。好处是"已预约不能下架""已完成不能重复
确认"这类规则不依赖调用顺序，任何人都无法绕过。

允许的迁移（与实验二状态图一致）::

    DRAFT      -> AUDITING
    AUDITING   -> PUBLISHED | DRAFT      （通过 / 驳回且无对外版本）
    PUBLISHED  -> RESERVED | OFF_SHELF
    RESERVED   -> CONFIRMED | PUBLISHED  （确认 / 卖家取消预约）
    CONFIRMED  -> FINISHED
    OFF_SHELF  -> PUBLISHED              （管理员解除，卖家不可自行恢复）
    FINISHED   -> 终态
"""

from __future__ import annotations

from campustrade.errors import Conflict, ValidationError
from campustrade.models import AuditResult, Item, ItemStatus
from campustrade.models import ReportState, ReservationStatus

_TRANSITIONS: dict[ItemStatus, frozenset[ItemStatus]] = {
    ItemStatus.DRAFT: frozenset({ItemStatus.AUDITING}),
    ItemStatus.AUDITING: frozenset({ItemStatus.PUBLISHED, ItemStatus.DRAFT}),
    ItemStatus.PUBLISHED: frozenset({ItemStatus.RESERVED,
                                     ItemStatus.OFF_SHELF}),
    ItemStatus.RESERVED: frozenset({ItemStatus.CONFIRMED,
                                    ItemStatus.PUBLISHED}),
    ItemStatus.CONFIRMED: frozenset({ItemStatus.FINISHED}),
    ItemStatus.FINISHED: frozenset(),
    ItemStatus.OFF_SHELF: frozenset({ItemStatus.PUBLISHED}),
}

_STATUS_ALIASES = {
    "草稿": ItemStatus.DRAFT,
    "待审核": ItemStatus.AUDITING,
    "已发布": ItemStatus.PUBLISHED,
    "已预约": ItemStatus.RESERVED,
    "已确认": ItemStatus.CONFIRMED,
    "已完成": ItemStatus.FINISHED,
    "已下架": ItemStatus.OFF_SHELF,
}


def can_transition(current: ItemStatus, target: ItemStatus) -> bool:
    """判断两个状态之间是否允许迁移。"""
    return target in _TRANSITIONS[current]


def ensure_transition(item: Item, target: ItemStatus) -> None:
    """确认迁移合法，否则抛 Conflict 并说明当前状态。"""
    if not can_transition(item.status, target):
        raise Conflict(
            f"商品 {item.item_id} 当前为{status_text(item.status)}，"
            f"不能变更为{status_text(target)}",
            f"version={item.version}",
        )


def apply_status(item: Item, target: ItemStatus) -> None:
    """校验并写入新状态，同时递增版本号（乐观锁）。"""
    ensure_transition(item, target)
    item.status = target
    item.version += 1


def parse_status(text: str) -> ItemStatus:
    """把用户输入的状态名解析成枚举，非法值抛 ValidationError。"""
    raw = (text or "").strip()
    if not raw:
        raise ValidationError("状态不能为空")
    if raw in _STATUS_ALIASES:
        return _STATUS_ALIASES[raw]
    try:
        return ItemStatus(raw.upper())
    except ValueError as exc:
        raise ValidationError(f"无效的商品状态：{text}") from exc


_RESERVATION_ALIASES = {
    ReservationStatus.EFFECTIVE: "有效",
    ReservationStatus.CANCELLED: "已取消",
    ReservationStatus.CONFIRMED: "已确认",
    ReservationStatus.FINISHED: "已完成",
}

_REPORT_ALIASES = {
    ReportState.PENDING: "待处理",
    ReportState.OFF_SHELF: "已下架",
    ReportState.REJECTED: "已驳回",
}

_AUDIT_ALIASES = {
    AuditResult.APPROVED: "通过",
    AuditResult.REJECTED: "驳回",
}


def reservation_status_text(status: ReservationStatus) -> str:
    """返回预约状态的中文名。"""
    return _RESERVATION_ALIASES.get(status, status.value)


def report_state_text(state: ReportState) -> str:
    """返回举报状态的中文名。"""
    return _REPORT_ALIASES.get(state, state.value)


def audit_result_text(result: AuditResult) -> str:
    """返回审核结论的中文名。"""
    return _AUDIT_ALIASES.get(result, result.value)


def status_text(status: ItemStatus) -> str:
    """返回状态的中文名，用于提示与列表展示。"""
    for name, value in _STATUS_ALIASES.items():
        if value is status:
            return name
    return status.value
