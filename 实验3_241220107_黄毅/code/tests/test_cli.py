"""命令行界面冒烟测试：用脚本化输入跑一遍主流程。

夹具中有几个只负责铺数据、不会出现在断言里，故关闭 unused-argument。
"""

# pylint: disable=unused-argument

# 用例名即文档：此处不对每个 test_ 函数再写 docstring。
# pylint: disable=missing-function-docstring

from __future__ import annotations

from campustrade.cli.shell import Shell


def _run(app, answers: list[str]) -> list[str]:
    lines: list[str] = []
    queue = list(answers)

    def fake_input(prompt: str) -> str:
        lines.append(prompt)
        if not queue:
            raise EOFError
        return queue.pop(0)

    Shell(app, input_fn=fake_input, output_fn=lines.append).run()
    return lines


def test_login_search_and_logout(app, data):
    lines = _run(app, [
        "2", "241220101", "Campus#2026",   # 登录
        "1", "概率", "", "", "", "", "",     # 搜索
        "0",                                # 退出登录
        "0",                                # 退出程序
    ])
    text = "\n".join(lines)
    assert "登录成功" in text
    assert "命中" in text


def test_guest_can_browse(app, data, listed):
    lines = _run(app, ["3", "0"])
    text = "\n".join(lines)
    assert "概率论与数理统计" in text


def test_invalid_choice_is_reported(app, data):
    lines = _run(app, ["9", "0"])
    assert any("无效的选项" in line for line in lines)


def test_reserve_via_menu(app, data, listed):
    lines = _run(app, [
        "2", "241220102", "Campus#2026",
        "3", str(listed.item_id), "req-cli-1",
        "0", "0",
    ])
    text = "\n".join(lines)
    assert "预约成功" in text
    assert app.store.reservations.first(
        lambda row: row.item_id == listed.item_id) is not None


def test_admin_sees_audit_menu(app, data):
    lines = _run(app, ["2", "900000001", "Campus#2026", "21", "0", "0"])
    text = "\n".join(lines)
    assert "待审核商品" in text
    assert "管理员" in text
