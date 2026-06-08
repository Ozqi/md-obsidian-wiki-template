---
title: 全局知识库变更日志
created: 2026-06-08
updated: 2026-06-08
tags:
  - wiki/log
aliases:
  - Global Log
content_origin: mixed
ai_model: "GPT-5"
human_reviewed: false
reviewed_at: ""
---

- 2026-06-08 schema | [[README]]、[[wiki-worker]] | 收敛为纯提示词模板：删除预设主题分类目录，保留规则、Agent、skills、脚本和 raw source 骨架；原因：模板只需要提示词完整，不需要具体知识分类；后续：使用者按自身 vault 自定义路由。
- 2026-06-08 schema | [[README]]、[[AGENTS]]、[[CLAUDE]] | 初始化 Obsidian LLM Wiki 模板：加入 Wiki Worker、Lint Agent、Notion Agent、raw source 队列和基础脚本；原因：模板仓库初始化；后续：按实际知识域调整路由表。
