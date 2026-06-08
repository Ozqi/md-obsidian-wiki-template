---
title: Obsidian LLM Wiki Template
created: 2026-06-08
updated: 2026-06-08
tags:
  - project/template
aliases:
  - md obsidian wiki template
content_origin: mixed
ai_model: "GPT-5"
human_reviewed: false
reviewed_at: ""
---

# Obsidian LLM Wiki Template

面向 Agent 协作的 Obsidian 知识库提示词模板：提供维护规则、Agent 配置、Claude Code subagent、Obsidian skills、raw source 队列和辅助脚本。

## 入口

- [[index|全局入口]]：提示词与模板入口。
- [[dashboard|人工 Review 看板]]：待审文档入口。
- [[log|全局知识库变更日志]]：重要 ingest、schema、lint、结构变更。
- [[raw_sources/index|Raw Sources]]：资料 ingest TODO 和原始资料入口。
- [[AGENTS|Codex 维护规则]] / [[CLAUDE|Claude Code 维护规则]]：仓库级写作规范。

## Agent

| Agent | 配置 | Claude Code 入口 | 用途 |
|---|---|---|---|
| Wiki Worker | `.agents/wiki-worker.md` | `.claude/agents/wiki-worker.md` | 默认知识工作入口；负责 ingest、QA、知识路由和受控增删改查。 |
| Lint Agent | `.agents/lint-agent.md` | `.claude/agents/lint-agent.md` | 巡检结构、来源、语法、风格密度、旧 AI 标记和语义冲突。 |
| Notion Agent | `.agents/notion-agent.md` | `.claude/agents/notion-agent.md` | 检索、读取、同步 Notion；维护 `.agents/notion-memory.md` 本地地图。 |

`.agents/skills/` 是 Obsidian、网页解析、Canvas、Bases 等工具能力，不是独立 Agent。

## 使用方式

1. 克隆本仓库为新 vault。
2. 复制或保留全部提示词文件：`AGENTS.md`、`CLAUDE.md`、`.agents/`、`.claude/agents/`。
3. 修改 `.agents/notion-memory.md`，填入你的 Notion workspace / database / page 入口；不用 Notion 可保留空表。
4. 处理资料前先登记到 [[raw_sources/index]]。
5. 写入知识时默认调用 Wiki Worker；巡检时调用 Lint Agent。
6. 人工审阅后把页面 frontmatter 的 `human_reviewed` 改成 `true`。

## 提示词文件

- `AGENTS.md`：Codex 仓库级规则。
- `CLAUDE.md`：Claude Code 仓库级规则。
- `.agents/wiki-worker.md`：ingest、QA、路由、受控增删改查。
- `.agents/lint-agent.md`：结构、来源、语法、风格密度巡检。
- `.agents/notion-agent.md`：Notion 对接规则。
- `.agents/notion-memory.md`：Notion 本地记忆模板。
- `.claude/agents/*.md`：Claude Code subagent wrapper。
- `.agents/skills/`：Obsidian Markdown、Bases、Canvas、CLI、网页解析等技能提示词。

## 规范

- 正文只插入知识条目，不写聊天式总结。
- 元数据写 frontmatter：`created`、`updated`、`ai_model`、`human_reviewed`、`reviewed_at`。
- 来源放文末 `## 参考`。
- 内部链接用 Obsidian wikilink。
- Mermaid 图优先用纵向目录树式布局。
- raw source 和 `raw_sources/repos/` 代码镜像默认只读。

## 脚本

- `scripts/md_outline_index.py <file>`：生成 Markdown 标题树 JSON，用于插入定位。
- `scripts/review_dashboard.py`：刷新 [[dashboard]]。

## 初始化

```bash
git init
python3 scripts/review_dashboard.py
```
