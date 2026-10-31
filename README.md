# 软件工程 · 校园二手交易系统

学号 241220107　姓名 黄毅

本仓库覆盖整门课程的设计、实现与构建：实验一产出需求分析报告，实验二在其基础上完成架构设计与
界面设计，实验三按设计图实现代码、做静态检查与单元测试，并托管到本仓库。需求与设计同源，因此
三个实验共用一个仓库，后一实验对前一实验内容的回改也记录在本仓库中。

## 目录

| 路径 | 内容 |
| --- | --- |
| `requirements.md` | 实验一交付物之一：19 条需求（v1.1，含实验二设计期的回改记录） |
| `chat.txt` | 实验一交付物之一：需求访谈记录 |
| `report.pdf` | 实验一交付物之一：需求分析报告 |
| `实验2_241220107_黄毅/` | 实验二交付物：`实验报告.pdf`、`UML/`（6 张图的 puml 与 png）、`UI界面/`（10 张界面图） |
| `实验3_241220107_黄毅/` | 实验三交付物：`实验报告.pdf`、`UML/`（类图、服务类图、两张时序图、状态图、组件图）、`code/`（22 个源文件 + 73 个测试 + 检查记录） |
| `src/ui/` | 界面原型的 HTML/CSS 与导出脚本，界面图由此生成 |
| `src/report/` | 实验二报告的 LaTeX 源与插图，`实验报告.pdf` 由此编译 |
| `src/report3/` | 实验三报告的 LaTeX 源、listing 生成脚本与插图 |

## 代码在哪、怎么跑

实验三的实现在 `实验3_241220107_黄毅/code/`，Python 3.10+，只用标准库：

```bash
cd 实验3_241220107_黄毅/code
python run.py --demo      # 端到端演示（内存库，11 节场景）
python run.py --seed      # 铺演示数据后进入命令行界面
python -m compileall -q campustrade run.py tests
python -m pylint campustrade run.py tests   # 10.00/10
python -m pytest -q                         # 73 passed
```

演示账号密码均为 `Campus#2026`：管理员 `900000001`，普通用户 `241220101`（卖家）、
`241220102`、`241220103`（买家）。细节见 `实验3_241220107_黄毅/code/README.md`。

## 重新生成

界面图（需要本机 Chrome，输出到 `src/ui/png/`）：

```bash
cd src/ui
python build_ui.py     # 生成 12 个界面 HTML（报告取其中 10 个）
python shot.py         # 无头浏览器 2 倍图导出 PNG
```

实验二报告 PDF（需要 TeX Live 与 ctex）：

```bash
cd src/report
xelatex main.tex && xelatex main.tex
```

实验三报告 PDF：先由真实运行输出生成 listing，再编译。

```bash
cd src/report3
python make_listings.py     # 从 code/docs/*.txt 生成 listings/*.tex
xelatex main.tex && xelatex main.tex
```

UML 图由 PlantUML 渲染，源码在各实验目录的 `UML/*.puml`：

```bash
java -jar plantuml.jar -charset UTF-8 -tpng *.puml
```

## 提交约定

提交按“一类产物一次提交”拆分，提交说明标注该次改动属于 **AI 生成** 还是 **人工修改**，
人工修改的部分写明改了什么、为什么改。这样回看历史时可以先看人工修改的 diff（含判断），
AI 生成的部分只看是否被完整改写；需要回退时也只需撤掉某一次。

实验二的提交顺序：

1. `实验二 UML`：六图的 puml 与渲染图（AI 生成初稿 + 人工修订 7 处）
2. `实验二 UI`：10 个界面稿与原型源文件（AI 出版式，人工改布局与控件）
3. `回改实验一`：REQ-017 驳回后状态、REQ-001 幂等键、REQ-009 模块归属
4. `实验二 报告`：报告 LaTeX 源与 PDF

第 3 条是实验二设计期的真实回改：画状态图时发现 REQ-017“审核驳回后商品回到草稿”会让已被预约的
已发布商品退回草稿，与同一条“修改审核期间买家仍可预约”冲突。先改需求、再改图，两次改动分属
两个提交，diff 可以互相对照。详细理由见 `requirements.md` 文末的“实验二设计期的回改记录”。

实验三的提交顺序：

1. `实验三 代码`：五层实现与 73 个测试（AI 生成初稿 + 人工修订，含三处真实缺陷修复）
2. `实验三 代码留档`：pylint 前后对比、测试与演示输出、代码规模、十轮提示词记录
3. `实验三 UML`：按实现修订的类图、新增服务类图与两张时序图
4. `实验三 报告`：报告 LaTeX 源与 PDF

实验三实现期对实验二设计有三处修订（实体方法上移到服务层、`ItemRevision` 增加 `categoryId`、
新增 `ServiceBase`/`Store`/`Table`），理由见实验三报告 2.3 与 7.1 节。
