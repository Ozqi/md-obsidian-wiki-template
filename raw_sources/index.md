---
title: Raw Sources
created: 2026-06-09
updated: 2026-06-09
tags:
  - wiki/raw-sources
aliases:
  - 原始资料
  - Ingest TODO
content_origin: mixed
ai_model: "GPT-5"
human_reviewed: false
reviewed_at: ""
---

# Raw Sources

原始资料区入口，也是 ingest 任务 TODO。Agent 处理外部资料、网页、论文、长文档、代码仓库或 raw source 前，必须先读本页。

## 规则

- 本页可维护任务状态；其他 raw source 文件默认只读。
- 新资料先保留 URL / 路径，再决定是否写入 Wiki。
- 代码仓库统一拉取到 `raw_sources/repos/`，只读解析，不在镜像内修改。
- 稳定结论写入主题页、概念页、对比页或综合页。
- 完成、阻塞、改目标都回写本页。

## 状态

- `[ ]` 待读
- `[/]` 处理中
- `[x]` 已写入 Wiki
- `[?]` 需要补充目标、权限或来源
- `[-]` 暂不处理

## Ingest TODO

### 优先

- [ ] 示例资料 | 来源：待填 | 写入：[[目标页]]

### Lint 待处理
