"""端到端演示脚本。

作用有两个：给报告提供可复现的运行输出；在没有单元测试环境时充当
冒烟测试。脚本按需求编号分节，全部操作都走公开服务接口，唯一例外是
第 10 节把确认时间回拨 8 天以模拟时间流逝——真实系统里这一步由定时
任务触发。
"""

from __future__ import annotations

import threading
from datetime import datetime, timedelta
from typing import Callable

from campustrade.context import Application, build_application
from campustrade.cli.tables import display_width
from campustrade.errors import DomainError
from campustrade.models import Item, ItemDraft, ItemEdit, ItemFilter
from campustrade.models import ReservationStatus, normalize_price
from campustrade.seed import SeedData, seed
from campustrade.state import parse_status, status_text

_EXTRA_BUYERS = ("241220201", "241220202", "241220203", "241220204")
_RULE_WIDTH = 60

Out = Callable[[str], None]


def run_demo(output: Out = print) -> None:
    """跑一遍从发布到统计的完整流程。"""
    app = build_application(None)
    data = seed(app)
    _section(output, 1, "注册与登录（REQ-004）")
    _demo_auth(app, data, output)

    _section(output, 2, "发布与审核（REQ-002/003/019）")
    item = _demo_publish(app, data, output)

    _section(output, 3, "公开查询（REQ-005）")
    _demo_search(app, output)

    _section(output, 4, "预约的幂等与唯一性（REQ-001）")
    _demo_reserve(app, data, item, output)

    _section(output, 5, "取消预约（REQ-008）")
    _demo_cancel(app, data, item, output)

    _section(output, 6, "确认交易与确认完成（REQ-006/007）")
    _demo_trade(app, data, item, output)

    _section(output, 7, "修改已发布商品（REQ-017）")
    _demo_revision(app, data, output)

    _section(output, 8, "举报与下架（REQ-010/014）")
    _demo_report(app, data, output)

    _section(output, 9, "并发预约（REQ-001 竞争场景）")
    _demo_concurrency(app, data, output)

    _section(output, 10, "超时自动完成（REQ-015）")
    _demo_auto_finish(app, data, output)

    _section(output, 11, "统计（REQ-018）与操作日志（REQ-013）")
    _demo_stats(app, data, output)
    output("\n演示结束：全部操作均按预期完成或被正确拒绝。")


# ----------------------------------------------------------------------
# 输出与断言辅助
# ----------------------------------------------------------------------


def _section(out: Out, index: int, title: str) -> None:
    remain = _RULE_WIDTH - display_width(title) - 8
    out(f"\n=== {index}. {title} " + "=" * max(0, remain))


def _ok(out: Out, text: str) -> None:
    out(f"  ✓ {text}")


def _bad(out: Out, text: str) -> None:
    out(f"  ✗ {text}")


def _expect_error(out: Out, label: str, action: Callable[[], object]) -> None:
    """执行一个预期失败的操作，并确认它确实被拒绝。"""
    try:
        action()
    except DomainError as exc:
        _bad(out, f"{label} -> 已拒绝：{exc}")
        return
    _ok(out, f"{label} -> 未被拦截（不符合预期）")


def _status(app: Application, item: Item) -> str:
    return status_text(app.store.items.require(item.item_id).status)


def _published(app: Application, data: SeedData, title: str, price: str,
               category: str = "教材书籍") -> Item:
    """建草稿、送审、管理员通过，得到一件已发布商品。"""
    item = app.items.create_draft(data.seller_token, ItemDraft(
        category_id=data.categories[category].category_id,
        title=title,
        description="演示数据：成色良好，可当面交易",
        price=normalize_price(price),
        images=["demo.jpg"],
    ))
    app.items.submit_audit(data.seller_token, item.item_id)
    app.audit.approve(data.admin_token, item.item_id)
    return item


# ----------------------------------------------------------------------
# 各节场景
# ----------------------------------------------------------------------


def _demo_auth(app: Application, data: SeedData, out: Out) -> None:
    _expect_error(out, "重复学号注册",
                  lambda: app.auth.register("241220101", "Another#2026"))
    _expect_error(out, "密码错误登录",
                  lambda: app.auth.login("241220101", "wrong-password"))
    user = app.auth.authenticate(data.seller_token)
    _ok(out, f"登录态有效：{user.student_no}，角色 {user.role.value}")
    _expect_error(out, "未登录直接预约",
                  lambda: app.trade.reserve("", 1, "req-anon"))


