#!/usr/bin/env python3
"""Build a heading outline index for one Markdown file."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
FENCE_RE = re.compile(r"^[ \t]*(```+|~~~+)")


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def clean_heading(raw: str) -> str:
    return raw.strip().rstrip("#").strip()


def parse_frontmatter(lines: list[str]) -> dict[str, Any]:
    if not lines or lines[0].strip() != "---":
        return {"exists": False, "start_line": None, "end_line": None}

    for idx, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return {"exists": True, "start_line": 1, "end_line": idx}

    return {"exists": True, "start_line": 1, "end_line": None, "malformed": True}


def parse_headings(lines: list[str], body_start_line: int) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []
    in_fence = False

    for line_no, line in enumerate(lines, start=1):
        if line_no < body_start_line:
            continue

        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue

        if in_fence:
            continue

        match = HEADING_RE.match(line)
        if not match:
            continue

        level = len(match.group(1))
        title = clean_heading(match.group(2))

        while stack and stack[-1]["level"] >= level:
            stack.pop()

        parent = stack[-1] if stack else None
        path = [*(parent["path"] if parent else []), title]
        node = {
            "id": f"h{len(headings) + 1}",
            "level": level,
            "title": title,
            "line": line_no,
            "parent_id": parent["id"] if parent else None,
            "path": path,
            "children": [],
        }

        if parent:
            parent["children"].append(node["id"])

        headings.append(node)
        stack.append(node)

    for idx, node in enumerate(headings):
        next_peer_or_parent = None
        for later in headings[idx + 1 :]:
            if later["level"] <= node["level"]:
                next_peer_or_parent = later
                break

        node["section_start_line"] = node["line"] + 1
        node["section_end_line"] = (
            next_peer_or_parent["line"] - 1 if next_peer_or_parent else len(lines)
        )
        node["insert_after_line"] = node["section_end_line"]

    return headings


def build_tree(headings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {node["id"]: {**node, "children": []} for node in headings}
    roots: list[dict[str, Any]] = []

    for node in headings:
        current = by_id[node["id"]]
        parent_id = node["parent_id"]
        if parent_id:
            by_id[parent_id]["children"].append(current)
        else:
            roots.append(current)

    return roots


def relative_path(path: Path, root: Path) -> str:
    resolved = path.resolve()
    root_resolved = root.resolve()
    try:
        return str(resolved.relative_to(root_resolved))
    except ValueError:
        return str(path)


def build_index(md_path: Path, vault_root: Path) -> dict[str, Any]:
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    frontmatter = parse_frontmatter(lines)
    body_start_line = (frontmatter.get("end_line") or 0) + 1 if frontmatter["exists"] else 1
    headings = parse_headings(lines, body_start_line)

    return {
        "schema": "md-outline-index/v1",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "file": {
            "path": str(md_path),
            "relative_path": relative_path(md_path, vault_root),
            "sha1": sha1(text),
            "line_count": len(lines),
        },
        "frontmatter": frontmatter,
        "body_start_line": body_start_line,
        "headings": headings,
        "tree": build_tree(headings),
    }


def default_output_path(md_path: Path, vault_root: Path) -> Path:
    safe_name = relative_path(md_path, vault_root).replace("/", "__")
    return vault_root / "tmp" / "md-outline-index" / f"{safe_name}.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse one Markdown file and output a JSON heading outline."
    )
    parser.add_argument("markdown_file", type=Path)
    parser.add_argument("--vault-root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, help="Output JSON path.")
    parser.add_argument("--stdout", action="store_true", help="Print JSON instead of writing a file.")
    args = parser.parse_args()

    md_path = args.markdown_file
    if not md_path.is_absolute():
        md_path = (args.vault_root / md_path).resolve()

    index = build_index(md_path, args.vault_root)
    payload = json.dumps(index, ensure_ascii=False, indent=2)

    if args.stdout:
        print(payload)
        return 0

    out_path = args.out or default_output_path(md_path, args.vault_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(payload + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
