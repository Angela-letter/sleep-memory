# Sleep Memory · 睡眠记忆

<p align="center">
  <img src="docs/assets/architecture.png" alt="Sleep Memory 四层架构：WAKE 在线推理与 SLEEP 离线巩固" width="820">
</p>

> **不用等模型内置「睡眠」，在系统层给 Agent 装上可检索的长期记忆。**

灵感来自论文 [*Language Models Need Sleep*](https://arxiv.org/abs/2605.26099)（2026）：长程 Agent 若只在 context 里堆 token，会越来越慢、越来越贵；论文提出 **离线巩固 → 写入固定大小记忆 → 清空短期 cache**。

本项目把同一思路落在 **Cursor / Claude Code 等 Agent IDE** 上，用你已有的工具拼出四层记忆，不改模型权重。

## 为什么有用

| 痛点 | 睡眠记忆怎么做 |
|------|----------------|
| 长对话 context 爆满、变慢 | **consolidate**：摘要写进 Obsidian，新开会话用 Gety 续上 |
| 只记得当前 chat，忘了白天别的会话 | **nightly** 扫全天 `agent-transcripts`，不只复盘当前窗口 |
| 本地笔记/语雀/剪藏散落 | 脚本采集「今日增量」，合成一篇日复盘 |
| ASR/Agent 胡编进长期记忆 | **待你确认** 闸门：可疑内容默认不入库 |
| 密钥、私聊写进复盘 | 脱敏规则：只记「密钥在 `.env`」，第三人材料隔离存放 |

实测效果（个人环境，仅供参考）：

- 睡前 5 分钟产出 **300–800 字** 可读日复盘，Gety 可搜
- Context 优化：归档低频 Skill 后，新会话 token 占用可从 ~78% 降到 ~15%
- 手机录音流水线：转写 → 摘要 → `手机录音/YYYY-MM/`，与日复盘引用衔接

## 四层架构（L0–L4）

| 层 | 名称 | 载体 | 职责 |
|----|------|------|------|
| **L0** | 会话扫描 | `~/.cursor/projects/*/agent-transcripts/` | 跨 workspace 汇总「今天所有 chat」 |
| **L1** | 工作记忆 | Agent context | 只放此刻推理需要的内容 |
| **L2** | 热检索 | [Gety](https://gety.ai) CLI / MCP | 按需拉片段，不整库塞进 prompt |
| **L3** | 巩固笔记 | Obsidian Markdown | 日复盘、会话巩固、录音摘要 |
| **L4** | 实体事实 | Memory MCP | 跨会话短事实（路径、偏好、项目名） |

详见 [docs/architecture.md](docs/architecture.md)。

## 三种模式

| 模式 | 触发词 | 动作 |
|------|--------|------|
| **nightly** | 睡前复盘、今日收获 | 8 步流水线 → Obsidian `日复盘/YYYY-MM-DD.md` |
| **consolidate** | 对话太长、清 context 前 | 当前会话摘要 → `会话巩固/` |
| **recall** | 之前说过啥 | Gety + Memory 检索后回答 |

## 快速开始

### 1. 环境变量

```bash
# Obsidian 库路径（必填）
export OBSIDIAN_VAULT="$HOME/Obsidian"

# 可选：语雀采集
export YUQUE_PERSONAL_TOKEN="your_token"
export YUQUE_LOGIN="your_yuque_login"
```

### 2. 扫描今日 Cursor 会话

```bash
python scripts/scan-day-transcripts.py --date 2026-06-16 --json
```

### 3. 采集今日增量（Obsidian / Chrome / 语雀）

```bash
python scripts/collect-day-sources.py --date 2026-06-16 --json
```

### 4. 在 Cursor 里用 Skill

将 [SKILL.md](SKILL.md) 复制到 `~/.cursor/skills/sleep-memory/`，对 Agent 说：

```
睡前复盘
# 或
/sleep-memory nightly
```

## 仓库结构

```
sleep-memory/
├── README.md
├── SKILL.md                 # Cursor Agent Skill（入口）
├── docs/
│   ├── architecture.md      # 四层详解 + context 预算
│   ├── nightly-pipeline.md  # 睡前 8 步流水线
│   ├── paper-mapping.md     # 与「Language Models Need Sleep」对照
│   └── privacy.md           # 脱敏与「待你确认」规则
├── scripts/
│   ├── scan-day-transcripts.py
│   └── collect-day-sources.py
├── references/
│   ├── nightly-template.md
│   └── layers.md
└── examples/
    └── daily-review-sample.md # 虚构样例，无真实 PII
```

## 与论文的异同

| 论文（模型内化） | Sleep Memory（系统外挂） |
|------------------|--------------------------|
| 睡眠阶段改 fast weights | 睡前 Agent 写 Obsidian + Memory |
| 清空 attention cache | 新开会话 / 仅保留 recap 链接 |
| 需训练/推理栈支持 | **Obsidian + Gety + MCP** 即可落地 |
| 记忆在参数里 | 记忆在可编辑 Markdown 里 |

论文解决「模型怎么记」；本项目解决 **「人怎么记、Agent 怎么在第二天找回」**。二者互补，见 [docs/paper-mapping.md](docs/paper-mapping.md)。

## 可扩展流水线

| 场景 | 建议工具 |
|------|----------|
| 手机录音转写 | 本地 ASR / 云 API + `transcribe_*.py` |
| 录音 → 摘要 | `sleep_summarize.py` → Obsidian `手机录音/` |
| 目录索引 | 每周刷新 MOC / Dataview |
| 定时触发 | Cursor Automations 每晚固定 prompt |

## 隐私与脱敏

- 日复盘 **不粘贴** 密钥、完整 API Key、第三人私聊全文
- ASR 误听、不合常理推断 → 默认进 `## 待你确认`，你拍板后才入库
- 敏感导出放 **隔离目录**，不进入 Gety 明文索引

详见 [docs/privacy.md](docs/privacy.md)。

## License

MIT — 见 [LICENSE](LICENSE)。

## 引用

若本项目对你有帮助，可引用：

```bibtex
@misc{sleep-memory2026,
  title  = {Sleep Memory: System-Layer Consolidation for Coding Agents},
  author = {Angela-letter},
  year   = {2026},
  url    = {https://github.com/Angela-letter/sleep-memory}
}
```
