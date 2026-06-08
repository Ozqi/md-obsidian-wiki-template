# Obsidian-LLM Wiki 维护规则

目标：把资料、问答和项目理解沉淀为可复用、可追溯、可互链的 Markdown 知识网络。

`AGENTS.md` 与 `CLAUDE.md` 是本 vault 的规则层，必须保持同步；它们本身不按普通笔记处理，不需要 frontmatter。

## 1. 生成风格

正文只写知识，不写聊天式包裹。

- 每次生成都视作“知识条目插入”：定义、事实、流程、对比、决策、疑问、反例、结论。
- 不在插入内容前后写“总结”“以下是”“本次更新”“后续可以”等说明性套话。
- 不把生成模型、生成时间、审阅提醒、执行过程、写入理由写进正文。
- 不为了完整而生成空泛概述；只插入能被复用、检索、互链的关键知识。
- 不确定内容写成知识状态，例如“待核验：...”或“争议：...”，并保留来源。
- 报告、dashboard、log 可以保留自身必要格式，但仍应短、准、可执行。

## 2. 文档属性

普通笔记和知识库 Markdown 必须使用 Obsidian YAML frontmatter。历史文件在下次被编辑、重写或由 AI 补充时迁移。

配置文件、agent 规则文件、`.obsidian/` 下文件、插件配置、脚本说明不按普通笔记处理。

标准格式：

```yaml
---
title: <文件标题>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
tags:
  - <tag>
aliases:
  - <alias>
content_origin: human | ai | mixed
ai_model: "<model>"
human_reviewed: false
reviewed_at: ""
---
```

字段规则：

- `title`：默认与文件名主体一致。
- `created`：页面创建或首次整理成文日期。
- `updated`：最近一次知识内容更新日期。
- `tags`：Obsidian 层级标签；无明确标签写 `[]`。
- `aliases`：无别名写 `[]`。
- `content_origin`：`human` / `ai` / `mixed`。
- `ai_model`：AI 参与生成或大段改写时填写；纯人工写 `""`。
- `human_reviewed`：人工审阅过写 `true`，否则写 `false`。
- `reviewed_at`：人工审阅日期；未审写 `""`。

不再新增 `AI-GENERATED-CONTENT` 注释块、正文审阅 checklist、`ai_event`、`ai_generated_at`、`ai_review_status`。旧字段可暂时保留；下次编辑该文件时迁移为 `created`、`updated`、`ai_model`、`human_reviewed`、`reviewed_at`。

AI 改动普通笔记时：更新 `updated`，设置 `content_origin: mixed` 或 `ai`，写入 `ai_model`，并把 `human_reviewed` 置为 `false`。人工审阅后再改为 `true`。

## 3. 元数据与来源归位

知识以外的信息只能放两个位置：

- 文档属性：创建时间、更新时间、生成模型、是否人工审阅、标签、别名。
- 文档末尾：外部链接、raw source 路径、参考资料。

文末来源格式：

```markdown
## 参考

- [资料标题](https://example.com)
- `raw_sources/example.md`
```

正文中保留必要内部 wikilink；外链和长来源说明优先放文末。临时计划、抓取状态、执行细节写入 `tmp/` 或 `raw_sources/index.md`，不混入知识正文。

## 4. Wiki 结构

三层结构：

- Raw sources：原始资料是 source of truth，尽量不可变；AI 只读取、引用、提炼，不直接改写原文。
- Wiki：主题页、概念页、实体页、对比页、综合页、来源要点页；新资料进入时要更新相关旧页。
- Schema：`AGENTS.md`、`CLAUDE.md`、模板和规则文件；必须确定、同步、少解释。

长期主题必须有入口页，优先使用同目录 `index.md`；已有总览页可沿用。入口页只维护：一句话说明、核心 wikilink、当前结论/问题、最近更新入口。不要给普通目录强行创建 `index.md`。

名词解释按模块归档：每个长期模块优先维护自己的术语页或术语区；`概念百科/名词科普` 只放跨主题、难归类、方法论级或轻量速记的通用名词。具体领域术语不堆到通用名词页。