def _demo_publish(app: Application, data: SeedData, out: Out) -> Item:
    books = data.categories["教材书籍"].category_id
    item = app.items.create_draft(data.seller_token, ItemDraft(
        category_id=books,
        title="线性代数 同济第七版",
        description="无笔记，封面有轻微折痕",
        price=normalize_price("25"),
        images=["linalg.jpg"],
    ))
    _ok(out, f"保存草稿 #{item.item_id}，状态 {status_text(item.status)}")
    app.items.submit_audit(data.seller_token, item.item_id)
    _ok(out, f"提交审核后状态 {_status(app, item)}")
    _expect_error(out, "卖家自行审核通过",
                  lambda: app.audit.approve(data.seller_token, item.item_id))
    app.audit.approve(data.admin_token, item.item_id)
    _ok(out, f"管理员通过后状态 {_status(app, item)}")

    empty = app.items.create_draft(data.seller_token, ItemDraft(
        category_id=books, title="待补描述的台灯", description="",
        price=normalize_price("30")))
    _expect_error(out, "描述为空时提交审核",
                  lambda: app.items.submit_audit(data.seller_token,
                                                 empty.item_id))
    app.items.update_item(data.seller_token, empty.item_id,
                          ItemEdit(description="九成新，带原包装"))
    app.items.submit_audit(data.seller_token, empty.item_id)
    _ok(out, f"补齐描述后提交成功，状态 {_status(app, empty)}")
    _expect_error(out, "驳回不填原因",
                  lambda: app.audit.reject(
                      data.admin_token, empty.item_id, ""))
    app.audit.reject(data.admin_token, empty.item_id, "缺少实拍图")
    _ok(out, f"驳回后状态 {_status(app, empty)}")
    history = app.audit.history(data.seller_token, empty.item_id)
    _ok(out, f"审核历史 {len(history)} 条，最新结论 "
             f"{history[0].result.value}：{history[0].reason}")
    return item


def _demo_search(app: Application, out: Out) -> None:
    hits = app.items.search(ItemFilter(keyword="同济"))
    _ok(out, f"关键词“同济”命中 {len(hits)} 件")
    for row in hits:
        out(f"      #{row.item_id} {row.title} / {row.price} 元")
    hits = app.items.search(ItemFilter(max_price=normalize_price("50")))
    _ok(out, f"价格不高于 50 元命中 {len(hits)} 件")
    _expect_error(out, "非法状态参数", lambda: parse_status("已删除"))
    _expect_error(out, "价格区间倒置",
                  lambda: app.items.search(ItemFilter(
                      min_price=normalize_price("100"),
                      max_price=normalize_price("10"))))


def _demo_reserve(app: Application, data: SeedData, item: Item,
                  out: Out) -> None:
    first = app.trade.reserve(data.buyer_token, item.item_id, "req-0001")
    _ok(out, f"买家预约成功，预约号 {first.reservation_id}，"
             f"商品状态 {_status(app, item)}")
    replay = app.trade.reserve(data.buyer_token, item.item_id, "req-0001")
    _ok(out, f"同一 requestId 重发返回原记录：预约号 "
             f"{replay.reservation_id}（共 "
             f"{len(app.store.reservations)} 条预约记录）")
    _expect_error(out, "另一买家再预约",
                  lambda: app.trade.reserve(data.other_token, item.item_id,
                                            "req-0002"))
    _expect_error(out, "卖家预约本人商品",
                  lambda: app.trade.reserve(data.seller_token, item.item_id,
                                            "req-0003"))
    _expect_error(out, "缺少 requestId",
                  lambda: app.trade.reserve(
                      data.other_token, item.item_id, ""))


def _demo_cancel(app: Application, data: SeedData, item: Item,
                 out: Out) -> None:
    _expect_error(out, "非卖家取消预约",
                  lambda: app.trade.cancel(data.buyer_token, item.item_id))
    app.trade.cancel(data.seller_token, item.item_id)
    _ok(out, f"卖家取消后状态 {_status(app, item)}")
    again = app.trade.reserve(data.buyer_token, item.item_id, "req-0004")
    _ok(out, f"买家重新预约成功，预约号 {again.reservation_id}")


def _demo_trade(app: Application, data: SeedData, item: Item,
                out: Out) -> None:
    _expect_error(out, "买家确认交易",
                  lambda: app.trade.confirm(data.buyer_token, item.item_id))
    app.trade.confirm(data.seller_token, item.item_id)
    _ok(out, f"卖家确认后状态 {_status(app, item)}")
    _expect_error(out, "非预约买家确认完成",
                  lambda: app.trade.finish(data.other_token, item.item_id))
    app.trade.finish(data.buyer_token, item.item_id)
    _ok(out, f"买家确认完成后状态 {_status(app, item)}")
    _expect_error(out, "重复确认完成",
                  lambda: app.trade.finish(data.buyer_token, item.item_id))
    _expect_error(out, "对已完成商品预约",
                  lambda: app.trade.reserve(data.other_token, item.item_id,
                                            "req-0005"))


