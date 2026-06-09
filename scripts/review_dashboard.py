#!/usr/bin/env python3
"""Generate dashboard.md for human review of AI-assisted notes."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
AI_BLOCK_START = "<!-- AI-GENERATED-CONTENT:START -->"
REVIEW_CHECKBOX = "- [ ] 已人工审阅"


SKIP_DIRS = {
    ".git",
    ".obsidian",
    ".claude",
    ".agents",
    ".understand-anything",
    "node_modules",
    "raw_sources",
    "tmp",
    "wretched-wavelength",
    "Excalidraw",
    ".trash",
}

SKIP_GLOBS = {
    "image/**/*.excalidraw.md",
}

SKIP_FILES = {
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "dashboard.md",
    "index.md",
    "log.md",
}


def parse_frontmatter(text: str) -> dict[str, Any]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    data: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in match.group(1).splitlines():
        line = raw_line.rstrip()
        if not line:
            continue

        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(line[4:].strip().strip('"'))
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            data[key] = []
        elif value == "[]":
            data[key] = []
        else:
            data[key] = value.strip('"')

    return data


def wikilink(path: Path, title: str) -> str:
    target = str(path.with_suffix(""))
    display = title or path.stem
    return f"[[{target}|{display}]]"


def group_name(path: Path) -> str:
    parts = path.parts
    if len(parts) == 1:
        return "全局入口"
    return parts[0]


def priority(path: Path, ai_block_count: int) -> str:
    if ai_block_count > 0:
        return "P0"
    return "P1"


def should_skip(path: Path) -> bool:
    return (
        path.name in SKIP_FILES
        or any(part in SKIP_DIRS for part in path.parts)
        or any(path.match(pattern) for pattern in SKIP_GLOBS)
    )


def is_false(value: Any) -> bool:
    return str(value).strip().lower() in {"false", "no", "0", ""}


def needs_review(fm: dict[str, Any]) -> bool:
    if "human_reviewed" in fm:
        return is_false(fm.get("human_reviewed"))
    return fm.get("ai_review_status") == "pending"


def collect(vault_root: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for md_path in sorted(vault_root.rglob("*.md")):
        rel = md_path.relative_to(vault_root)
        if should_skip(rel):
            continue

        text = md_path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not needs_review(fm):
            continue

        ai_block_count = text.count(AI_BLOCK_START)
        unchecked_count = text.count(REVIEW_CHECKBOX)
        items.append(
            {
                "path": rel,
                "title": str(fm.get("title") or rel.stem),
                "updated": str(fm.get("updated") or fm.get("date") or ""),
                "ai_block_count": ai_block_count,
                "unchecked_count": unchecked_count,
                "group": group_name(rel),
                "priority": priority(rel, ai_block_count),
            }
        )

    return items


def render(items: list[dict[str, Any]]) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S +0800")
    generated_date = dt.datetime.now().strftime("%Y-%m-%d")
    total = len(items)
    legacy_count = sum(
        1 for item in items if item["ai_block_count"] > 0 or item["unchecked_count"] > 0
    )

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        grouped[item["group"]].append(item)

    p0_items = sorted(
        [item for item in items if item["priority"] == "P0"],
        key=lambda item: str(item["path"]),
    )

    lines = [
        "---",
        "title: 人工 Review 看板",
        "created: 2026-06-02",
        f"updated: {generated_date}",
        "tags:",
        "  - wiki/dashboard",
        "aliases:",
        "  - Review Dashboard",
        "  - 待审看板",
        "content_origin: ai",
        'ai_model: "GPT-5"',
        "human_reviewed: false",
        'reviewed_at: ""',
        "---",
        "",
        "# 人工 Review 看板",
        "",
        "待人工审阅文档入口。",
        "",
        "## 摘要",
        "",
        f"- 待审：{total}",
        f"- 旧标记：{legacy_count}",
        f"- 刷新：{now}",
        "",
        "## 入口",
        "",
    ]

    if not items:
        lines.append("当前没有待人工 review 的文档。")
        return "\n".join(lines) + "\n"

    if p0_items:
        links = "、".join(wikilink(item["path"], item["title"]) for item in p0_items)
        lines.extend(["### 优先审（旧 AI 标记）", "", links, ""])

    p0_paths = {item["path"] for item in p0_items}

    for group in sorted(grouped):
        group_items = [item for item in grouped[group] if item["path"] not in p0_paths]
        if not group_items:
            continue
        group_items = sorted(group_items, key=lambda item: (item["priority"], str(item["path"])))
        links = "、".join(wikilink(item["path"], item["title"]) for item in group_items)
        lines.extend([f"### {group}（{len(group_items)}）", "", links])
        lines.append("")

    lines.extend(["## 刷新", "", "`python3 scripts/review_dashboard.py`"])

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate dashboard.md from pending review frontmatter.")
    parser.add_argument("--vault-root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, default=Path("dashboard.md"))
    args = parser.parse_args()

    vault_root = args.vault_root.resolve()
    out_path = args.out if args.out.is_absolute() else vault_root / args.out
    items = collect(vault_root)
    out_path.write_text(render(items), encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
