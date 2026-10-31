"""命令行界面。

界面层只做三件事：收集输入、调用服务、把结果排版。任何业务判断都
不写在这里——服务抛出的 ``DomainError`` 统一在最外层捕获并打印，
所以新增一条业务规则只需要改服务层。
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Callable

from campustrade import Application
from campustrade.cli.tables import pad, render_table, rule
from campustrade.errors import DomainError, ValidationError
from campustrade.models import Item, ItemDraft, ItemEdit, ItemFilter
from campustrade.models import ItemStatus, Reservation, normalize_price
from campustrade.services.moderation import ACTION_OFF_SHELF, ACTION_REJECT
from campustrade.state import audit_result_text, parse_status
from campustrade.state import report_state_text, reservation_status_text
from campustrade.state import status_text

Handler = Callable[[], None]
_WIDE = 66


class Shell:
    """交互式控制台。"""

    def __init__(
        self,
        app: Application,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self._app = app
        self._input = input_fn
        self._print = output_fn
        self._token = ""
        self._running = True

    # ------------------------------------------------------------------
    # 主循环
    # ------------------------------------------------------------------

    def run(self) -> None:
        """启动主循环，Ctrl-C 或输入流结束时正常退出。"""
        self._banner()
        self._warn_auto_finished()
        try:
            while self._running:
                self._step()
        except (EOFError, KeyboardInterrupt):
            self._print("\n再见。")

    def _step(self) -> None:
        commands = self._commands()
        self._print_menu(commands)
        key = self._ask("请选择")
        handler = dict((item[0], item[2]) for item in commands).get(key)
        if handler is None:
            self._print("  无效的选项。")
            return
        try:
            handler()
        except DomainError as exc:
            self._print(f"  ✗ {exc}")

    def _banner(self) -> None:
        self._print(rule("=", _WIDE))
        self._print(pad("  校园二手交易系统 · 命令行版", _WIDE, "center"))
        self._print(rule("=", _WIDE))

    def _warn_auto_finished(self) -> None:
        done = self._app.trade.auto_finish_due()
        if done:
            self._print(f"  [系统] 有 {len(done)} 笔交易因超时自动完成")

    def _print_menu(self, commands: list[tuple[str, str, Handler]]) -> None:
        actor = self._current_user()
        who = "未登录（可匿名浏览）"
        if actor is not None:
            role = "管理员" if actor.is_admin() else "买家/卖家"
            who = f"{actor.student_no}（{role}）"
        self._print("")
        self._print(rule("-", _WIDE))
        self._print(f"  当前身份：{who}")
        self._print(rule("-", _WIDE))
        line = ""
        for index, (key, label, _) in enumerate(commands, start=1):
            line += pad(f"{key}. {label}", 22)
            if index % 3 == 0:
                self._print("  " + line.rstrip())
                line = ""
        if line:
            self._print("  " + line.rstrip())

    def _commands(self) -> list[tuple[str, str, Handler]]:
        actor = self._current_user()
        if actor is None:
            return [
                ("1", "注册", self._register),
                ("2", "登录", self._login),
                ("3", "浏览商品", self._browse),
                ("0", "退出程序", self._quit),
            ]
        common = [
            ("1", "搜索商品", self._search),
            ("2", "商品详情", self._detail),
            ("3", "预约商品", self._reserve),
            ("4", "我的预约", self._my_reservations),
            ("5", "取消预约", self._cancel),
            ("6", "确认交易", self._confirm),
            ("7", "确认完成", self._finish),
            ("8", "发布商品", self._publish),
            ("9", "我的商品", self._my_items),
            ("10", "修改商品", self._modify),
            ("11", "提交审核", self._submit),
            ("12", "下架商品", self._off_shelf),
            ("13", "举报商品", self._report),
            ("14", "我的通知", self._notifications),
            ("15", "我的统计", self._my_stats),
            ("0", "退出登录", self._logout),
        ]
        if not actor.is_admin():
            return common
        admin = [
            ("21", "待审核商品", self._pending),
            ("22", "审核通过", self._approve),
            ("23", "审核驳回", self._reject),
            ("24", "审核历史", self._audit_history),
            ("25", "待处理举报", self._pending_reports),
            ("26", "处理举报", self._handle_report),
            ("27", "全站统计", self._site_stats),
            ("28", "操作日志", self._logs),
            ("29", "分类管理", self._categories),
            ("30", "恢复下架", self._restore),
        ]
        return common + admin

    def _current_user(self):
        if not self._token:
            return None
        try:
            return self._app.auth.authenticate(self._token)
        except DomainError:
            self._token = ""
            return None

    # ------------------------------------------------------------------
    # 输入辅助
    # ------------------------------------------------------------------

    def _ask(self, label: str) -> str:
        return self._input(f"  {label}：").strip()

    def _ask_int(self, label: str) -> int:
        raw = self._ask(label)
        try:
            return int(raw)
        except ValueError as exc:
            raise ValidationError(f"请输入数字，收到 {raw!r}") from exc

    def _ask_price(self, label: str) -> Decimal | None:
        raw = self._ask(label)
        return normalize_price(raw) if raw else None

    def _ask_datetime(self, label: str) -> datetime | None:
        raw = self._ask(f"{label}（YYYY-MM-DD，留空不限）")
        if not raw:
            return None
        try:
            return datetime.strptime(raw, "%Y-%m-%d")
        except ValueError as exc:
            raise ValidationError("日期格式应为 YYYY-MM-DD") from exc

    def _choose_category(self) -> int:
        categories = self._app.items.list_categories()
        self._print(render_table(
            ["编号", "分类"],
            [[row.category_id, row.name] for row in categories],
            ["right", "left"],
        ))
        return self._ask_int("分类编号")

    # ------------------------------------------------------------------
    # 展示辅助
    # ------------------------------------------------------------------

    def _show_items(self, items: list[Item]) -> None:
        rows = []
        for item in items:
            rows.append([
                item.item_id,
                item.title[:18],
                f"{item.price:.2f}",
                status_text(item.status),
                item.published_at.strftime("%m-%d %H:%M")
                if item.published_at else "-",
            ])
        self._print(render_table(
            ["编号", "标题", "价格", "状态", "发布"],
            rows,
            ["right", "left", "right", "left", "left"],
        ))

    def _show_item(self, item: Item) -> None:
        self._print(f"  编号：{item.item_id}   状态：{status_text(item.status)}"
                    f"   版本：{item.version}")
        self._print(f"  标题：{item.title}")
        self._print(f"  价格：{item.price:.2f} 元")
        self._print(f"  描述：{item.description or '（未填写）'}")
        if item.off_shelf_reason:
            self._print(f"  下架原因：{item.off_shelf_reason}")

    def _show_reservations(self, rows: list[Reservation]) -> None:
        table = []
        for row in rows:
            table.append([
                row.reservation_id,
                row.item_id,
                row.buyer_id,
                reservation_status_text(row.status),
                "是" if row.disputed else "否",
            ])
        self._print(render_table(
            ["预约号", "商品", "买家", "状态", "异议"],
            table,
            ["right", "right", "right", "left", "left"],
        ))

    # ------------------------------------------------------------------
    # 账户
    # ------------------------------------------------------------------

    def _register(self) -> None:
        student_no = self._ask("学号（8~12 位数字）")
        password = self._ask("密码（至少 8 位）")
        user = self._app.auth.register(student_no, password)
        self._print(f"  注册成功，用户编号 {user.user_id}，请登录。")

    def _login(self) -> None:
        student_no = self._ask("学号")
        password = self._ask("密码")
        self._token = self._app.auth.login(student_no, password)
        self._print("  登录成功。")

    def _logout(self) -> None:
        self._app.auth.logout(self._token)
        self._token = ""

    def _quit(self) -> None:
        self._running = False

    # ------------------------------------------------------------------
    # 浏览与交易
    # ------------------------------------------------------------------

    def _browse(self) -> None:
        self._show_items(self._app.items.search(ItemFilter()))

    def _search(self) -> None:
        keyword = self._ask("关键词（留空不限）")
        category = self._ask("分类编号（留空不限）")
        low = self._ask_price("最低价（留空不限）")
        high = self._ask_price("最高价（留空不限）")
        status = self._ask("状态（留空默认已发布）")
        sort = self._ask("排序 newest/price_asc/price_desc（默认 newest）")
        cond = ItemFilter(
            keyword=keyword,
            category_id=int(category) if category else None,
            min_price=low,
            max_price=high,
            status=parse_status(status) if status else None,
        )
        items = self._app.items.search(cond, sort or "newest")
        self._print(f"  命中 {len(items)} 件")
        self._show_items(items)

    def _detail(self) -> None:
        item_id = self._ask_int("商品编号")
        item = self._app.items.get_item(item_id, self._token or None)
        self._show_item(item)
        revision = self._app.items.revision_of(item_id)
        if revision is not None:
            self._print(f"  待审修改：{revision.title} / {revision.price:.2f} 元")

    def _reserve(self) -> None:
        item_id = self._ask_int("商品编号")
        request_id = self._ask("请求号（留空自动生成）")
        key = request_id or uuid.uuid4().hex[:12]
        reservation = self._app.trade.reserve(self._token, item_id, key)
        self._print(f"  预约成功：预约号 {reservation.reservation_id}，"
                    f"请求号 {reservation.request_id}")

    def _my_reservations(self) -> None:
        self._show_reservations(
            self._app.trade.my_reservations(self._token))

    def _cancel(self) -> None:
        item_id = self._ask_int("商品编号")
        self._app.trade.cancel(self._token, item_id)
        self._print("  已取消预约，商品恢复为已发布。")

    def _confirm(self) -> None:
        item_id = self._ask_int("商品编号")
        self._app.trade.confirm(self._token, item_id)
        self._print("  已确认交易，请与买家线下交付。")

    def _finish(self) -> None:
        item_id = self._ask_int("商品编号")
        self._app.trade.finish(self._token, item_id)
        self._print("  交易已完成。")

    def _dispute(self) -> None:
        item_id = self._ask_int("商品编号")
        note = self._ask("异议说明")
        self._app.trade.raise_dispute(self._token, item_id, note)
        self._print("  已提交异议，自动完成计时暂停。")

    # ------------------------------------------------------------------
    # 商品维护
    # ------------------------------------------------------------------

    def _publish(self) -> None:
        category_id = self._choose_category()
        title = self._ask("标题")
        description = self._ask("描述（草稿可留空）")
        price = self._ask_price("价格")
        if price is None:
            raise ValidationError("价格不能为空")
        images = self._ask("图片文件名（逗号分隔，可留空）")
        draft = ItemDraft(
            category_id=category_id,
            title=title,
            description=description,
            price=price,
            images=[part for part in images.split(",") if part.strip()],
        )
        item = self._app.items.create_draft(self._token, draft)
        self._print(f"  草稿已保存，编号 {item.item_id}，"
                    "可用“提交审核”送审。")

    def _my_items(self) -> None:
        self._show_items(self._app.items.my_items(self._token))

    def _modify(self) -> None:
        item_id = self._ask_int("商品编号")
        title = self._ask("新标题（留空不改）")
        description = self._ask("新描述（留空不改）")
        price = self._ask_price("新价格（留空不改）")
        item = self._app.items.update_item(
            self._token, item_id,
            ItemEdit(
                title=title or None,
                description=description or None,
                price=price,
            ),
        )
        if item.status is ItemStatus.PUBLISHED:
            self._print("  修改已提交审核，前台仍展示原信息。")
        else:
            self._print("  草稿已更新。")

    def _submit(self) -> None:
        item_id = self._ask_int("商品编号")
        item = self._app.items.submit_audit(self._token, item_id)
        self._print(f"  已提交审核，当前状态：{status_text(item.status)}")

    def _off_shelf(self) -> None:
        item_id = self._ask_int("商品编号")
        reason = self._ask("下架原因")
        self._app.items.off_shelf(self._token, item_id, reason)
        self._print("  已下架。")

    def _report(self) -> None:
        item_id = self._ask_int("商品编号")
        reason_type = self._ask("举报类型（如 虚假描述/违禁物品）")
        text = self._ask("补充说明")
        report = self._app.moderation.submit_report(
            self._token, item_id, reason_type, text)
        self._print(f"  举报已提交，编号 {report.report_id}，等待管理员处理。")

    # ------------------------------------------------------------------
    # 通知与统计
    # ------------------------------------------------------------------

    def _notifications(self) -> None:
        rows = self._app.journal.inbox(self._current_user())
        table = [[
            row.notify_id,
            row.kind,
            row.content[:30],
            "已读" if row.read else "未读",
        ] for row in rows]
        self._print(render_table(["编号", "类型", "内容", "状态"], table,
                                 ["right", "left", "left", "left"]))
        notify_id = self._ask("标记已读的编号（留空跳过）")
        if notify_id:
            self._app.journal.mark_read(self._current_user(), int(notify_id))

    def _my_stats(self) -> None:
        start = self._ask_datetime("开始日期")
        end = self._ask_datetime("结束日期")
        summary = self._app.stats.seller_summary(
            self._token, start, _end_of_day(end))
        self._print(f"  发布 {summary['item_published']} 件，"
                    f"预约 {summary['item_reserved']} 次，"
                    f"完成 {summary['item_finished']} 笔，"
                    f"交易额 {summary['trade_amount']} 元")

    # ------------------------------------------------------------------
    # 管理端
    # ------------------------------------------------------------------

    def _pending(self) -> None:
        items = self._app.audit.pending(self._token)
        table = [[
            item.item_id,
            item.title[:18],
            status_text(item.status),
            item.version,
            "有" if self._app.items.revision_of(item.item_id) else "无",
        ] for item in items]
        self._print(render_table(
            ["编号", "标题", "状态", "版本", "待审修改"], table,
            ["right", "left", "left", "right", "left"]))

    def _approve(self) -> None:
        item_id = self._ask_int("商品编号")
        version = self._ask("审核时看到的版本（留空不校验）")
        item = self._app.audit.approve(
            self._token, item_id, int(version) if version else None)
        self._print(f"  审核通过，商品状态：{status_text(item.status)}")

    def _reject(self) -> None:
        item_id = self._ask_int("商品编号")
        reason = self._ask("驳回原因")
        item = self._app.audit.reject(self._token, item_id, reason)
        self._print(f"  已驳回，商品状态：{status_text(item.status)}")

    def _audit_history(self) -> None:
        item_id = self._ask_int("商品编号")
        records = self._app.audit.history(self._token, item_id)
        table = [[
            row.audit_id,
            audit_result_text(row.result),
            row.reason or "-",
            row.audit_at.strftime("%m-%d %H:%M"),
        ] for row in records]
        self._print(render_table(["编号", "结果", "原因", "时间"], table,
                                 ["right", "left", "left", "left"]))

    def _pending_reports(self) -> None:
        reports = self._app.moderation.pending_reports(self._token)
        table = [[
            row.report_id,
            row.item_id,
            row.reason_type,
            report_state_text(row.state),
            row.created_at.strftime("%m-%d %H:%M"),
        ] for row in reports]
        self._print(render_table(
            ["编号", "商品", "类型", "状态", "时间"], table,
            ["right", "right", "left", "left", "left"]))

    def _handle_report(self) -> None:
        report_id = self._ask_int("举报编号")
        choice = self._ask("处置方式 1=下架商品 2=驳回举报")
        action = ACTION_OFF_SHELF if choice == "1" else ACTION_REJECT
        self._app.moderation.handle(self._token, report_id, action)
        self._print("  已处理。")

    def _site_stats(self) -> None:
        start = self._ask_datetime("开始日期")
        end = self._ask_datetime("结束日期")
        summary = self._app.stats.site_summary(
            self._token, start, _end_of_day(end))
        for key, value in summary.items():
            self._print(f"  {key}: {value}")

    def _logs(self) -> None:
        action = self._ask("操作类型（留空不限）")
        rows = self._app.journal.query(self._current_user(),
                                       action_type=action)
        table = [[
            row.log_id,
            row.operator_id,
            row.action_type,
            row.target_id,
            "成功" if row.result else "失败",
        ] for row in rows[:20]]
        self._print(render_table(
            ["编号", "操作人", "动作", "对象", "结果"], table,
            ["right", "right", "left", "right", "left"]))

    def _categories(self) -> None:
        self._print(render_table(
            ["编号", "分类"],
            [[row.category_id, row.name]
             for row in self._app.items.list_categories()],
            ["right", "left"]))
        choice = self._ask("1=新增 2=改名 3=删除 其他=返回")
        if choice == "1":
            name = self._ask("分类名")
            self._app.items.create_category(self._token, name)
            self._print("  已新增。")
        elif choice == "2":
            category_id = self._ask_int("分类编号")
            name = self._ask("新名称")
            self._app.items.rename_category(self._token, category_id, name)
            self._print("  已改名。")
        elif choice == "3":
            category_id = self._ask_int("分类编号")
            self._app.items.delete_category(self._token, category_id)
            self._print("  已删除。")

    def _restore(self) -> None:
        item_id = self._ask_int("商品编号")
        self._app.items.restore(self._token, item_id)
        self._print("  已恢复上架。")


def _end_of_day(moment: datetime | None) -> datetime | None:
    """把筛选用的结束日期补到当天 23:59:59，避免漏掉当天记录。"""
    if moment is None:
        return None
    return moment.replace(hour=23, minute=59, second=59)
