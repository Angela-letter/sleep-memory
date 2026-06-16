# 与论文 *Language Models Need Sleep* 的对照

论文：[Language Models Need Sleep](https://arxiv.org/abs/2605.26099)（arXiv:2605.26099，2026）

核心主张：长程 Agent 在 **线推理** 中积累的 attention 状态会退化；应在 **离线睡眠阶段** 把经验巩固进 **固定容量** 的长期记忆，并 **清空短期 cache**，以恢复速度并保持能力。

## 概念映射

| 论文概念 | Sleep Memory 实现 |
|----------|---------------------|
| Wake（在线） | Cursor 多会话 coding；L1 context |
| Sleep（离线） | 睡前 `nightly`；`consolidate` 归档 |
| Fast weights / 短期 | 当前 chat + tool 结果 |
| Consolidated memory | Obsidian `日复盘/`、`会话巩固/` |
| Fixed-size memory | Memory MCP 短实体 + 精选 recap（非全文） |
| Clear cache | 新开会话；context 仅带 recap 链接 |
| Retrieval at wake | Gety `recall`；打开 Obsidian 链接 |

## 论文解决 vs 本项目解决

| 维度 | 论文 | Sleep Memory |
|------|------|--------------|
| 记忆存在哪 | 模型参数 / 专用记忆模块 | 文件系统 + MCP |
| 谁可编辑 | 需重新训练或专用 API | 人可直接改 Markdown |
| 可审计性 | 黑箱 | Git / Obsidian 历史 |
| 部署门槛 | 推理框架改造 | Skill + 脚本 + 现有工具 |
| 跨设备 | 跟模型走 | 跟 Obsidian 同步走 |

## 互补而非替代

- 若未来 IDE 内置「会话睡眠」，本项目的 **L3 笔记** 仍可做人可读日记与团队知识库。
- 论文强调 **容量固定**；实践上 Obsidian 可增长，但 **Memory L4** 应保持精简，模拟 fixed-size。
- 论文的 offline 是 **批量梯度式巩固**；这里是 **LLM 摘要式巩固** — 信息有损，靠「待你确认」降低幻觉入库。

## 延伸阅读（系统层记忆）

- [MemGPT / Letta](https://github.com/letta-ai/letta) — 分层 memory + 分页
- [Zep](https://github.com/getzep/zep) — 会话记忆服务
- Cursor Rules / Skills — 静态长期指令（与本项目动态 recap 互补）

## 一句话

> 论文问：**模型** 怎样才能睡个好觉；  
> Sleep Memory 问：**你的 Agent 工作流** 怎样才能睡个好觉。