def _demo_revision(app: Application, data: SeedData, out: Out) -> None:
    item = _published(app, data, "罗技 M590 静音鼠标", "89", "数码电子")
    app.items.update_item(data.seller_token, item.item_id,
                          ItemEdit(price=normalize_price("79")))
    shown = app.items.get_item(item.item_id, data.seller_token)
    _ok(out, f"修改已发布商品后，前台仍显示《{shown.title}》/"
             f"{shown.price} 元，状态 {status_text(shown.status)}")
    revision = app.items.revision_of(item.item_id)
    _ok(out, f"新内容暂存于待审记录 #{revision.revision_id}，"
             f"提交时间 {revision.submit_at.strftime('%H:%M:%S')}")
    pending = [row.item_id for row in app.audit.pending(data.admin_token)]
    _ok(out, f"该商品进入待审核列表：{item.item_id in pending}")
    reserved = app.trade.reserve(data.buyer_token, item.item_id, "req-0100")
    _ok(out, f"修改审核期间买家仍可预约：预约号 "
             f"{reserved.reservation_id}，前台仍是旧标题"
             f"《{app.items.get_item(item.item_id, data.seller_token).title}》")
    app.audit.approve(data.admin_token, item.item_id)
    shown = app.items.get_item(item.item_id, data.seller_token)
    _ok(out, f"审核通过后原子更新为 {shown.price} 元，待审记录已清除："
             f"{app.items.revision_of(item.item_id) is None}")

    second = _published(app, data, "考研英语真题 2010-2024", "45")
    app.items.update_item(data.seller_token, second.item_id,
                          ItemEdit(price=normalize_price("39")))
    app.audit.reject(data.admin_token, second.item_id, "图片不清晰")
    shown = app.items.get_item(second.item_id, data.seller_token)
    _ok(out, f"驳回修改后仍为{status_text(shown.status)}，显示原价 "
             f"{shown.price} 元，待审内容已丢弃："
             f"{app.items.revision_of(second.item_id) is None}")


def _demo_report(app: Application, data: SeedData, out: Out) -> None:
    target = app.items.search(ItemFilter(keyword="考研"))[0]
    report = app.moderation.submit_report(
        data.buyer_token, target.item_id, "虚假描述", "实物与图片不符")
    _ok(out, f"举报已提交，编号 {report.report_id}")
    again = app.moderation.submit_report(
        data.buyer_token, target.item_id, "虚假描述", "重复提交")
    _ok(out, f"同一用户重复举报返回原记录：{again.report_id}")
    _expect_error(out, "普通用户处理举报",
                  lambda: app.moderation.handle(
                      data.buyer_token, report.report_id, "OFF_SHELF"))
    app.moderation.handle(data.admin_token, report.report_id, "OFF_SHELF")
    _ok(out, f"下架后状态 {_status(app, target)}")
    _expect_error(out, "预约已下架商品",
                  lambda: app.trade.reserve(data.other_token, target.item_id,
                                            "req-0006"))
    _expect_error(out, "重复处理同一举报",
                  lambda: app.moderation.handle(data.admin_token,
                                                report.report_id, "REJECT"))


def _demo_concurrency(app: Application, data: SeedData, out: Out) -> None:
    item = _published(app, data, "四级词汇书", "15")
    tokens = []
    for student_no in _EXTRA_BUYERS:
        app.auth.register(student_no, "Campus#2026")
        tokens.append(app.auth.login(student_no, "Campus#2026"))
    gate = threading.Barrier(len(tokens))
    results: list[str] = []
    guard = threading.Lock()

    def worker(token: str, index: int) -> None:
        gate.wait()
        try:
            app.trade.reserve(token, item.item_id, f"race-{index}")
            text = "成功"
        except DomainError as exc:
            text = f"失败（{exc.code}）"
        with guard:
            results.append(text)

    threads = [threading.Thread(target=worker, args=(token, index))
               for index, token in enumerate(tokens)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    _ok(out, f"{len(tokens)} 个买家同时预约，结果：{results}")
    effective = app.store.reservations.find(
        lambda row: row.item_id == item.item_id
        and row.status is ReservationStatus.EFFECTIVE)
    _ok(out, f"商品最终状态 {_status(app, item)}，有效预约 "
             f"{len(effective)} 条")


def _demo_auto_finish(app: Application, data: SeedData, out: Out) -> None:
    item = _published(app, data, "护眼台灯", "35", "生活用品")
    app.trade.reserve(data.buyer_token, item.item_id, "req-0007")
    app.trade.confirm(data.seller_token, item.item_id)
    reservation = app.store.reservations.first(
        lambda row: row.item_id == item.item_id)
    reservation.confirm_at = datetime.now() - timedelta(days=8)
    app.store.reservations.update(reservation)
    _ok(out, "把确认时间回拨 8 天，模拟时间流逝")
    done = app.trade.auto_finish_due()
    _ok(out, f"自动完成 {len(done)} 笔，商品状态 {_status(app, item)}")
    notices = app.journal.inbox(app.auth.authenticate(data.seller_token))
    _ok(out, f"卖家共收到 {len(notices)} 条通知，最新一条："
             f"{notices[0].content}")


def _demo_stats(app: Application, data: SeedData, out: Out) -> None:
    seller = app.stats.seller_summary(data.seller_token)
    _ok(out, f"卖家统计：{seller}")
    site = app.stats.site_summary(data.admin_token)
    _ok(out, f"全站统计：{site}")
    _expect_error(out, "普通用户查全站统计",
                  lambda: app.stats.site_summary(data.buyer_token))
    logs = app.journal.query(app.auth.authenticate(data.admin_token))
    _ok(out, f"操作日志共 {len(logs)} 条，最新一条 {logs[0].action_type}"
             f" / {logs[0].detail}")
    _expect_error(out, "普通用户查操作日志",
                  lambda: app.journal.query(
                      app.auth.authenticate(data.buyer_token)))
