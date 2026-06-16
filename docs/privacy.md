# 隐私与脱敏规范

公开仓库、日复盘、Memory MCP 均遵守本规范。Agent 执行 sleep-memory 时 **默认启用**。

## 禁止写入长期记忆的内容

| 类别 | 示例 | 应改为 |
|------|------|--------|
| 密钥 | `sk-xxx`, API token | 「密钥在 `.env` / 密码管理器」 |
| 本机绝对路径（公开场景） | `D:\user\secret\...` | `$OBSIDIAN_VAULT` / `~/projects/foo` |
| 第三人身份 | 真实姓名、微信号 | 「友人」「同事 A」或省略 |
| 私聊全文 | 微信导出 JSON | 不索引；隔离目录 + 加密归档 |
| 家庭/健康细节 | 除非用户明确要求 | 不进 GitHub 示例 |
| 未确认 ASR | 「爸爸说…」若未核实 | `## 待你确认` |

## 「待你确认」闸门

**进待确认：**

- 语音识别不确定的专名
- Agent 推断的用户意图/关系
- 单一来源、无法交叉验证的事实
- 用户说「不要了」「删掉」的内容 — **直接删除**，不存档

**进正文（需满足至少一条）：**

- 用户明确肯定
- 多源一致（如代码已 commit + chat 一致）
- 纯技术事实（修了哪个 bug、用了哪个库）

## 敏感文件存放

推荐：

```
~/private/              # 不加入 Gety 索引
├── chat-exports/       # 聊天导出
├── recordings-raw/     # 原始录音
└── credentials/        # 本地密钥（永不进 Obsidian）
```

- 导出脚本默认输出到 `private/`，勿指向 Obsidian 根目录
- 可选：7z 密码压缩、系统全盘加密、独立 vault

## GitHub 发布检查清单

发布前自检：

- [ ] 无 `.env`、无 token 字面量
- [ ] 脚本默认路径为 `~` 或环境变量
- [ ] 示例日复盘为虚构场景
- [ ] `collect-day-sources.py` 无语雀 login 硬编码
- [ ] README 截图/日志已打码

## Memory MCP 写入准则

✅ 可写：

```text
项目 sleep-memory 仓库 github.com/Angela-letter/sleep-memory
偏好：复盘用中文
工具链：Cursor + Obsidian + Gety
```

❌ 勿写：

```text
用户住在 XX 区
API key 是 sk-...
朋友张三的电话是 ...
```

## 用户撤销权

用户任何时候可说：

- 「不要了」→ 删除对应笔记与 Memory 实体
- 「脱敏后发到 GitHub」→ 仅发布架构与虚构示例，不含私人复盘正文

本仓库即按 **架构公开 + 私人数据不出库** 原则维护。
