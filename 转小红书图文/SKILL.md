# 转小红书图文

将完整文章转换为小红书 3:4 图文切片——不提炼、不抽象、原文完整保留，字号自适应填满每张切片。**只输出切片图，不保留长图。**

## 核心差异（对比 article-to-html）

| 维度 | article-to-html | 转小红书图文 |
|------|-----------------|-------------|
| 内容策略 | 提炼核心论点，3-6 张切片 | **全文转换，完整保留原文** |
| 切片数量 | 3-6 张 | ≤ 16 张 |
| 字号策略 | 固定最小 30px | **动态自适应，正文 ≥ 24px** |
| 标题样式 | 依赖模板 | **加粗 + 放大 + 变色，强制区分正文** |
| 留白策略 | 首中尾差异化（60/16/48） | **固定规则：上下各 1 行 + 行距 1×字号 + 段距 2×字号** |
| 截图方式 | 完整长图 → slice-image 切割 | **逐卡 boundingBox 截图，直接输出切片** |
| 输出产物 | 长图 + 切片 + HTML | **仅切片图 + HTML（参考保留）** |
| 风格匹配 | 9 种参考风格 | 9 种风格 + 内容关键词智能匹配 |

## 设计理念

**你是排版引擎，不是内容编辑器。** 文章原文一个字都不能少，但要把文字以最佳阅读体验嵌入 3:4 画布。

- **完整性第一** — 不等同于信息图的精简提炼，原文必须完整保留
- **字号自适应** — 每张切片的内容量不同，字号动态调整填满空间，正文最小 24px 保证手机端清晰可读
- **标题与正文分离** — 文章标题、分段标题用加粗+放大+变色突出（标题默认 84px 加粗 + 主色高亮），正文保持可读性
- **固定间距规则** — 正文行间距 = 1 倍字号（`line-height: 2.0`，行盒 = 2×字号，行间空白 = 1×字号），段落间距 = 2 倍正文字号，切片顶部/底部各留 1 行字高度的空白

## 工作流程

```
用户提供文章（标题 + 正文）
    ↓
① 内容分析 — 识别标题层级（H1/H2/H3）、段落、引用块、列表
    ↓
② 风格匹配 — 根据文章关键词匹配视觉风格（配色、字体、装饰）
    ↓
③ 切片计算 — 运行 generate.py，自动计算字号和切片分配
    ↓
④ HTML 生成 — 生成自包含 HTML，标题加粗放大变色，正文自适应字号
    ↓
⑤ 后处理 — post-process.sh 一键：fix-html.js 修复 CSS + 字号兜底 + 截图 → 直接输出切片图
```

### 步骤③ 切片计算算法

```
输入: 文章段落列表，每段有类型（title/h2/h3/p/quote）
      目标画布 1080×1440px，内容区宽 984px（左右各 48px 留白）

间距规则（固定，不可变）：
  - 正文行间距 = 1 倍字号（line-height: 2.0）
  - 段落间距 = 2 倍正文字号
  - 切片顶部留白 = 1 行字高度（= 正文字号 px）
  - 切片底部留白 = 1 行字高度（= 正文字号 px）

对每张切片:
  1. 以默认字号（正文38px，标题84px，H2 52px，H3 32px）开始
  2. 计算切片总高度 = 顶部留白 + Σ(块高度 + 段间距) + 底部留白（最后一块不加段间距）
  3. 如果总高度 > 1440px:
     → 减小正文字号（最小 24px）
     → 如果仍超出，将尾部段落溢出到下一张切片
  4. 记录本切片的最终字号配置
  5. 切片数量由内容自然决定，不强制凑整
  6. 如果切片数已达 16 且仍有内容 → 报错提示
```

### 标题层级渲染规范

