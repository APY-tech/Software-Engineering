"""业务异常定义。

系统内部所有"可预期的失败"（入参非法、越权、状态冲突等）都以本模块的
异常表达，由命令行层统一捕获并翻译成人能读懂的提示。这样服务层不需要
返回错误码，也不需要 print，便于单元测试直接断言异常类型。
"""

from __future__ import annotations


class DomainError(Exception):
    """所有业务异常的基类。

    Attributes:
        code: 稳定的错误码，供界面层与测试选择提示语。
        detail: 便于定位问题的补充说明，可留空。
    """

    code = "DOMAIN_ERROR"

    def __init__(self, message: str, detail: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def __str__(self) -> str:
        if self.detail:
            return f"{self.message}（{self.detail}）"
        return self.message


class ValidationError(DomainError):
    """入参不合法，例如价格非正数、必填字段为空。"""

    code = "VALIDATION_ERROR"


class AuthError(DomainError):
    """未登录、会话过期或账号密码错误。"""

    code = "AUTH_ERROR"


class SessionExpired(AuthError):
    """会话已过期，需要重新登录。"""

    code = "SESSION_EXPIRED"


class PermissionDenied(DomainError):
    """已登录但不具备该操作的权限（角色或资源归属不符）。"""

    code = "PERMISSION_DENIED"


class NotFound(DomainError):
    """按主键查询的目标不存在。"""

    code = "NOT_FOUND"


class Conflict(DomainError):
    """与当前业务状态冲突，例如对已预约商品重复预约。"""

    code = "CONFLICT"
