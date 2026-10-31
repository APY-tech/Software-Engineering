"""用户注册、登录与会话管理（REQ-004 / REQ-012 / REQ-016）。

会话令牌保存在服务端表里，客户端只拿到令牌。所有需要登录的操作都
走 ``authenticate``，过期与停用在这里统一拦截，业务服务不再各写一遍。
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from campustrade.errors import AuthError, Conflict, PermissionDenied
from campustrade.errors import SessionExpired, ValidationError
from campustrade.models import AccountState, Role, Session, User
from campustrade.security import hash_password, new_token, verify_password
from campustrade.services.journal import JournalService
from campustrade.storage import Store

_STUDENT_NO_PATTERN = re.compile(r"^\d{8,12}$")
_MIN_PASSWORD_LENGTH = 8
_MAX_PASSWORD_LENGTH = 64
_DEFAULT_TTL_MINUTES = 120


class AuthService:
    """账号与登录态。"""

    def __init__(
        self,
        store: Store,
        journal: JournalService,
        ttl_minutes: int = _DEFAULT_TTL_MINUTES,
    ) -> None:
        self._store = store
        self._journal = journal
        self._ttl = timedelta(minutes=ttl_minutes)
        self._clock = datetime.now

    def register(self, student_no: str, password: str) -> User:
        """用学号注册普通用户。普通用户同时具备买家与卖家身份。"""
        self._validate(student_no, password)
        if self._find_by_student_no(student_no) is not None:
            raise Conflict(f"学号 {student_no} 已被注册")
        user = self._create(student_no, password, Role.USER)
        self._journal.record(
            user.user_id, "REGISTER", user.user_id, True, f"注册 {student_no}")
        self._store.commit()
        return user

    def create_admin(self, token: str, student_no: str, password: str) -> User:
        """由现有管理员分配一个新的管理员账号。"""
        actor = self.authenticate(token)
        if not actor.is_admin():
            raise PermissionDenied("只有管理员可以分配管理员账号")
        self._validate(student_no, password)
        if self._find_by_student_no(student_no) is not None:
            raise Conflict(f"学号 {student_no} 已被注册")
        user = self._create(student_no, password, Role.ADMIN)
        self._journal.record(
            actor.user_id, "CREATE_ADMIN", user.user_id, True,
            f"新增管理员 {student_no}")
        self._store.commit()
        return user

    def bootstrap_admin(self, student_no: str, password: str) -> User:
        """首次部署时创建管理员；已存在同号账号时直接返回该账号。"""
        existing = self._find_by_student_no(student_no)
        if existing is not None:
            return existing
        self._validate(student_no, password)
        user = self._create(student_no, password, Role.ADMIN)
        self._journal.record(
            user.user_id, "BOOTSTRAP_ADMIN", user.user_id, True, "初始化管理员")
        self._store.commit()
        return user

    def login(self, student_no: str, password: str) -> str:
        """校验口令并创建会话，返回令牌。"""
        user = self._find_by_student_no(student_no)
        if user is None or not verify_password(password, user.password_hash):
            self._journal.record(0, "LOGIN", 0, False, f"学号 {student_no} 登录失败")
            self._store.commit()
            raise AuthError("学号或密码错误")
        if not user.is_active():
            self._journal.record(
                user.user_id, "LOGIN", user.user_id, False, "账号已停用")
            self._store.commit()
            raise AuthError("账号已停用，请联系管理员")
        now = self._clock()
        session = Session(
            token=new_token(),
            user_id=user.user_id,
            expire_at=now + self._ttl,
        )
        self._store.sessions.add(session)
        self._journal.record(user.user_id, "LOGIN", user.user_id, True, "登录成功")
        self._store.commit()
        return session.token

    def logout(self, token: str) -> None:
        """注销会话。重复注销不报错。"""
        session = self._store.sessions.get(token)
        if session is None:
            return
        self._store.sessions.remove(token)
        self._journal.record(
            session.user_id, "LOGOUT", session.user_id, True, "退出登录")
        self._store.commit()

    def authenticate(self, token: str) -> User:
        """把令牌换成当前用户，令牌缺失、过期或账号停用都抛异常。"""
        if not token:
            raise AuthError("该操作需要登录后执行")
        session = self._store.sessions.get(token)
        if session is None:
            raise AuthError("登录状态无效，请重新登录")
        if not session.is_valid(self._clock()):
            self._store.sessions.remove(token)
            raise SessionExpired("登录已过期，请重新登录")
        user = self._store.users.require(session.user_id)
        if not user.is_active():
            raise AuthError("账号已停用，请联系管理员")
        return user

    def change_password(self, token: str, old: str, new: str) -> None:
        """修改本人密码。"""
        user = self.authenticate(token)
        if not verify_password(old, user.password_hash):
            raise AuthError("原密码不正确")
        self._validate_password(new)
        if old == new:
            raise ValidationError("新密码不能与原密码相同")
        user.password_hash = hash_password(new)
        self._store.users.update(user)
        self._journal.record(
            user.user_id, "CHANGE_PASSWORD", user.user_id, True, "修改密码")
        self._store.commit()

    def get_user(self, user_id: int) -> User:
        """按主键取用户。"""
        return self._store.users.require(user_id)

    def _create(self, student_no: str, password: str, role: Role) -> User:
        user = User(
            user_id=self._store.users.new_id(),
            student_no=student_no,
            password_hash=hash_password(password),
            role=role,
            account_state=AccountState.ACTIVE,
            created_at=self._clock(),
        )
        self._store.users.add(user)
        return user

    def _find_by_student_no(self, student_no: str) -> User | None:
        return self._store.users.first(
            lambda row: row.student_no == student_no)

    def _validate(self, student_no: str, password: str) -> None:
        if not _STUDENT_NO_PATTERN.match(student_no):
            raise ValidationError("学号应为 8~12 位数字")
        self._validate_password(password)

    @staticmethod
    def _validate_password(password: str) -> None:
        if len(password) < _MIN_PASSWORD_LENGTH:
            raise ValidationError(
                f"密码长度不能少于 {_MIN_PASSWORD_LENGTH} 位")
        if len(password) > _MAX_PASSWORD_LENGTH:
            raise ValidationError(
                f"密码长度不能超过 {_MAX_PASSWORD_LENGTH} 位")
        if password.strip() != password:
            raise ValidationError("密码首尾不能有空格")