插入名词时先按目录层级、主题层级和现有小节语义寻找位置；能放入已有分类就插入对应分类，必要时新增合适小节，禁止为了省事追加到文档尾部。

内部链接使用 wikilink：`[[页面名]]`、`[[页面名#标题]]`、`[[页面名|显示文本]]`。外部资料使用 Markdown 链接并优先收束到文末参考区。

Mermaid 图优先表达层级和归属，不追求横向铺开。默认使用 `flowchart TD` / `graph TD` 的纵向目录树式布局；避免 `graph LR` 造成宽图。节点较多时按模块拆成多个小图，或改用 Markdown 列表/表格。单个节点的同层分支过多时，用 `subgraph` 分组，保持读者从上到下扫描。

## 5. Ingest / Query / 写回

处理新资料时：

1. 读取 raw source，保留来源链接或路径。
2. 提炼事实、观点、概念、实体、疑问和不确定点。
3. 长资料先写来源要点页，不把加工内容混进原文。
4. 更新相关主题页、概念页、实体页、对比页或综合页。
5. 补 wikilink、反链语境和文末来源。
6. 新资料推翻旧结论时，显式标记冲突、修正或争议。
7. 必要时更新主题 `index.md`。
8. 触发 Log 规则时追加根目录 `log.md`；长期主题可另写局部 `log.md`。

基于 wiki 回答问题时：先读主题 `index.md`，再读相关页面；事实性问题必要时回 raw source 核验。

高价值回答要写回 wiki：对比表变对比页，综合判断变主题页，问题清单变研究路线，临时关联变 wikilink 或新概念页。

写回原则：优先更新已有页面；新建前先搜索查重。不要写回寒暄、一次性命令输出、无长期价值的中间推理。

### Markdown 预读索引

向已有 Markdown 文件插入内容前，优先运行 `scripts/md_outline_index.py <文件>`，读取 `tmp/md-outline-index/*.json` 中的标题树、行号和 section 范围，再选择插入位置。小文件或一次性微调可直接人工阅读，但禁止不看结构就追加到文档尾部。

索引用途：

- 根据 `tree` 和 `headings[].path` 判断主题层级。
- 根据 `section_start_line` / `section_end_line` 找到小节边界。
- 根据 `insert_after_line` 在目标小节末尾插入内容。
- 根据 `frontmatter.end_line` 区分属性区和正文。

索引文件属于 `tmp/` 临时状态，不写入 wiki 结论；原 Markdown 改动后必须重新生成。

### raw_sources / tmp

`raw_sources/index.md` 是 raw source 区的 ingest TODO 入口，负责记录待读资料、目标写入位置、状态和阻塞原因。除 `raw_sources/index.md` 外，`raw_sources/` 下原始资料文件默认严格只读；AI 不应在原始资料文件内写规划、状态、提炼内容或处理标记。

`tmp/` 只用于 Agent 自我规划、批处理草稿和本轮执行细节。用户可见、长期保留的 ingest 队列必须维护在 `raw_sources/index.md`。

### 代码仓库 raw source

外部代码仓库也属于 raw source，统一拉取到 `raw_sources/repos/`。代码学习、仓库解析、架构理解、API/实现核验时，先查 `raw_sources/index.md`，再到 `raw_sources/repos/<repo>/` 读取本地镜像。

`raw_sources/repos/` 下仓库是只读来源副本，不是开发工作区。禁止在其中编辑、格式化、生成文件、安装依赖产物、提交 commit、改分支或执行会改变工作树的命令。允许的默认操作只有读取和分析：`rg`、`find`、`sed`、`git log`、`git show`、`git status`、静态浏览。

需要新增代码仓库时：clone 到 `raw_sources/repos/`，在 `raw_sources/index.md` 记录仓库 URL、目标 Wiki 页、当前 commit/ref 和处理状态。需要刷新仓库时，只在用户明确要求或 ingest 任务要求下执行，并记录新 commit/ref。

代码解析结论写入 Wiki 层主题页、项目页、架构页、概念页或对比页；临时阅读计划写入 `tmp/`；不要把解析笔记写回代码仓库副本。

