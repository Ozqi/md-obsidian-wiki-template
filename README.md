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

面向 Agent 协作的 Obsidian 知识库模板：把资料、代码仓库、网页、问答和项目理解沉淀为可追溯、可互链、可巡检的 Markdown wiki。

## 入口

- [[index|全局入口]]：主题导航。
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
2. 修改 `.agents/wiki-worker.md` 的路由表，使目录和主题匹配你的知识库。
3. 修改 `.agents/notion-memory.md`，填入你的 Notion workspace / database / page 入口；不用 Notion 可保留空表。
4. 处理资料前先登记到 [[raw_sources/index]]。
5. 写入知识时默认调用 Wiki Worker；巡检时调用 Lint Agent。
6. 人工审阅后把页面 frontmatter 的 `human_reviewed` 改成 `true`。

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
