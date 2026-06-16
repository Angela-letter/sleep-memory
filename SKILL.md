---
name: sleep-memory
description: >-
  【睡眠记忆·分层架构】L0–L4 + 精选库 L2b/L3b：Gety 全盘 / 专题索引 / Obsidian 巩固 / Memory MCP。
  睡前日复盘：汇总当天文档、对话与收获，写入 Obsidian 并更新长期记忆。
  Use when user says 睡眠记忆、四层记忆、睡前复盘、日复盘、今日收获、巩固记忆、
  sleep memory、nightly recap、daily review、记忆架构、清空 context 前摘要，或长对话/长任务结束前需要归档。
argument-hint: "[nightly|consolidate|recall] [optional date YYYY-MM-DD]"
---

# 睡眠记忆（Sleep Memory）

灵感来自 [*Language Models Need Sleep*](https://arxiv.org/abs/2605.26099)：**离线巩固 → 清空工作记忆 → 日后按需检索**。
在系统层落地为四层（含 L0 会话扫描），不依赖新模型架构。

完整文档见本仓库 [README.md](README.md)。

## 四层分工

| 层 | 名称 | 载体 | 何时用 |
|----|------|------|--------|
| L0 | 会话扫描 | `~/.cursor/projects/*/agent-transcripts/` | nightly 必须：当天**所有** chat |
| L1 | 工作记忆 | Agent context | 只放「此刻推理需要」的内容 |
| L2 | 热检索 | Gety CLI / MCP | 全盘发现；按需拉片段 |
| L2b | 专题检索 | Gety `Folder: 精选库` | 读 `_index.md` 后精准搜 |
| L3 | 巩固笔记 | Obsidian Markdown | 日复盘、会话巩固 |
| L3b | 专题地图 | `精选库/{专题}/_index.md` | 按主题索引原件路径 |
| L4 | 实体事实 | Memory MCP | 跨会话短事实 |

详见 [references/layers.md](references/layers.md) 与 [docs/architecture.md](docs/architecture.md)。

## 默认路径（环境变量覆盖）

| 变量 | 默认 |
|------|------|
| `OBSIDIAN_VAULT` | `~/Obsidian` |
| `CURATED_LIBRARY_ROOT` | `~/curated-library`（个人路径仅放环境变量，勿写进公开仓库） |
| 日复盘 | `{vault}/日复盘/YYYY/YYYY-MM-DD.md` |
| 会话巩固 | `{vault}/会话巩固/YYYY-MM-DD-{slug}.md` |
| 手机录音摘要 | `{vault}/手机录音/YYYY-MM/`（可选流水线） |

---

## 模式路由

| 意图 | 模式 | 动作 |
|------|------|------|
| 睡前复盘、今日收获 | **nightly** | 8 步流水线 |
| 对话太长、清 context 前 | **consolidate** | 摘要 → `会话巩固/` |
| 查旧事 | **recall** | Gety + Memory 检索 |

---

## 睡前日复盘（nightly）⛔ 主流程

```
- [ ] Step 1: 确定日期 ⛔
- [ ] Step 2: L0 扫描全天 Cursor 会话 ⛔
- [ ] Step 3: 采集今日增量（Obsidian / Chrome / 语雀）⛔
- [ ] Step 4: 日程（钉钉/飞书 MCP，可选）
- [ ] Step 5: L2 Gety 补充扫描
- [ ] Step 6: 合成并写入 Obsidian ⚠️
- [ ] Step 7: L4 Memory MCP（短事实）
- [ ] Step 8: 向用户汇报
```

### Step 2: L0 扫描

```bash
python scripts/scan-day-transcripts.py --date YYYY-MM-DD --json
```

对每个会话：读 `first_query` / `queries`；需结论时只读 jsonl **末尾** assistant 消息。

### Step 3: 采集增量

```bash
export OBSIDIAN_VAULT="$HOME/Obsidian"   # 按需
python scripts/collect-day-sources.py --date YYYY-MM-DD --json
```

语雀需 `YUQUE_PERSONAL_TOKEN` + `YUQUE_LOGIN`。

### Step 4: 日程

使用已配置的钉钉/飞书 Calendar MCP 或 API。不可用 → 标注「日程待补充」，**不编造**。

### Step 5: Gety

```bash
gety search "" --sort-by update_time --sort-order descending --update-time-from <today_T00> --json
```

Top 5–8 即可；无结果则以 Step 3 Obsidian mtime 为准。

### Step 6: 写入 Obsidian

- 模板：[references/nightly-template.md](references/nightly-template.md)（含 `## 精选库`）
- 已存在 → 文末追加 `## 晚间补充`，不删用户手写
- 若今日涉及资料归档/专题索引，填写 `## 精选库`；无则写「无」
- 隐私：[docs/privacy.md](docs/privacy.md)

### 待你确认 ⚠️

ASR 误听、过度推断、第三人敏感内容 → 只进 `## 待你确认`，等你拍板后才入正文与 Memory。

### Step 7: Memory MCP

仅 3–8 条短事实；`search_nodes` 查重后 `create_entities` / `add_observations`。

---

## consolidate / recall

- **consolidate**：`{vault}/会话巩固/{date}-{slug}.md`，frontmatter `tags: [睡眠摘要, 会话巩固]`
- **recall**：`gety search` → `gety doc` → `memory search_nodes`，cite 来源路径

---

## 反模式

- ❌ 只复盘当前会话、不扫 agent-transcripts
- ❌ 把密钥/第三人私聊写进复盘或 Memory
- ❌ 编造日程或 Gety 无依据的「收获」
- ❌ 可疑 ASR 内容未经确认写入正文

## 脚本

- `scripts/scan-day-transcripts.py`
- `scripts/collect-day-sources.py`

## 附加资源

- [精选库工作流](docs/curated-library-workflow.md)
- [日复盘模板](references/nightly-template.md)
- [专题索引模板](references/curated-index-template.md)
- [流水线详解](docs/nightly-pipeline.md)
- [论文对照](docs/paper-mapping.md)
