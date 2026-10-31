"""仓储层：内存表 + JSON 快照。

选型说明：课程作业的数据量在千条量级，用 JSON 文件保存整库快照足够，
且不引入第三方依赖，便于在任意机器上编译运行。表对象对外只暴露
增删改查，不暴露内部字典，避免服务层绕过校验直接改数据。

并发：交易相关的临界区由服务层加锁，这里再加一把可重入锁保护
"读快照—写快照"这个过程，保证同一进程内多线程写入不会写坏文件。
"""

from __future__ import annotations

import dataclasses
import json
import os
import threading
import types
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Generic, Iterator, TypeVar, get_args
from typing import get_origin, get_type_hints

from campustrade.errors import NotFound
from campustrade.models import AuditRecord, Category, Item, ItemRevision
from campustrade.models import Notification, OperationLog, Report, Reservation
from campustrade.models import Session, User

K = TypeVar("K")
T = TypeVar("T")

_JSON_VERSION = 1


def _hints(cls: type) -> dict[str, Any]:
    """返回类字段的类型注解，带缓存（解析字符串注解开销较大）。"""
    return get_type_hints(cls)


def _encode_value(value: Any) -> Any:
    """把字段值转成可 JSON 序列化的形式。"""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_encode_value(item) for item in value]
    return value


def _decode_value(hint: Any, raw: Any) -> Any:
    """按字段声明的类型把 JSON 值还原成领域对象。"""
    if raw is None:
        return None
    origin = get_origin(hint)
    if origin is types.UnionType:
        hint = next(arg for arg in get_args(hint) if arg is not types.NoneType)
        origin = get_origin(hint)
    result = raw
    if origin is list:
        result = [_decode_value(get_args(hint)[0], item) for item in raw]
    elif isinstance(hint, type) and issubclass(hint, Enum):
        result = hint(raw)
    elif hint is datetime:
        result = datetime.fromisoformat(raw)
    elif hint is Decimal:
        result = Decimal(raw)
    return result


def encode_entity(entity: Any) -> dict[str, Any]:
    """把实体编码成字典。"""
    return {
        field.name: _encode_value(getattr(entity, field.name))
        for field in dataclasses.fields(entity)
    }


def decode_entity(cls: type[T], raw: dict[str, Any]) -> T:
    """把字典解码成实体。"""
    hints = _hints(cls)
    values = {
        name: _decode_value(hints[name], raw.get(name))
        for name in hints
    }
    return cls(**values)


class Table(Generic[K, T]):
    """一张表：主键到实体的映射，附带自增主键分配。"""

    def __init__(self, name: str, entity: type[T]) -> None:
        self.name = name
        self._entity = entity
        self._rows: dict[K, T] = {}
        self._next_id = 1

    def new_id(self) -> int:
        """分配一个自增主键。"""
        ident = self._next_id
        self._next_id += 1
        return ident

    def add(self, row: T) -> T:
        """插入实体，主键重复视为调用方错误。"""
        key = row.ident  # type: ignore[attr-defined]
        if key in self._rows:
            raise ValueError(f"主键重复：{self.name}.{key}")
        self._rows[key] = row
        if isinstance(key, int) and key >= self._next_id:
            self._next_id = key + 1
        return row

    def get(self, ident: K) -> T | None:
        """按主键查询，不存在返回 None。"""
        return self._rows.get(ident)

    def require(self, ident: K) -> T:
        """按主键查询，不存在抛 NotFound。"""
        row = self._rows.get(ident)
        if row is None:
            raise NotFound(f"记录不存在：{self.name}[{ident}]")
        return row

    def all(self) -> list[T]:
        """返回全部记录的快照副本。"""
        return list(self._rows.values())

    def find(self, predicate: Callable[[T], bool]) -> list[T]:
        """按谓词筛选。"""
        return [row for row in self._rows.values() if predicate(row)]

    def first(self, predicate: Callable[[T], bool]) -> T | None:
        """返回第一个满足谓词的记录。"""
        for row in self._rows.values():
            if predicate(row):
                return row
        return None

    def update(self, row: T) -> T:
        """用新值替换同主键记录。"""
        key = row.ident  # type: ignore[attr-defined]
        if key not in self._rows:
            raise NotFound(f"记录不存在：{self.name}[{key}]")
        self._rows[key] = row
        return row

    def remove(self, ident: K) -> None:
        """删除记录，不存在时忽略。"""
        self._rows.pop(ident, None)

    def __iter__(self) -> Iterator[T]:
        return iter(list(self._rows.values()))

    def __len__(self) -> int:
        return len(self._rows)

    def dump(self) -> dict[str, Any]:
        """导出为 JSON 结构。"""
        return {
            "next_id": self._next_id,
            "rows": [encode_entity(row) for row in self._rows.values()],
        }

    def load(self, payload: dict[str, Any]) -> None:
        """从 JSON 结构恢复。"""
        self._rows.clear()
        self._next_id = int(payload.get("next_id", 1))
        for raw in payload.get("rows", []):
            row = decode_entity(self._entity, raw)
            self._rows[row.ident] = row  # type: ignore[attr-defined]
        if self._rows:
            numeric = [key for key in self._rows if isinstance(key, int)]
            if numeric:
                self._next_id = max(self._next_id, max(numeric) + 1)