引用代码来源时使用：仓库 URL + commit/ref + 文件路径。必要格式：

```markdown
## 参考

- `raw_sources/repos/<repo>/<path>` @ `<commit>`
- [repo](https://github.com/owner/repo)
```

处理流程：

1. 每次处理 raw source / URL ingest 前，先读 `raw_sources/index.md`。
2. 从 `raw_sources/index.md` 选择待处理项；任务较复杂时，在 `tmp/` 建本轮执行计划。
3. 只读读取原始资料或抓取 URL，保留路径/URL 作为来源。
4. 长资料先在 Wiki 层建立来源要点页或主题页条目，不把加工内容写回原始资料文件。
5. 更新相关主题页、概念页、实体页、对比页或综合页。
6. 回写 `raw_sources/index.md` 的任务状态、写入目标和阻塞原因；重要 ingest 追加根目录 `log.md`。
7. 抓取失败、登录受限、内容过长或主题不明时，把任务标为待补充，不改原始资料文件。

## 6. 全局 log.md

根目录 `log.md` 是本 Obsidian-LLM wiki 仓库的全局变更总账。只记录知识库变化，不记录聊天流水、命令输出或无长期价值的中间推理。

必须写入全局 `log.md` 的情况：

- 新建、重命名、合并、拆分重要页面或主题目录。
- ingest 新资料并写入 wiki。
- 修改主题入口页 `index.md`、核心概念页、对比页、综合页。
- 修正旧结论、标记冲突、删除或替换过时内容。
- 进行 wiki lint 并产出需要后续处理的问题清单。
- 修改 `AGENTS.md`、`CLAUDE.md`、模板、schema 或其他会影响 AI 写作行为的规则文件。

不必写入全局 `log.md` 的情况：只改错别字、格式微调、未写回 wiki 的一次性问答、临时命令输出、未形成稳定结论的聊天推理。

日志格式保持紧凑，每条 1 行；只有后续事项较多时才另起子项：

```markdown
- YYYY-MM-DD <ingest|query|update|lint|schema> | [[页面A]]、[[页面B]] | <事件名>：<一句话记录>；原因：<用户要求/资料更新/规则调整>；后续：<无/待办>
```

局部主题 `log.md` 只作为长期主题细账，可选维护；全局 `log.md` 记录入口级变化。

## 7. Lint

Lint 目标：发现 wiki 结构、语法、风格密度和内容质量问题，产出具体问题项；未经用户确认，不大规模改写历史笔记。

### 触发方式

- 用户明确要求 lint。
- 大量 ingest、目录重组、规则修改后。
- 发现同一主题出现重复页、冲突结论或大量孤立页时。

### 执行步骤

1. **确定范围**：全 vault、某个主题目录、某类页面或最近改动文件。
2. **结构扫描**：检查 frontmatter、旧 AI 内容块、缺失 `index.md` 的长期主题、孤立页、重复标题/别名、断链和空链接。
3. **来源扫描**：检查事实性结论、引用、外部资料是否缺少文末来源链接或 raw source 路径。
4. **语法风格扫描**：检查 Markdown / Obsidian 语法、术语一致性、中英文混排、病句、冗余总结、低信息密度段落。
5. **语义抽查**：抽查核心页面之间是否有旧结论被覆盖、相互矛盾、概念重复、主题边界不清。
6. **输出报告并写回 TODO**：按严重程度分组，列出问题、页面、证据、改法；对摆放错误、分类错误、文档过长、raw source 边界污染、缺来源或需要拆分/迁移/重归档的问题，同步写入 `raw_sources/index.md` 的 TODO 队列。
7. **等待确认**：只有用户同意后，才执行批量重命名、合并、拆分或大规模改写。
8. **记录日志**：如果 lint 产出后续问题清单或执行了修复，追加根目录 `log.md`。

### 检查项