| 层级 | 字号范围 | 加粗 | 颜色策略 | 示例 |
|------|---------|------|---------|------|
| 文章主标题 H1 | 64-96px | ✅ 必加粗 | 主色高亮（如 #C62828） | 大标题独占首切片顶部 |
| 章节标题 H2 | 40-56px | ✅ 必加粗 | 辅色（如 #1565C0） | 段落前的分节标题 |
| 小节标题 H3 | 28-40px | ✅ 必加粗 | 辅色变体 | 子段落的小标题 |
| 正文 P | 24-64px（自适应） | ❌ 正常 | 正文色（深灰 #2D2D2D） | 自适应填充 |
| 引用/金句 | 24-48px | ✅ 斜体+加粗 | 强调色 + 左边框 | 独立引用块 |

## 风格匹配规则

根据文章内容关键词自动匹配视觉风格：

| 关键词 | 匹配风格 | 配色基调 | 字体 |
|--------|---------|---------|------|
| 科技/AI/编程/代码/互联网 | 暗色科技 | 深色底 + 霓虹绿 #00FFB2 | IBM Plex Mono |
| 商业/财经/股票/投资/企业 | 商务简报 | 深蓝主色 + 白底 | DM Sans + 思源黑体 |
| 生活/旅行/美食/日常/手账 | 手账笔记 | 暖纸色 + 多彩便签 | ZCOOL KuaiLe |
| 文学/小说/故事/人物/非虚构 | 杂志编辑 | 暖白底 + 衬线标题 | Playfair Display + 思源宋体 |
| 新闻/时事/社会/热点 | 报纸新闻 | 纸色底 + 黑+红色 | Playfair + 思源宋体 |
| 设计/艺术/创意/潮流 | 孟菲斯波普 | 撞色 #FFD166+#EF476F+#06D6A0 | Rubik |
| 自然/环保/极简/冥想 | 极简北欧 | 暖白+苔绿#6B8F71+赤陶 | Outfit |
| 历史/复古/怀旧/经典 | 复古未来 | 深棕底+琥珀色+绿磷光 | Space Mono |
| 教程/学习/笔记/知识 | 实验室蓝图 | 灰白网格+鼠尾草绿 | 系统默认等宽 |

**混搭规则**：如果文章跨越多个领域，优先使用占比最高的风格，并在首切片使用该风格的主视觉。

## 技术约束

### 画布规范

```css
/* 切片画布 */
.slice-card {
  width: 1080px;
  height: 1440px;           /* 固定高度 */
  box-sizing: border-box;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;  /* 从上到下自然排列 */
  /* padding 由各切片按字号动态设置 inline style:
     padding: <body_fs>px 48px <body_fs>px 48px;  （上下各 1 行字高度） */
}

/* 可用内容宽度: 984px = 1080 - 48×2 */
```

### 间距规则（固定）

所有切片统一遵守，不可通过字号调节规避：

- **顶部留白** = 1 行字高度 = 正文字号 px（`padding-top`）
- **底部留白** = 1 行字高度 = 正文字号 px（`padding-bottom`）
- **正文行间距** = 1 倍字号（`line-height: 2.0`，行盒 = 2×字号，行间空白 = 1×字号）
- **段落间距** = 2 倍正文字号（`margin-bottom`，最后一段为 0）
- **左右留白** = 48px（固定）

- **切片数量动态** — 内容自然分页，该几张就几张，不强制凑整

### 标题强制样式（必须遵守）

