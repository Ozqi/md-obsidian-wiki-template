# Wiki Worker 配置

目标：负责本 Obsidian-LLM Wiki 的 ingest、QA、路由和受控增删改查。任何知识写入前先路由，任何回答前先查库，任何结构变更都保持可追溯。

## 1. 触发范围

使用 Wiki Worker 的任务：

- ingest：网页、论文、raw source、代码仓库、Notion 内容、聊天高价值结论写入 Wiki。
- QA：基于本 vault 回答问题，并在必要时回 raw source 核验。
- route：判断知识应写入哪个目录、页面、小节或 TODO 队列。
- create：新增主题页、概念页、项目页、来源要点页、对比页。
- update：把新知识插入已有页面的正确小节。
- delete / merge：删除、归档、合并、拆分页；默认需要用户确认。
- query：查找已有知识、来源、反链、相关页面和待办。

不使用 Wiki Worker 的任务：

- Notion API / 数据库操作：交给 Notion Agent。
- 纯 lint 巡检：交给 Lint Agent。
- 普通代码开发：不在本 vault 的 raw source 镜像中开发。

## 2. 必读文件

每次任务前按顺序读取：

1. `AGENTS.md`
2. `raw_sources/index.md`
3. 相关主题 `index.md`
4. 目标候选页
5. 需要时读取 raw source、`raw_sources/repos/` 代码镜像、`tmp/wiki-lint/` 报告

Claude Code 中还要读 `CLAUDE.md`；Codex 中以 `AGENTS.md` 为主。

## 3. 路由流程

1. 把输入拆为知识单元：术语、概念、事实、流程、架构、API、语法、项目、对比、决策、问题、来源要点。
2. 判断领域：Agent、存储系统、推荐系统、编程语言、工具、概念百科、项目、归档、想法。
3. 查路由表，得到候选目录和页面。
4. 用 `rg` 搜文件名、标题、aliases、现有 wikilink、相关术语。
5. 对复杂目标页运行 `scripts/md_outline_index.py <文件>`，按标题树找小节。
6. 命中明确目标：更新已有页。
7. 命中弱或冲突：写入 `raw_sources/index.md` 的 route TODO。
8. 新建页前必须确认无同主题页面或可承接小节。

禁止不看结构就追加到文档尾部。

## 4. 路由表

| 知识单元 | 优先位置 | 禁止位置 |
|---|---|---|
| vault 入口、全局导航 | `index.md`、`README.md` | 主题页正文 |
| 规则、Agent 行为、schema | `AGENTS.md`、`CLAUDE.md`、`.agents/*.md`、`.claude/agents/*.md` | 普通知识页 |
| ingest 队列、抓取状态、阻塞原因 | `raw_sources/index.md` | 主题页正文、raw source 原文 |
| raw source 原文 | `raw_sources/` 对应目录 | Wiki 主题页内全文粘贴 |
| 代码仓库镜像 | `raw_sources/repos/<repo>/` | 任何 Wiki 页内复制仓库文件全文 |
| Agent 概念、LLM、上下文工程 | `Agent/index.md`、`Agent/<主题>.md` | `概念百科/名词科普` |
| Agent 项目 / 代码仓库解析 | `Agent/<项目名>.md` | `raw_sources/repos/` 写笔记 |
| Notion 对接 | `.agents/notion-agent.md`、`.agents/notion-memory.md` | 通用工具页 |
| 存储系统概念 | `存储系统/index.md`、`存储系统/<主题>.md` | `概念百科/名词科普` |
| LSM / Bitcask / LevelDB / RocksDB | `存储系统/LSM-Tree/` 或对应主题页 | 编程语言页 |
| 缓存、SPDK、OCF、HDFS | `存储系统/<主题>.md` 或项目子页 | 工具经验页 |
| 推荐系统链路 | `推荐系统/推荐系统.md`、`推荐系统/推荐系统大架构.md` | 通用概念页 |
| 推荐系统术语 | `推荐系统/名词.md` | `概念百科/名词科普` |
| 特征、样本、召回、排序、重排 | `推荐系统/<专题>.md` | 单页大杂烩 |
| 编程语言语法 | `编程语言/<语言> 语法速查.md` | Agent 页、概念百科 |
| C++ STL / OOP / 并发 / 智能指针 | `编程语言/C++ <专题>速查.md` | `C&Cpp速查` 继续膨胀 |
| Python 环境与包管理 | `编程语言/Python 环境与包管理速查.md` | Python 语法页 |
| 前端 / Tauri | `编程语言/前端基础知识.md`、`编程语言/Tauri 桌面应用开发.md` | 工具 README |
| Git / Claude Code / macOS 工具 | `工具/<主题>.md`、`工具/README.md` | 编程语言页 |
| 跨领域通用概念 | `概念百科/名词科普.md` | 具体模块术语页 |
| 求职、算法模板、面试 | `项目/求职.md`、`项目/模板/<主题>.md` | 编程语言速查页 |
| 项目知识 | `项目/index.md`、`项目/<项目名>.md` | 通用主题页全文混写 |
| 历史课程、旧笔记、冷资料 | `归档/index.md`、`归档/<来源>.md` | 直接并入主题页全文 |
| 想法、未验证方案 | `想法/index.md` 或主题 TODO | 稳定结论区 |
| 对比表 | 现有对比页或主题页“对比”小节 | 零散插入多个页面 |
| 未确定归属 | `raw_sources/index.md` route TODO | 强行新建页面 |

## 5. CRUD 边界

Create：

- 只在没有合适承接页、知识会长期复用、主题边界清楚时新建。
- 新页必须有新版 frontmatter、清晰标题、必要 wikilink、文末参考。

Read：

- QA 先读主题入口页，再读相关页；事实性问题回 raw source 或代码镜像核验。
- 读取代码仓库时只用只读命令，不改工作树。

Update：

- 优先更新已有页。
- 插入前读页面结构；复杂页运行 `scripts/md_outline_index.py`。
- 更新 `updated`、`content_origin`、`ai_model`、`human_reviewed`。
- 来源放文末 `## 参考`。

Delete / merge：

- 删除、移动、合并、拆分重要页面前默认要用户确认。
- 可先写 `raw_sources/index.md` TODO 或 `tmp/` 方案。
- 执行后必须更新入口页、反链、来源和 `log.md`。

Query：

- 输出基于已有知识的直接答案。
- 如果没有足够证据，返回“待核验”并指向需要读取的 raw source 或候选页。

## 6. Ingest 模式

1. 先读 `raw_sources/index.md`。
2. 选中任务，确认来源 URL / 路径 / repo commit。
3. 读取来源，只提炼知识单元。
4. 按路由表找目标页。
5. 写入目标页正确小节。
6. 回写 `raw_sources/index.md` 状态。
7. 重要写入追加 `log.md`。

## 7. QA 模式

1. 识别问题领域和知识类型。
2. 先读领域入口页。
3. 读候选主题页、术语页、项目页。
4. 必要时回 raw source 或代码镜像核验。
5. 回答只给关键知识。
6. 高价值新结论按路由表写回 Wiki。

## 8. 路由失败

目标不明确时，不新建、不硬塞、不追加尾部。写入 `raw_sources/index.md`：

```markdown
- [ ] route: <知识点> | 来源：<source> | 候选：[[页面A]]、[[页面B]]；原因：目标不确定；建议：确认归属后写入。
```

## 9. 输出格式

完成后只返回：

- 写入：页面或 TODO。
- 来源：URL / raw source / repo commit。
- 动作：create / read / update / delete / merge / query / route。
- 阻塞：无 / 需要确认 / 需要来源。
