# 校园二手交易系统（CampusTrade）· 实验三实现

学号 241220107　姓名 黄毅

依据实验二的需求（19 条）与 UML 设计（类图 / 状态图 / 时序图 / 组件图）实现。
语言 Python 3，仅用标准库，无需安装依赖即可运行；开发期额外用 pylint 做风格检查、
pytest 跑单元测试。

## 运行

```bash
python run.py --demo      # 端到端演示，内存库，不影响数据文件
python run.py --seed      # 首次运行：铺演示数据并进入交互界面
python run.py             # 交互式运行，数据存 data/campustrade.json
python run.py --memory    # 只用内存库，退出即清空
```

演示账号（密码均为 `Campus#2026`）：

| 学号 | 角色 |
| --- | --- |
| 900000001 | 管理员 |
| 241220101 | 普通用户（卖家） |
| 241220102 | 普通用户（买家） |
| 241220103 | 普通用户（买家） |

## 检查与测试

```bash
python -m compileall -q campustrade run.py tests   # 语法编译检查
python -m pylint campustrade run.py tests          # 代码风格（PEP 8）
python -m pytest -q                                # 单元测试
```

开发期安装了 pylint 4.1.3 与 pytest 9.2.0：

```bash
python -m pip install pylint pytest
```

## 目录结构

```
code/
├── run.py                  入口：参数解析与启动
├── pylintrc                pylint 配置（行宽 79、PEP 8）
├── campustrade/
│   ├── models.py           实体、枚举、值对象
│   ├── errors.py           业务异常层次
│   ├── state.py            商品状态机（状态图的可执行版本）
│   ├── security.py         口令散列与会话令牌
│   ├── storage.py          仓储层：内存表 + JSON 快照
│   ├── context.py          应用装配（依赖顺序）
│   ├── seed.py             演示数据
│   ├── demo.py             端到端演示脚本
│   ├── services/           业务服务（对应组件图的 8 个模块）
│   │   ├── auth.py         用户与权限
│   │   ├── item.py         商品与分类
│   │   ├── audit.py        审核
│   │   ├── trade.py        交易
│   │   ├── moderation.py   举报治理
│   │   ├── stats.py        统计
│   │   ├── journal.py      日志与通知
│   │   └── base.py         服务基类（取当前用户、落盘）
│   └── cli/                控制台界面
│       ├── shell.py        菜单、输入、结果展示
│       └── tables.py       中文宽度对齐的表格渲染
├── tests/                  73 个单元测试
└── docs/                   风格检查、测试、运行输出与代码规模统计
```

## 与实验二设计的对应关系

| 实验二 | 实验三实现 |
| --- | --- |
| 类图 8 个包、10 个类、5 个枚举 | `models.py` 一一对应；`ItemRevision` 增加 `category_id` |
| 类图上的 `Item.submitAudit()` 等方法 | 上移到 `ItemService` / `AuditService`，实体只保留局部判断 |
| 状态图 7 个状态 | `state.py` 的迁移表，非法迁移抛 `Conflict` |
| 时序图"预约" | `TradeService.reserve`：加锁 + 幂等键 + 唯一有效预约 |
| 组件图 8 个模块 | `services/` 下 7 个服务 + `journal` 横切模块 |

设计差异与理由见实验报告第 5 节。

## 数据文件

`data/campustrade.json` 为整库快照（原子替换写入）。删除该文件即回到空库，
配合 `--seed` 可重建演示数据。该文件已在 `.gitignore` 中忽略。