```css
/* 文章主标题 — 首切片顶部，加粗放大变色 */
.article-title {
  font-size: 84px;       /* 动态范围 64-96px，大幅突出 */
  font-weight: 900;      /* 强制加粗 */
  color: var(--accent);  /* 主色调高亮 */
  line-height: 1.2;
  margin-bottom: 0;      /* 由 inline style 统一设 2×正文字号段间距 */
}

/* 章节标题 H2 */
.section-title {
  font-size: 52px;       /* 动态范围 40-56px */
  font-weight: 800;      /* 强制加粗 */
  color: var(--secondary); /* 辅色区分 */
  line-height: 1.3;
  margin: 0;
}

/* 小节标题 H3 */
.subsection-title {
  font-size: 32px;       /* 动态范围 28-40px */
  font-weight: 700;      /* 强制加粗 */
  color: var(--secondary-light);
  line-height: 1.35;
  margin: 0;
}

/* 正文段落 — 自适应字号，固定行距 */
.body-text {
  font-size: 38px;       /* 动态范围 24-64px */
  font-weight: 400;      /* 正常字重 */
  color: #2D2D2D;        /* 深灰，非纯黑 */
  line-height: 2.0;      /* 行距 = 1 倍字号（行盒 = 2×字号） */
  margin: 0 0 2em 0;     /* 段落间距 = 2 倍字号（最后一段 margin-bottom: 0） */
  text-align: justify;
  overflow-wrap: break-word;
  word-break: normal;
}

/* 引用块 */
.blockquote {
  font-size: 28px;       /* 动态范围 24-48px */
  font-style: italic;
  font-weight: 600;
  color: var(--accent);
  border-left: 6px solid var(--accent);
  padding: 10px 20px;
  margin: 0;
  background: var(--card-bg);
  border-radius: 0 8px 8px 0;
}
```
> 🔒 **内联样式保障**：标题元素的 `font-weight` 和 `color` 同时通过内联样式输出（优先级最高），确保即使 Google Fonts 加载失败或 CSS 被覆盖，标题仍然保持加粗变色效果。

### 禁止事项

| 写法 | 后果 |
|------|------|
| `.slice-card { height: auto }` | 高度不确定，切片对不齐 |
| `.slice-card { min-height: 1440px }` | 内容不足时底部大片空白 |
| `body { padding: 40px }` | 四周大白边 |
| `.container { max-width: 800px }` | 两侧空白 |
| `.slice-card { overflow: visible }` | 内容溢出到相邻切片 |
| `.slice-card::before / ::after` | 过渡渐变伪元素（已禁用） |
| 正文 < 24px | 手机上完全看不清 |
| 标题不加粗 | 层次混乱，无法区分标题和正文 |
| 切片 > 16 张 | 超过小红书单篇发布上限 |
| 擅自删减原文 | 违背"完整转换"核心原则 |
| CSS columns / 多栏布局 | 窄画布下阅读体验差 |
| 输出完整长图 | 技能定位只输出切片图 |

## HTML 结构模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { margin: 0; padding: 0; background: transparent; }
  .container { width: 1080px; margin: 0; padding: 0; }
  
  .slice-card {
    width: 1080px; height: 1440px;
    box-sizing: border-box; overflow: hidden;
    position: relative; display: flex;
    flex-direction: column; justify-content: flex-start;
    /* padding 由各切片 inline style 动态设置 */
    /* 背景色由风格决定 */
  }
  
  /* ... 标题和正文样式由 generate.py 动态注入 ... */
</style>
</head>
<body>
<div class="container">
  <div class="slice-card" data-slice="1">
    <!-- 第1张切片内容：文章标题 + 开头段落 -->
  </div>
  <div class="slice-card" data-slice="2">
    <!-- 第2张切片内容 -->
  </div>
  <!-- ... 最多16张 ... -->
</div>
</body>
</html>
```

## 目录结构

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 本文件 |
| `scripts/generate.py` | **核心**：内容分析 + 切片计算 + HTML 生成 |
| `scripts/fix-html.js` | CSS 修复脚本（统一 padding:0px 48px，标题加粗兜底） |
| `scripts/post-process.sh` | 后处理一键脚本（版本文件夹 + fix-html + 字号兜底 + 截图） |
| `scripts/screenshot.js` | **逐卡截图**：遍历 .slice-card 逐个 boundingBox 截图，直接输出切片图 |
| `scripts/slice-image.js` | 保留兼容（不再主动调用） |

## 输出产物

```
E:\codefile\trae\mp_article\小红书图文\
└── {标题}-{YYYYMMDDHHMM}-V{N}\
    ├── .meta.txt              ← 元信息（标题/时间戳/版本号）
    ├── index.html             ← 生成的 HTML（参考保留）
    └── index_slice_01.png     ← 小红书 3:4 切片 × N 张
        index_slice_02.png
        ...
