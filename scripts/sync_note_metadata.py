#!/usr/bin/env python3
"""Sync Obsidian note frontmatter and build a metadata index."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
from pathlib import Path


STANDARD_KEYS = [
    "title",
    "created",
    "updated",
    "tags",
    "aliases",
    "content_origin",
    "ai_model",
    "human_reviewed",
    "reviewed_at",
]

SKIP_EXACT = {
    "AGENTS.md",
    "CLAUDE.md",
}

SKIP_PREFIXES = (
    ".agents/",
    ".claude/",
    ".git/",
    ".obsidian/",
    ".trash/",
    "Excalidraw/",
    "raw_sources/repos/",
    "scripts/",
    "tmp/",
)

SKIP_DIR_NAMES = {
    "__pycache__",
}

INDEX_PATH = Path("tmp/note-metadata-index.json")


def today() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d")


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout


def staged_markdown_files(root: Path) -> list[Path]:
    output = run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM", "--", "*.md"],
        root,
    )
    return [root / line for line in output.splitlines() if line.strip()]


def all_markdown_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.md"))


def rel_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def is_note(path: Path, root: Path) -> bool:
    rel = rel_path(path, root)
    if rel in SKIP_EXACT:
        return False
    if rel != "raw_sources/index.md" and rel.startswith("raw_sources/"):
        return False
    if any(rel.startswith(prefix) for prefix in SKIP_PREFIXES):
        return False
    return not any(part in SKIP_DIR_NAMES for part in Path(rel).parts)


def split_frontmatter(text: str) -> tuple[dict[str, object], str, bool]:
    if not text.startswith("---\n"):
        return {}, text, False

    end = text.find("\n---", 4)
    if end == -1:
        return {}, text, False

    raw = text[4:end]
    body = text[end + len("\n---") :]
    if body.startswith("\n"):
        body = body[1:]
    return parse_frontmatter(raw), body, True


def parse_scalar(value: str) -> object:
    value = value.strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "[]":
        return []
    if value == '""':
        return ""
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def parse_frontmatter(raw: str) -> dict[str, object]:
    data: dict[str, object] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            value = line[4:].strip()
            current = data.setdefault(current_key, [])
            if isinstance(current, list):
                current.append(value)
            continue
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        current_key = key
        if raw_value:
            data[key] = parse_scalar(raw_value)
        else:
            data[key] = []
    return data


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value == "":
        return '""'
    text = str(value)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return text
    escaped = text.replace('"', '\\"')
    return f'"{escaped}"'


def render_frontmatter(data: dict[str, object]) -> str:
    lines = ["---"]
    for key in STANDARD_KEYS:
        value = data.get(key)
        if isinstance(value, list):
            if value:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: []")
        else:
            lines.append(f"{key}: {yaml_scalar(value)}")

    for key in sorted(k for k in data if k not in STANDARD_KEYS):
        value = data[key]
        if isinstance(value, list):
            if value:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: []")
        else:
            lines.append(f"{key}: {yaml_scalar(value)}")

    lines.append("---")
    return "\n".join(lines) + "\n"


def default_title(path: Path) -> str:
    if path.name == "README.md":
        return "README"
    return path.stem


def sync_file(path: Path, root: Path, ai_model: str, reset_review: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    data, body, _ = split_frontmatter(text)
    now = today()
    existed_body = bool(body.strip())

    data["title"] = data.get("title") or default_title(path)
    data["created"] = data.get("created") or data.get("date") or now
    data["updated"] = now
    data["tags"] = data.get("tags") if isinstance(data.get("tags"), list) else []
    data["aliases"] = data.get("aliases") if isinstance(data.get("aliases"), list) else []

    old_model = str(data.get("ai_model") or "")
    model = ai_model or old_model
    data["ai_model"] = model
    if model:
        data["content_origin"] = "mixed" if existed_body else "ai"
    else:
        data["content_origin"] = data.get("content_origin") or "human"

    if reset_review:
        data["human_reviewed"] = False
        data["reviewed_at"] = ""
    else:
        data["human_reviewed"] = bool(data.get("human_reviewed", False))
        data["reviewed_at"] = data.get("reviewed_at") or ""

    new_text = render_frontmatter(data) + "\n" + body.lstrip("\n")
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def collect_headings(body: str) -> list[dict[str, object]]:
    headings: list[dict[str, object]] = []
    for lineno, line in enumerate(body.splitlines(), start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append(
                {
                    "level": len(match.group(1)),
                    "title": match.group(2),
                    "line": lineno,
                }
            )
    return headings


def build_index(root: Path) -> None:
    notes: list[dict[str, object]] = []
    for path in all_markdown_files(root):
        if not is_note(path, root):
            continue
        text = path.read_text(encoding="utf-8")
        data, body, has_frontmatter = split_frontmatter(text)
        notes.append(
            {
                "path": rel_path(path, root),
                "title": data.get("title") or default_title(path),
                "created": data.get("created") or "",
                "updated": data.get("updated") or "",
                "tags": data.get("tags") if isinstance(data.get("tags"), list) else [],
                "aliases": data.get("aliases") if isinstance(data.get("aliases"), list) else [],
                "content_origin": data.get("content_origin") or "",
                "ai_model": data.get("ai_model") or "",
                "human_reviewed": bool(data.get("human_reviewed", False)),
                "reviewed_at": data.get("reviewed_at") or "",
                "has_frontmatter": has_frontmatter,
                "headings": collect_headings(body)[:20],
            }
        )

    output = {
        "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "root": str(root),
        "notes": notes,
    }
    path = root / INDEX_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stage_paths(root: Path, paths: list[Path]) -> None:
    rels = [rel_path(path, root) for path in paths]
    if rels:
        subprocess.run(["git", "add", "--", *rels], cwd=root, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Obsidian note metadata.")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--staged", action="store_true", help="Use staged Markdown files.")
    parser.add_argument("--stage", action="store_true", help="Stage changed notes after syncing.")
    parser.add_argument("--index", action="store_true", help="Build tmp/note-metadata-index.json.")
    parser.add_argument("--all", action="store_true", help="Sync all ordinary notes.")
    parser.add_argument("--ai-model", default=os.environ.get("WIKI_AI_MODEL", ""))
    parser.add_argument(
        "--keep-reviewed",
        action="store_true",
        help="Keep human_reviewed/reviewed_at instead of marking changed notes unreviewed.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if args.staged:
        candidates = staged_markdown_files(root)
    elif args.all:
        candidates = all_markdown_files(root)
    else:
        candidates = [(root / path).resolve() for path in args.paths]

    changed: list[Path] = []
    for path in candidates:
        if path.exists() and path.suffix == ".md" and is_note(path, root):
            if sync_file(path, root, args.ai_model, not args.keep_reviewed):
                changed.append(path)

    if args.index:
        build_index(root)

    if args.stage:
        stage_paths(root, changed)

    if changed:
        print("synced metadata:")
        for path in changed:
            print(f"- {rel_path(path, root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
