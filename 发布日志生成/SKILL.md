---
name: "发布日志生成"
description: "This skill should be used when the user wants to generate a release log document (发布日志) from a product development project progress spreadsheet (研发项目进度表). It reads Excel data, filters by requirement status, and outputs a professionally formatted Word document following the specified style rules."
---

# 发布日志生成

## 用途

根据快递100产研团队的《研发项目进度表.xlsx》，自动生成符合规范格式的发布日志 Word 文档（.docx）。

## 使用时机

用户说"生成发布日志"、"按需求状态输出文档"、"从进度表导出发布日志"或上传 `*研发项目进度表*.xlsx` 并要求整理成发布日志时，触发本技能。

## 输入文件

| 文件 | 说明 |
|------|------|
| `*研发项目进度表*.xlsx` | 主数据文件（用户上传） |
| `D:/office/项目数据汇总/发布日志/2026/2026年3月31日发布日志.docx` | 格式参照模板（已内置于脚本逻辑中，无需用户上传） |

## 数据筛选规则

- 筛选列：`需求状态` = `已发布`
- 去重依据：`禅道编号`（同一编号仅保留一条）
- Sheet名：用户上传文件中包含"0331"等迭代标识的 Sheet，由用户提供 Sheet 名

## 8个项目模块及关联关键词

| 序号 | 模块名 | 关联项目列关键词 |
|------|--------|-----------------|
| 一 | 个人产品 | `个人产品(#5)` |
| 二 | 寄件联盟 | `寄件联盟(#23)` |
| 三 | API开放平台 | `API开放平台(#12)` |
| 四 | 商家寄件 | `商家寄件(#29)` |
| 五 | 企业快递管理SaaS | `企业快递管理SaaS(#19)` |
| 六 | 电商快递管家SaaS | `电商快递管家SaaS(#1)` |
| 七 | 收件端 | `收件端(#4)` |
| 八 | 业务平台 | `业务平台(#37)` |

## 输出文档格式规范

### 文档结构

```
标题段（居中 Heading 3）
总结段（行距2.0，含所有模块名和总数）
  ↓
（模块1标题）→ 表格 → 空行
（模块2标题）→ 表格 → 空行
...
（模块8标题）→ 表格
```

### 字体

- 全文：微软雅黑 12pt
- rFonts 四项（ascii / hAnsi / eastAsia / cs）全部设为"微软雅黑"
- 字号 half-points：如 12pt → sz=24

### 标题段

- 样式：`Heading 3`，居中对齐
- 内容格式：`YYYY年M月D日发布日志`

### 总结段

- 样式：`Normal`
- 行距：2.0 倍行距（`line=480, lineRule=auto`）
- 内容模板：
  > `YYYY年M月D日迭代版本总共发布了N个需求，包括新功能及产品优化。本次发布内容包括{模块1}、{模块2}...等。具体发布内容如下：`

### 模块标题段

- 样式：`Normal`
- 行距：1.5 倍（`line=360, lineRule=auto`）
- **加粗**
- **颜色：`#0082FF`（蓝色）**
- 格式：`（一）模块名（数量个）`，所有模块均带中文序号（不区分第一个）

### 空行段

- 样式：`Normal`
- 行距：1.5 倍
- 内容：空格占位

### 表格样式

| 属性 | 值 |
|------|-----|
| 样式 | `Normal Table` |
| 列宽（twips） | 序号列 560，第2列 2417，第3列 2306，第4列 3029 |
| 行高 | 360 twips |
| 垂直对齐 | center |
| **段落行距** | **固定 20 磅（`line=400, lineRule=exact`）** |
| **边框** | 全边框（top/left/bottom/right/insideH/insideV）：`single`, `sz=4`, `color=000000` |

#### 表格列宽说明

列宽维持原文档比例（560:2417:2306:3029），总宽度按 A4 纸张（11906 twips）减去左右边距（各1800 twips）= 8306 twips，比例不变即可通过 `set_cell_width` 逐一设置。

#### 单元格边框设置

同时在两个层级设置边框（双重保险）：
- 表格级：`tblPr > tblBorders`（控制内部边框）
- 单元格级：`tcPr > tcBorders`（控制每个格子的四条边）

### 表头行

- 内容：`['序号', '需求名称', '需求分类', '需求意义与预期价值']`
- 加粗
- 序号列：居中；其余列：左对齐

### 数据行

- 序号列：数字居中
- 其余列：文字左对齐
- 不加粗，文字颜色 `#000000`

## 执行流程

1. 读取用户上传的 Excel 文件（sheet_name 由用户提供，或自动检测包含"0331"等迭代标识的 Sheet）
2. 筛选 `需求状态 == '已发布'`，按 `禅道编号` 去重
3. 按 PROJECT_KEYS 映射表将每条需求分配到对应模块
4. 按 PROJECT_ORDER 顺序遍历，对每个模块：
   - 添加空行段落（1.5倍）
   - 添加蓝色加粗模块标题（含中文序号）
   - 生成四列表格（表头 + 数据行，含边框和固定20磅行距）
5. 保存到 `D:/office/项目数据汇总/发布日志/2026/{原文件名}(整理版-已发布).docx`

## 脚本文件

执行脚本位于：`scripts/gen_release_log.py`

脚本内置以下配置常量，无需额外传参：
- `PROJECT_ORDER`：模块顺序列表
- `PROJECT_KEYS`：模块名 → 关联项目列值的映射
- `COL_WIDTHS`：表格列宽（twips）
- `BLUE_COLOR`：`'0082FF'`
- `OUTPUT_DIR`：`D:/office/项目数据汇总/发布日志/2026/`

## 常见问题

- **Sheet名不是0331**：让用户提供正确的 Sheet 名
- **文档被 Word 占用**：执行 `Get-Process WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force` 后重新保存
- **部分模块无数据**：脚本自动跳过空模块
- **输出路径不存在**：脚本会自动使用已有目录