```

> **不再输出 index_full.png 完整长图。** 截图脚本直接逐卡 boundingBox 截图，产物就是切片图。

## 技术参数速查

| 参数 | 值 | 来源 |
|------|----|------|
| 画布尺寸 | 1080 × 1440px | generate.py |
| 上下留白 | 各 1 行字高度 = 正文字号 px | generate.py（动态 inline style） |
| 左右留白 | 48px | generate.py |
| 可用内容宽度 | 984px | 1080 - 48×2 |
| 正文字号范围 | 24-64px | generate.py |
| 正文字号默认 | 38px | generate.py |
| 标题字号范围 | 64-96px | generate.py |
| 标题字号默认 | 84px | generate.py |
| H2 字号范围 | 40-56px | generate.py |
| H2 字号默认 | 52px | generate.py |
| H3 字号范围 | 28-40px | generate.py |
| H3 字号默认 | 32px | generate.py |
| 引用字号范围 | 24-48px | generate.py |
| 引用字号默认 | 28px | generate.py |
| 正文行高系数 | 2.0（行间距 = 1×字号） | generate.py |
| 段落间距 | 2×正文字号 | generate.py |
| 切片顶部留白 | 1×正文字号 | generate.py |
| 切片底部留白 | 1×正文字号 | generate.py |
| 最大切片数 | 16 | generate.py |
| 字号策略 | 仅缩小适配（不放大填充） | generate.py |
| Emoji 宽度系数 | 0.88（同 CJK） | generate.py (estimate_width) |

> ⚠️ **Emoji 宽度估算**：🔄🎧🔥💎 等补充平面字符在 `count_chars()` 中归入 `wide_symbols`，宽度系数 0.88（与 CJK 相同），不再是 0.25。此前 emoji 被误归为 "other" 导致高度严重低估，含大量 emoji 的切片（如推荐歌单）会溢出截断。

## 与 article-to-html 规则同步

本技能的以下规则与 article-to-html 保持同步（修改时需双向更新）：

| 规则 | 同步内容 | article-to-html 参考文件 |
|------|---------|--------------------------|
| 技术底线 | 截图流程、HTML 结构约束 | `rules/01-技术底线.md` |
| 截图流程 | Puppeteer 配置、Chrome 路径 | `rules/02-截图流程.md` |
| 禁止事项 | body padding、overflow、多栏等 | `rules/01-技术底线.md` |

**关键差异（不同步）**：
- article-to-html 使用差异化留白（首60/中16/尾48），本技能使用固定间距规则（上下各1行+行距1×+段距2×）
- article-to-html 输出完整长图+切片，本技能只输出切片图
- article-to-html 正文字号 ≥ 30px，本技能 ≥ 24px（全文转换需要更大字号弹性）

## 使用示例

```
用户输入：
  标题：「深圳湾的最后一盏灯」
  正文：「2026年3月，深圳南山科技园...」（全文 3000 字）

执行步骤：
  1. 识别风格 → "文学/小说/故事" → 杂志编辑风格
  2. 解析文章 → 1个H1 + 4个H2 + 30个段落
  3. 切片计算 → 通过 generate.py 按固定间距规则（行距1×/段距2×/上下各1行留白）自动分配到 N 张切片
  4. 生成 HTML → 标题 84px 加粗 红色，H2 52px 加粗 深蓝，正文 line-height:2.0 自适应字号
  5. 后处理 → post-process.sh：fix-html.js 修复 + 字号兜底 + screenshot.js 截图
  6. 交付 → N 张 1080×1440 小红书切片图（数量由内容自然决定）
```
