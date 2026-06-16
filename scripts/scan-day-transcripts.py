#!/usr/bin/env python3
"""扫描指定日期的 Cursor agent-transcripts（跨 workspace）。

用法:
  python scripts/scan-day-transcripts.py
  python scripts/scan-day-transcripts.py --date 2026-06-14
  python scripts/scan-day-transcripts.py --json

Windows 控制台 UTF-8:
  set PYTHONIOENCODING=utf-8
  python scripts/scan-day-transcripts.py --json > scan.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path.home() / ".cursor" / "projects"
QUERY_RE = re.compile(r"<user_query>\s*(.*?)\s*</user_query>", re.S)
# 系统/子代理注入消息，跳过不计入用户意图
SKIP_PREFIXES = (
    "Briefly inform the user",
    "The beginning of the above subagent",
)


def extract_user_text(content: list) -> str:
    for c in content:
        if c.get("type") != "text":
            continue
        t = c.get("text", "")
        m = QUERY_RE.search(t)
        text = (m.group(1) if m else t).strip()
        if any(text.startswith(p) for p in SKIP_PREFIXES):
            return ""
        return text
    return ""


def scan_day(target: date) -> list[dict]:
    sessions = []
    if not ROOT.exists():
        return sessions
    for jsonl in ROOT.rglob("agent-transcripts/*/*.jsonl"):
        if "subagents" in jsonl.parts:
            continue
        mtime = datetime.fromtimestamp(jsonl.stat().st_mtime)
        if mtime.date() != target:
            continue
        project = jsonl.parts[jsonl.parts.index("projects") + 1]
        user_msgs = []
        for line in jsonl.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("role") != "user":
                continue
            text = extract_user_text(obj.get("message", {}).get("content", []))
            if text and len(text) > 3:
                user_msgs.append(text.replace("\n", " ").strip())
        if not user_msgs:
            continue
        sessions.append(
            {
                "project": project,
                "id": jsonl.parent.name,
                "time": mtime.strftime("%H:%M"),
                "count": len(user_msgs),
                "first_query": user_msgs[0][:300],
                "queries": user_msgs[:8],
                "transcript": str(jsonl),
            }
        )
    sessions.sort(key=lambda x: x["time"])
    return sessions


def to_markdown(sessions: list[dict], target: date) -> str:
    lines = [f"## 全天 Cursor 会话 · {target.isoformat()}", ""]
    lines.append(f"共 **{len(sessions)}** 个会话（来源 `~/.cursor/projects/*/agent-transcripts/`）")
    lines.append("")
    for i, s in enumerate(sessions, 1):
        lines.append(f"### {i}. {s['time']} · `{s['project']}` · `{s['id'][:8]}`")
        lines.append(f"- 首问：{s['first_query']}")
        if s["count"] > 1:
            lines.append(f"- 共 {s['count']} 条用户消息")
        lines.append(f"- 日志：`{s['transcript']}`")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="扫描某日 Cursor 会话")
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    target = date.fromisoformat(args.date)
    sessions = scan_day(target)
    if args.json:
        # Windows GBK 控制台友好
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass
        print(json.dumps(sessions, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(sessions, target))


if __name__ == "__main__":
    main()
