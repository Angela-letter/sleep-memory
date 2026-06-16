# 精选库工作流 · Gety × sleep-memory × 专题货架

本文档把 **Gety 全盘发现**、**精选库专题归档**、**sleep-memory 睡前巩固** 串成一条可长期运行的流水线。

## 一、为什么需要精选库（在四层之外）

sleep-memory 原四层：

| 层 | 职责 |
|----|------|
| L0–L1 | 会话与工作记忆 |
| L2 Gety | **发现**散落文件 |
| L3 Obsidian | **按时间**巩固（日复盘） |
| L4 Memory | 短事实 |

**缺口**：高价值**源文件**按**主题**归档、给 Agent 一张「地图」。  
精选库补 **L2b（专题检索）** + **L3b（专题索引）**：

| 层 | 名称 | 载体 |
|----|------|------|
| L2b | 专题热检索 | Gety `Folder: 精选库` connector |
| L3b | 专题地图 | `{精选库}/{专题}/_index.md` |

```
         ┌─────────────────────────────────────────┐
         │  L2  Gety 全盘（各盘符、CloudDrive 等）   │  找得到
         └──────────────────┬──────────────────────┘
                            │ 命中高价值
                            ▼
         ┌─────────────────────────────────────────┐
         │  L2b 精选库 folder + _index.md          │  搜得准
         └──────────────────┬──────────────────────┘
                            │ 睡前一句话
                            ▼
         ┌─────────────────────────────────────────┐
         │  L3  Obsidian 日复盘（按日）              │  记得住
         │  L3b 专题 _index（按主题）                │  找得回原件
         └─────────────────────────────────────────┘
```

## 二、目录与默认路径

| 项目 | 示例路径（请用环境变量覆盖） |
|------|------------------------------|
| 精选库根 | `$CURATED_LIBRARY_ROOT` 或 `~/curated-library/` |
| 待归档 | `$CURATED_LIBRARY_ROOT/inbox/` |
| 示例专题 | `$CURATED_LIBRARY_ROOT/example-topic/` |
| Obsidian 复盘 | `$OBSIDIAN_VAULT/日复盘/` |
| sleep-memory 仓库 | 本仓库 clone 路径 |

可用环境变量覆盖（建议写入个人 `.env` 或 Memory MCP，**勿提交到 Git**）：

```bash
export CURATED_LIBRARY_ROOT="$HOME/curated-library"
export OBSIDIAN_VAULT="$HOME/Obsidian"
```

## 三、首次搭建（一次性，约 15 分钟）

### 1. 创建目录（已完成可跳过）

```
$CURATED_LIBRARY_ROOT/
├── README.md
├── _MOC.md
├── templates/
├── inbox/
└── example-topic/
    └── _index.md
```

### 2. 注册 Gety 连接器

```powershell
gety connector add "$env:CURATED_LIBRARY_ROOT" --name "Folder: 精选库"
gety connector list
```

确认列表中出现 `Folder: 精选库`，`searchable_doc_count` 随索引增长。

### 3. 种子专题索引

在 `example-topic/_index.md` 填「权威原件路径表」。  
**不必立刻搬家**——索引表记录「权威原件在哪」即可。

### 4. Memory MCP（可选）

写入一条实体事实，方便跨会话 recall：

- 实体：`精选库`
- 观察：`根路径 $CURATED_LIBRARY_ROOT；示例专题 example-topic/_index.md；Gety connector 名 Folder: 精选库`

## 四、日常流程

### 白天：发现 → inbox

1. Cursor / Gety 搜到好资料（真题、考点汇总、讲义）
2. 任选其一：
   - **轻量**：在对应专题 `_index.md` 的「待入库」加一行路径
   - **标准**：复制或硬链接到 `inbox/`
   - **重量**：复制到 `{专题}/sources/` 并更新索引表

硬链接示例（不占双倍空间，同盘符）：

```powershell
New-Item -ItemType HardLink `
  -Path "$env:CURATED_LIBRARY_ROOT/inbox/note-summary.md" `
  -Target "$env:OBSIDIAN_VAULT/Yuque/your-repo/note-summary.md"
```

### 问 Agent 时：检索顺序

```
1. Read {专题}/_index.md
2. gety search "<query>" -c "Folder: 精选库"
3. 不足再 gety search "<query>" 全盘
4. gety doc / Read 具体文件
```

### 睡前：sleep-memory nightly

在日复盘模板中填写 `## 精选库`（见 `references/nightly-template.md`）：

- 今日新加入 inbox 或更新了哪份 `_index.md`
- 不必重复全文，只记**路径 + 一句话用途**

### 周末：整理 inbox

1. 清空 `inbox/` → 归入 `{专题}/sources/` 或仅保留索引路径
2. 更新 `_MOC.md` 专题列表
3. 可选：Obsidian 月回顾里链到精选库变更

## 五、CloudDrive / 网盘挂载

- 挂载到本地盘符且在 Gety 扫描范围内 → **可索引**
- 按需下载：正文索引取决于读取时是否成功拉取
- **精选库建议**：常搜的 5–10 份文件**复制或硬链接到 `sources/`**（真本地），网盘只当备份

## 六、与 Gety 被替代时的兼容性

| 资产 | Gety 没了还在吗 |
|------|----------------|
| `精选库/**/*.md` 索引 | ✅ |
| `sources/` 原件 | ✅ |
| Obsidian 日复盘 | ✅ |
| Memory MCP 路径事实 | ✅ |
| 全盘「偶然搜到」能力 | ❌ 需换 Listary+Recoll 或新工具 |

**精选库 + Obsidian 是主权数据；Gety 是可选加速器。**

## 七、新建专题 checklist

- [ ] 建 `{专题}/_index.md`（复制 `templates/topic-index.md`）
- [ ] 在 `_MOC.md` 加一行
- [ ] 填「权威文件路径表」
- [ ] 首批 3–5 个文件进 `sources/` 或路径索引
- [ ] `gety search` 试搜验证

## 八、相关文件

| 文件 | 说明 |
|------|------|
| [references/curated-index-template.md](../references/curated-index-template.md) | 专题 `_index` 模板 |
| [references/nightly-template.md](../references/nightly-template.md) | 日复盘含 `## 精选库` |
| [references/layers.md](../references/layers.md) | L2b/L3b 架构 |
| [examples/curated-library-modian-sample.md](../examples/curated-library-modian-sample.md) | 专题索引样例 |