class Store:
    """整个持久化层的门面：持有所有表，并负责落盘。"""

    def __init__(self, path: str | os.PathLike[str] | None = None) -> None:
        self._path = Path(path) if path is not None else None
        self._lock = threading.RLock()
        self.users: Table[int, User] = Table("users", User)
        self.sessions: Table[str, Session] = Table("sessions", Session)
        self.categories: Table[int, Category] = Table("categories", Category)
        self.items: Table[int, Item] = Table("items", Item)
        self.revisions: Table[int, ItemRevision] = Table(
            "revisions", ItemRevision)
        self.audits: Table[int, AuditRecord] = Table("audits", AuditRecord)
        self.reservations: Table[int, Reservation] = Table(
            "reservations", Reservation)
        self.reports: Table[int, Report] = Table("reports", Report)
        self.logs: Table[int, OperationLog] = Table("logs", OperationLog)
        self.notifications: Table[int, Notification] = Table(
            "notifications", Notification)
        self._tables: dict[str, Any] = {
            "users": self.users,
            "sessions": self.sessions,
            "categories": self.categories,
            "items": self.items,
            "revisions": self.revisions,
            "audits": self.audits,
            "reservations": self.reservations,
            "reports": self.reports,
            "logs": self.logs,
            "notifications": self.notifications,
        }
        if self._path is not None and self._path.exists():
            self.load()

    @property
    def lock(self) -> threading.RLock:
        """返回可重入锁，供服务层保护临界区。"""
        return self._lock

    def commit(self) -> None:
        """把内存状态写回磁盘。未配置文件路径时为空操作。"""
        if self._path is None:
            return
        with self._lock:
            payload = {
                "version": _JSON_VERSION,
                "tables": {
                    name: table.dump() for name, table in self._tables.items()
                },
            }
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_suffix(self._path.suffix + ".tmp")
            tmp.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(tmp, self._path)

    def load(self) -> None:
        """从磁盘读取快照。文件损坏时抛 ValueError，由调用方决定如何处理。"""
        if self._path is None or not self._path.exists():
            return
        with self._lock:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            if payload.get("version") != _JSON_VERSION:
                raise ValueError("数据文件版本不匹配")
            tables = payload.get("tables", {})
            for name, table in self._tables.items():
                if name in tables:
                    table.load(tables[name])

    def clear(self) -> None:
        """清空全部数据，主要供测试使用。"""
        with self._lock:
            for table in self._tables.values():
                table.load({"next_id": 1, "rows": []})

    def counts(self) -> dict[str, int]:
        """返回各表记录数，便于统计与自检。"""
        return {name: len(table) for name, table in self._tables.items()}