- 属性：缺 frontmatter、字段缺失、旧字段未迁移、`human_reviewed` 缺失或不合理。
- 链接：孤立页、断链、缺少反链语境、外链未收束到文末参考区。
- 结构：长期主题无入口页、入口页过长、普通目录被强行建入口、重复页面未互链。
- 来源：事实性结论缺来源、来源要点页未连接主题页、raw source 未保留路径或 URL。
- 内容：旧结论未标记过期、冲突未说明、概念页与主题页职责混乱、高频概念无独立页。
- 语法：frontmatter、Markdown、Obsidian wikilink、表格、code fence、标题层级、中英文混排、术语大小写、病句和重复词。
- 风格密度：正文出现生成说明、总结套话、审阅 checklist、执行过程、空泛评价、重复结论、长铺垫、低信息密度段落。
- 日志：重要结构变更未写入 `log.md`，或把聊天流水写进日志。

### Lint TODO 写回

Lint Agent 发现可执行整理项时，不能只生成报告，还要同步维护 `raw_sources/index.md`：

- 摆放错误：页面应迁入其他目录、改为主题页/概念页/来源要点页，或当前目录语义不匹配。
- 分类错误：术语、概念、项目、工具经验放错模块，例如具体模块术语堆到通用名词页。
- 文档过长：单页过长、入口页承载正文、一个页面混合多个主题，应拆分、合并或重建入口。
- raw source 边界污染：原始资料里混入 AI 摘要、处理标记、旧 AI 元数据或审阅 checklist，需要迁移/清理方案。
- 来源缺口：事实性结论需要补 raw source、URL、commit/ref 或文末参考。

写回格式保持紧凑，优先追加到 `raw_sources/index.md` 的 `### 优先` 或 `### Lint 待处理`；已有同类任务时更新原条目，不重复追加：

```markdown
- [ ] lint: <问题标题> | 来源：<报告路径 或 问题页> | 写入：[[目标页或待定]]；原因：<摆放/分类/过长/来源边界>；建议：<下一步动作>。
```

Lint Agent 只写 TODO，不直接修正文档正文；用户确认修复后再按 TODO 或报告执行。

### 报告格式

报告不写摘要、结论、统计汇总或泛化建议，只列可定位、可修复的问题项：

```markdown
# Wiki Lint 报告：<范围>

- 时间：YYYY-MM-DD HH:mm:ss +0800
- 范围：<文件/目录/最近改动/全库>

## P1

### <问题标题>

- 页面：[[页面名]]
- 类型：<结构|来源|内容|语法|风格密度|流程>
- 证据：`path:line` 或简短摘录
- 问题：具体说明错在哪里
- 改法：给出可直接执行的改写、迁移、删除、拆分或补来源动作

## P2

### <问题标题>

- 页面：[[页面名]]
- 类型：<结构|来源|内容|语法|风格密度|流程>
- 证据：`path:line`
- 问题：...
- 改法：...
```

## 8. Notion Agent

本仓库的 Notion 对接规则见 `.agents/notion-agent.md`。Codex 和 Claude Code 都必须优先遵守该共享配置；需要调整 Notion 行为时只改这一份，再同步检查 `AGENTS.md` 与 `CLAUDE.md` 的引用。

## 9. Wiki Worker

本仓库的默认知识工作 Agent 是 `wiki-worker`，共享配置见 `.agents/wiki-worker.md`，Claude Code 项目级 subagent 包装见 `.claude/agents/wiki-worker.md`。

Wiki Worker 负责 ingest、QA、知识路由和受控 create / read / update / delete / merge。写入前必须先根据路由表判断目标目录、页面和小节；目标不明确时写入 `raw_sources/index.md` 的 `route:` TODO，不强行新建或追加文末。

## 10. Lint Agent

本仓库的 Wiki 巡检规则见 `.agents/lint-agent.md`。Codex 和 Claude Code 都必须优先遵守该共享配置；Claude Code 的项目级 subagent 包装见 `.claude/agents/lint-agent.md`。

Lint Agent 默认只读扫描，把报告写入 `tmp/wiki-lint/`，用于人工审阅或后续 Agent 修复。未经用户确认，不直接修改 Wiki 正文、raw source、规则文件或脚本。
