# 四层记忆架构（Skill 速查）

与 [docs/architecture.md](../docs/architecture.md) 一致，供 Agent 快速查阅。

## L0 会话扫描

- 路径：`~/.cursor/projects/*/agent-transcripts/*/*.jsonl`
- 工具：`scripts/scan-day-transcripts.py`
- **nightly 必跑**，避免漏掉其他 workspace 的 chat

## L1 工作记忆

- 载体：当前 context
- 预算：系统规则 + 当前代码 + 少量 recap 链接；勿塞整库

## L2 热检索

- 载体：Gety CLI / MCP
- 约定：关键词 query、Top 5、`--update-time-from` 过滤今日
- 始终 cite 文件路径

## L3 巩固笔记

```
日复盘/YYYY/YYYY-MM-DD.md
会话巩固/*.md
手机录音/YYYY-MM/*.md   # 可选
```

## L4 实体事实

- 载体：Memory MCP
- 存：项目名、路径占位、工具偏好
- 不存：长文、密钥、未确认推断

## 与论文

| 论文 | 本架构 |
|------|--------|
| KV cache | L1 |
| 睡眠巩固 | nightly / consolidate |
| 长期记忆 | L3 + L4 |
| 清空 cache | 新会话 + recap 链接 |
