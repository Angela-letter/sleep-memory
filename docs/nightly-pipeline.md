# 睡前复盘流水线（8 步）

Agent 执行 `nightly` 时按此顺序操作。脚本负责 **采集**；**叙事与判断** 由 Agent 完成。

## Step 1：确定日期

- 默认：本机本地日期的「今天」
- 用户说「这几天」：逐日循环，每天一篇 `日复盘/YYYY-MM-DD.md`

## Step 2：L0 扫描 Cursor 会话

```bash
python scripts/scan-day-transcripts.py --date YYYY-MM-DD --json
```

检查：

- 是否覆盖 **所有** 当天有活动的 workspace
- 用户消息预览是否足够归纳主题（无需读完整 jsonl）

Windows 若 `--json` 控制台乱码，可：

```bash
set PYTHONIOENCODING=utf-8
python scripts/scan-day-transcripts.py --date YYYY-MM-DD --json > scan.json
```

## Step 3：采集今日增量

```bash
python scripts/collect-day-sources.py --date YYYY-MM-DD --json
```

输出含：

- Obsidian：当日新建/修改的 md（排除模板、日复盘自身）
- Chrome：当日书签/历史（若配置）
- 语雀：当日新建/更新文档（需 `YUQUE_PERSONAL_TOKEN`）

## Step 4：可选 — 日程 / 剪贴板 / 录音

| 源 | 方式 |
|----|------|
| 日历 | 钉钉/飞书 MCP 或 API（需用户自行配置） |
| 录音 | 扫描 `手机录音/YYYY-MM/` 当日新增 |
| 剪贴板 | 一般不自动采集，避免隐私风险 |

采集失败项记入 `## 待补充`，不阻塞落盘。

## Step 5：去重与主题聚类

将 L0 + Step 3–4 的信息按 **项目/主题** 合并，避免同一 bug 在三个 chat 里写三遍。

## Step 6：按模板写叙事

使用 [references/nightly-template.md](../references/nightly-template.md)。

要求：

- 第一人称或客观第三人称，**可读**
- 每条收获尽量附 **可点击路径或仓库链接**（脱敏后）
- 代码/命令用 fenced block

## Step 7：「待你确认」闸门

以下内容 **默认只进 `## 待你确认`**，不进正文与 Memory：

- ASR 转写中明显误听的专名
- Agent 推断但用户未明确肯定的事实
- 涉及第三人的敏感社交内容
- 可能错误的配置值

用户确认后，Agent 在后续会话中更新笔记并删除待确认项。

## Step 8：落盘与 Memory

1. 写入 `日复盘/YYYY/YYYY-MM-DD.md`（已存在则 **追加**「批量补录」段，不覆盖全文）
2. Memory MCP：仅写入 3–8 条 **短事实**（项目名、决策、路径占位）
3. 可选：更新月回顾 MOC

## 质量自检清单

- [ ] 当天每个有消息的 Cursor workspace 都已提及或说明「无实质进展」
- [ ] 无 API Key / token / 第三人全名
- [ ] 有「明日可续」或「未竟事项」至少 0–3 条
- [ ] 待确认与正文分离

## 定时自动化（可选）

Cursor Automations 示例 prompt：

```
执行 sleep-memory nightly：日期=今天，先跑两个脚本，再写 Obsidian 日复盘。
```

建议时间：睡前 30 分钟；失败时次日补跑 `--date` 指定日期。
