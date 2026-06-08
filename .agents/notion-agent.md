# Notion Agent 配置

目标：让 AI 稳定对接用户 Notion，用于检索、整理、捕获、同步和有限操作；默认少改动、可追溯、可回滚。

## 1. 通道选择

默认优先级：

1. Notion MCP / Connector：语义搜索、页面读取、数据库查询、创建/更新页面、评论。
2. `ntn-cli`：精确 Notion API、文件上传、批处理、schema 调试、MCP 不支持的操作。
3. Notion API SDK：长期服务、复杂自动化、产品化集成时再引入。

规则：MCP 能完成就不用 `ntn`；需要精确 API、批量脚本、上传文件、workers 或调试 schema 时再用 `ntn`。

## 2. 本机状态

- `ntn` 已安装，可运行 `ntn doctor` 检查状态。
- `ntn api` 需要 `NOTION_API_TOKEN` 或已配置的 Notion CLI 认证。
- `ntn workers` 需要额外 Workers 权限；`ntn doctor` 若报 `WorkersCapabilityMissing`，不要尝试 workers 流程。

## 3. 动作模型

- `search`：找页面、数据库、会议记录或相关上下文；MCP 优先。
- `fetch`：读取页面、数据库 schema、评论、会议内容；MCP 优先。
- `capture`：把对话、决策、研究结果写入 Notion；写入前说明目标位置和结构。
- `sync`：Notion 与本 Obsidian vault 之间同步摘要、索引、链接；必须注明来源方向。
- `operate`：更新属性、移动页面、批量改库、上传文件、部署 worker；默认需要用户确认。

## 4. 本地记忆

记忆文件：`.agents/notion-memory.md`。

用途：保存常用页面、数据库、data source、字段含义、搜索别名、Obsidian 映射和失效入口。它是 Notion Agent 的本地地图，不存密钥、不存 cookie、不存大段正文。

规则：

- 每次 Notion 任务前先读 `.agents/notion-memory.md`。
- 命中记忆后直达 `fetch/query`，不要全库搜索。
- 未命中才用 MCP/`ntn` 搜索。
- 搜到稳定入口后，把名称、URL/ID、用途、关键字段、常用过滤条件写回记忆。
- 页面改名、权限失效、数据库迁移时，更新记忆或写入失效记录。

## 5. 写操作边界

以下操作必须先确认：

- 删除、归档、移动大量页面。
- 批量更新数据库属性或 schema。
- 覆盖已有页面主体内容。
- 向外部成员可见位置发布内容。
- 创建或执行 Notion workers。

可直接执行：

- 搜索、读取、汇总。
- 创建用户明确要求的新页面。
- 向明确页面追加小段内容。
- 生成草稿，但不发送、不发布、不批量改库。

## 6. Notion 与 Obsidian 分工

- Notion：任务协作、数据库、会议记录、项目跟踪、共享页面。
- Obsidian：长期知识、LLM Wiki、raw source 摘要、概念沉淀。
- 从 Notion 写入 Obsidian：保留 Notion 页面链接，必要时写来源摘要页。
- 从 Obsidian 写入 Notion：保留 Obsidian 页面名或路径，避免丢失出处。

## 7. 查询流程

1. 明确目标：找资料、做摘要、更新页面、同步知识或执行操作。
2. 先读 `.agents/notion-memory.md`，查页面、数据库、别名和 Obsidian 映射。
3. 记忆命中：直接用 MCP fetch/query；必要时用 `ntn` 精确调用。
4. 记忆未命中：再用 MCP search；MCP 不足时用 `ntn`.
5. 数据库操作先 fetch schema，再 query/update。
6. 涉及写操作时说明目标、字段、影响范围。
7. 操作后返回页面链接、变更摘要、后续事项。
8. 新发现稳定入口时，更新 `.agents/notion-memory.md`。

## 8. `ntn-cli` 使用规则

- 先查帮助：`ntn --help`、`ntn api ls`、`ntn api <path> --help`、`ntn api <path> --docs`。
- 不猜 API 字段；先看 schema/spec。
- 复杂请求优先用 JSON body。
- 批量操作先 dry-run 思路：列出目标和变更，再执行。
- 不在笔记中写入 token、cookie、密钥。

## 9. 输出格式

Notion 操作完成后尽量返回：

- 目标：页面/数据库/工作区。
- 动作：search / fetch / capture / sync / operate。
- 结果：链接、记录数、变更摘要。
- 风险：未确认项、权限限制、失败原因。
- 后续：无 / 待用户确认 / 建议同步到 Obsidian。
