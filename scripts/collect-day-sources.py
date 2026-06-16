#!/usr/bin/env python3
"""采集睡前复盘所需的「今日增量」数据源。

用法:
  python scripts/collect-day-sources.py
  python scripts/collect-day-sources.py --date 2026-06-14 --json

环境变量:
  OBSIDIAN_VAULT     Obsidian 库路径（默认 ~/Obsidian）
  YUQUE_PERSONAL_TOKEN / YUQUE_TOKEN  语雀 API
  YUQUE_LOGIN        语雀用户 login（采集知识库文档时需要）

输出：Obsidian 今日改动、Chrome 新书签、语雀文档/小记、采集失败项。
钉钉/飞书日程需单独配置 MCP 或 API。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

TZ = timezone(timedelta(hours=8))
CHROME_EPOCH_OFFSET = 11_644_473_600  # seconds from 1601-01-01 to Unix epoch


def default_vault() -> Path:
    env = os.environ.get("OBSIDIAN_VAULT")
    if env:
        return Path(env)
    return Path.home() / "Obsidian"


def parse_day(s: str | None) -> date | None:
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(TZ).date()


def chrome_us_to_dt(us: int) -> datetime:
    return datetime.fromtimestamp(us / 1_000_000 - CHROME_EPOCH_OFFSET, tz=TZ)


def scan_obsidian(vault: Path, target: date) -> dict[str, list[dict]]:
    skip_dirs = {".obsidian", ".trash", ".git"}
    all_files: list[dict] = []
    clippings: list[dict] = []
    if not vault.exists():
        return {"all": all_files, "clippings": clippings, "error": f"vault not found: {vault}"}
    for p in vault.rglob("*.md"):
        rel_parts = p.relative_to(vault).parts
        if any(part in skip_dirs or part.startswith(".") for part in rel_parts):
            continue
        try:
            st = p.stat()
        except OSError:
            continue
        mtime = datetime.fromtimestamp(st.st_mtime, tz=TZ)
        if mtime.date() != target:
            continue
        rel = "/".join(rel_parts)
        item = {
            "time": mtime.strftime("%H:%M"),
            "path": rel,
            "size": st.st_size,
            "is_clipping": rel.startswith("Clippings/"),
        }
        all_files.append(item)
        if item["is_clipping"]:
            clippings.append(item)
    all_files.sort(key=lambda x: x["time"])
    clippings.sort(key=lambda x: x["time"])
    return {"all": all_files, "clippings": clippings}


def scan_chrome_bookmarks(target: date) -> list[dict]:
    local = os.environ.get("LOCALAPPDATA", "")
    if not local:
        return []
    user_data = Path(local) / "Google" / "Chrome" / "User Data"
    if not user_data.exists():
        return []
    found: list[dict] = []

    def walk(node: Any, profile: str) -> None:
        if isinstance(node, dict):
            if node.get("type") == "url":
                us = int(node.get("date_added", 0) or 0)
                if us:
                    dt = chrome_us_to_dt(us)
                    if dt.date() == target:
                        found.append(
                            {
                                "time": dt.strftime("%H:%M"),
                                "name": node.get("name", ""),
                                "url": node.get("url", ""),
                                "profile": profile,
                            }
                        )
            for ch in node.get("children") or []:
                walk(ch, profile)
        elif isinstance(node, list):
            for ch in node:
                walk(ch, profile)

    for bm in user_data.rglob("Bookmarks"):
        profile = bm.parent.name
        try:
            data = json.loads(bm.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for root in data.get("roots", {}).values():
            walk(root, profile)
    found.sort(key=lambda x: (x["time"], x["name"]))
    return found


def yuque_request(path: str, token: str, params: dict | None = None) -> Any:
    import urllib.parse

    url = "https://www.yuque.com/api/v2" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = Request(
        url,
        headers={"X-Auth-Token": token, "User-Agent": "sleep-memory-collect"},
    )
    with urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def scan_yuque(target: date, login: str | None = None) -> dict[str, Any]:
    token = os.environ.get("YUQUE_PERSONAL_TOKEN") or os.environ.get("YUQUE_TOKEN")
    if not token:
        return {"error": "missing YUQUE_PERSONAL_TOKEN", "docs": [], "notes": []}
    login = login or os.environ.get("YUQUE_LOGIN", "")
    if not login:
        return {"error": "missing YUQUE_LOGIN", "docs": [], "notes": []}

    docs_today: list[dict] = []
    books = yuque_request(f"/users/{login}/repos", token).get("data", [])
    for book in books:
        offset = 0
        while True:
            payload = yuque_request(
                f"/repos/{book['id']}/docs",
                token,
                {"offset": offset, "limit": 100},
            )
            batch = payload.get("data") or []
            if not batch:
                break
            for doc in batch:
                u = parse_day(doc.get("updated_at"))
                c = parse_day(doc.get("created_at"))
                if u == target or c == target:
                    docs_today.append(
                        {
                            "book": book.get("name"),
                            "namespace": book.get("namespace"),
                            "title": doc.get("title"),
                            "slug": doc.get("slug"),
                            "created": str(c) if c else "",
                            "updated": str(u) if u else "",
                            "url": f"https://www.yuque.com/{book.get('namespace')}/{doc.get('slug')}",
                        }
                    )
            meta = payload.get("meta") or {}
            if not meta.get("has_more"):
                break
            offset += len(batch)

    notes_today: list[dict] = []
    page = 1
    while True:
        payload = yuque_request("/notes", token, {"page": page, "limit": 50})
        data = payload.get("data")
        notes = data.get("notes", []) if isinstance(data, dict) else []
        if not notes:
            break
        for note in notes:
            u = parse_day(note.get("published_at"))
            c = parse_day((note.get("content") or {}).get("updated_at"))
            if u == target or c == target:
                abstract = (note.get("content") or {}).get("abstract") or ""
                abstract = abstract.replace("<!doctype lake>", "").replace("<p>", "").replace("</p>", "")[:120]
                notes_today.append(
                    {
                        "id": note.get("doclet_id") or note.get("id"),
                        "preview": abstract,
                        "created": str(c) if c else "",
                        "updated": str(u) if u else "",
                    }
                )
        meta = payload.get("meta") or {}
        if not meta.get("has_more"):
            break
        page += 1

    docs_today.sort(key=lambda x: x.get("updated", ""), reverse=True)
    notes_today.sort(key=lambda x: x.get("updated", ""), reverse=True)
    return {"docs": docs_today, "notes": notes_today}


def to_markdown(report: dict, target: date) -> str:
    lines = [f"# 今日增量采集 · {target.isoformat()}", ""]
    obs = report["obsidian"]
    if obs.get("error"):
        lines.append(f"## Obsidian（跳过：{obs['error']}）")
    else:
        lines += [
            f"## Obsidian（{len(obs['all'])} 个 .md，其中 Clippings {len(obs['clippings'])}）",
            "",
        ]
        for item in obs["all"][:30]:
            tag = " [剪藏]" if item["is_clipping"] else ""
            lines.append(f"- {item['time']} `{item['path']}`{tag}")
        if len(obs["all"]) > 30:
            lines.append(f"- … 另有 {len(obs['all']) - 30} 个")

    lines += ["", f"## Chrome 新书签（{len(report['chrome'])}）", ""]
    if report["chrome"]:
        for b in report["chrome"]:
            lines.append(f"- {b['time']} [{b['name']}]({b['url']}) · `{b['profile']}`")
    else:
        lines.append("- 无")

    yq = report["yuque"]
    if yq.get("error"):
        lines += ["", f"## 语雀（跳过：{yq['error']}）"]
    else:
        lines += ["", f"## 语雀知识库文档（{len(yq['docs'])}）", ""]
        for d in yq["docs"][:20]:
            lines.append(f"- [{d['book']}] {d['title']} · {d['url']}")
        lines += ["", f"## 语雀小记（{len(yq['notes'])}）", ""]
        for n in yq["notes"][:20]:
            lines.append(f"- {n.get('preview') or '(空)'}")
    lines += ["", "## 钉钉 / 飞书日程", "", report.get("calendar_note", "")]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="采集睡前复盘今日增量")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--vault", default=None, help="Obsidian vault（默认 OBSIDIAN_VAULT 或 ~/Obsidian）")
    args = parser.parse_args()
    target = date.fromisoformat(args.date)
    vault = Path(args.vault) if args.vault else default_vault()

    report = {
        "date": target.isoformat(),
        "vault": str(vault),
        "obsidian": scan_obsidian(vault, target),
        "chrome": scan_chrome_bookmarks(target),
        "yuque": scan_yuque(target),
        "calendar_note": (
            "日程未配置：请通过钉钉/飞书 MCP 或 API 补充，或于日复盘手动填写。"
        ),
    }

    if args.json:
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(report, target))


if __name__ == "__main__":
    main()
