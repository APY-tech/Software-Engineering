"""账户与会话相关用例（REQ-004 / REQ-012 / REQ-016）。"""

# 用例名即文档：此处不对每个 test_ 函数再写 docstring。
# pylint: disable=missing-function-docstring

from __future__ import annotations

import pytest

from campustrade.context import build_application
from campustrade.errors import AuthError, Conflict, PermissionDenied
from campustrade.errors import SessionExpired, ValidationError
from campustrade.security import hash_password, verify_password


def test_register_then_login(app):
    user = app.auth.register("241220301", "Campus#2026")
    token = app.auth.login("241220301", "Campus#2026")
    assert app.auth.authenticate(token).user_id == user.user_id
    assert user.role.value == "USER"


def test_password_is_hashed(app):
    app.auth.register("241220302", "Campus#2026")
    stored = app.store.users.first(
        lambda row: row.student_no == "241220302")
    assert "Campus#2026" not in stored.password_hash
    assert stored.password_hash.startswith("pbkdf2_sha256$")


def test_duplicate_student_no_rejected(app):
    app.auth.register("241220303", "Campus#2026")
    with pytest.raises(Conflict):
        app.auth.register("241220303", "Another#2026")


def test_weak_password_rejected(app):
    with pytest.raises(ValidationError):
        app.auth.register("241220304", "1234567")


def test_bad_student_no_rejected(app):
    with pytest.raises(ValidationError):
        app.auth.register("abc123", "Campus#2026")


def test_wrong_password_rejected(app):
    app.auth.register("241220305", "Campus#2026")
    with pytest.raises(AuthError):
        app.auth.login("241220305", "wrong-password")


def test_session_expires():
    app = build_application(None, session_ttl_minutes=0)
    app.auth.register("241220306", "Campus#2026")
    token = app.auth.login("241220306", "Campus#2026")
    with pytest.raises(SessionExpired):
        app.auth.authenticate(token)


def test_logout_invalidates_token(app, data):
    app.auth.logout(data.buyer_token)
    with pytest.raises(AuthError):
        app.auth.authenticate(data.buyer_token)


def test_only_admin_can_create_admin(app, data):
    with pytest.raises(PermissionDenied):
        app.auth.create_admin(data.buyer_token, "241220307", "Campus#2026")
    created = app.auth.create_admin(data.admin_token, "241220307",
                                    "Campus#2026")
    assert created.is_admin()


def test_disabled_account_cannot_login(app, data):
    user = app.auth.get_user(app.auth.authenticate(data.other_token).user_id)
    user.account_state = user.account_state.__class__.DISABLED
    app.store.users.update(user)
    with pytest.raises(AuthError):
        app.auth.login("241220103", "Campus#2026")


def test_change_password(app, data):
    app.auth.change_password(data.buyer_token, "Campus#2026", "NewPass#2026")
    with pytest.raises(AuthError):
        app.auth.login("241220102", "Campus#2026")
    token = app.auth.login("241220102", "NewPass#2026")
    assert app.auth.authenticate(token).student_no == "241220102"


def test_hash_roundtrip():
    stored = hash_password("Campus#2026")
    assert verify_password("Campus#2026", stored)
    assert not verify_password("campus#2026", stored)
    assert not verify_password("Campus#2026", "broken")
