---
name: "natural-wallpaper-poster"
description: "This skill should be used when the user wants to automatically generate daily natural healing-style wallpapers for iPhone and post them to Xiaohongshu (小红书) platform. It handles wallpaper creation, watermark addition, scheduled posting, content generation, and error handling with retry mechanisms."
---

# Natural Wallpaper Poster - 山野收容所

自动化生成自然治愈风格iPhone壁纸并发布到小红书的技能。

## 账号配置

| 项目 | 内容 |
|------|------|
| 账号名称 | 山野收容所 |
| 账号简介 | 收容那些想逃离喧嚣的时刻。用一张壁纸的时间，躲进山野里透口气。 |
| 风格定位 | 自然创意大片风格，不追踪热点，专注自然风景表达 |

## 工作流程

### 完整发布流程

```
1. 生成壁纸提示词
   ↓
2. 调用AI绘图API生成壁纸
   ↓
3. 添加水印（可选）
   ↓
4. 生成小红书文案
   ↓
5. 发布到小红书
   ↓
6. 发送完成通知
```

### 定时任务配置

创建每日定时自动化任务：

```python
automation_config = {
    "name": "山野收容所-每日壁纸发布",
    "prompt": """
    执行完整的壁纸发布流程：
    1. 从 prompt_templates.md 读取提示词模板，生成一张自然治愈风格的壁纸提示词
    2. 调用 image_gen 工具生成壁纸图片，尺寸为 1179x2556 (9:16竖屏)
    3. 保存壁纸图片
    4. 从 xiaohongshu_content.md 读取文案模板，根据今日壁纸主题生成小红书文案
    5. 使用小红书技能发布内容，附带图片和文案
    6. 如遇错误，使用 error_handling.md 中的策略处理
    """,
    "schedule": {
        "type": "recurring",
        "rrule": "FREQ=DAILY;BYHOUR=8;BYMINUTE=0"  # 每天早上8点发布
    },
    "cwds": ["当前工作目录"],
    "status": "ACTIVE"
}
```

## 壁纸生成

### iPhone壁纸尺寸标准

| 机型 | 竖屏壁纸尺寸 | 比例 |
|------|-------------|------|
| iPhone 16 Pro Max | 2868 × 1320 | 约2.17:1 |
| iPhone 16 Pro | 2622 × 1206 | 约2.17:1 |
| iPhone 16 / 15 Pro | 2556 × 1179 | 约2.17:1 |
| **推荐通用尺寸** | **1179 × 2556** | **9:19.5** |

### 壁纸风格要求

**必须遵守的视觉规范：**
- 自然创意大片风格，强调光影、构图、故事感
- 简约、留白多、要素少，意味无穷的美感
- 画面颜色对比强烈，饱和度高
- **禁止出现任何人物元素**（人像、背影、群众等）
- **禁止有枝叶等遮挡物**
- 画面纯净、整洁、简约

**自然元素类别：**
- 🏔️ 山川（雪峰日出、高山草甸、峡谷晨雾等）
- 🌊 海洋（粉色沙滩、星空倒映、悬崖海浪等）
- 🌲 森林（晨雾森林、极光森林、萤火虫夜等）
- ⭐ 星空（银河星空、流星划过、极光爆发等）
- 🌸 花卉（薰衣草田、樱花盛开、玫瑰花园等）
- 🌅 日出日落（海边日落、沙漠日落、草原晨曦等）

### 生成壁纸的方法

1. **加载提示词模板**：读取 `references/prompt_templates.md`
2. **组合提示词**：
   - 从模板库中选择一个自然场景
   - 添加构图、光影、色彩要求
   - 强调纯净、无人物的技术规格
3. **调用image_gen工具**：
   ```
   prompt: "巍峨雪峰与金色日出，阳光穿透云雾..."
   size: "1179x2556"
   quality: "high"
   ```
4. **保存壁纸图片**

## 水印添加

### 水印配置

```python
WATERMARK_CONFIG = {
    "text": "山野收容所",
    "position": "bottom_right",
    "opacity": 60,        # 透明度 0-100
    "font_size": 28,
    "color": "#FFFFFF"     # 白色
}
```

### 添加水印方法

使用 `scripts/add_watermark.py` 脚本：

```bash
python scripts/add_watermark.py \
    --input wallpaper.png \
    --output wallpaper_with_wm.png \
    --text "山野收容所" \
    --position bottom_right \
    --opacity 60
```

## 小红书内容生成

### 文案结构

```
1. 情感共鸣开场
   - 触动心灵的句子
   - 与壁纸主题呼应

2. 画面描述
   - 诗意语言描绘壁纸
   - 带入感要强

3. 情感升华
   - 一句话触动心灵

4. 实用信息
   - 壁纸尺寸提示
   - 保存方式说明

5. 话题标签
   - 固定话题：#山野收容所 #自然壁纸 #治愈系
   - 动态话题：根据当日主题添加
```

### 话题标签库

**必带话题：**
- #山野收容所
- #自然壁纸
- #治愈系壁纸
- #手机壁纸

**可选话题：**
- #自然风景 #星空 #大海 #森林 #日出日落 #山川 #花海
- #解压 #放松 #正能量
- #值得收藏 #高清壁纸无水印

## 小红书发布

### 发布方法

使用小红书技能 (`xiaohongshu`) 发布内容：

1. **上传图片**：使用 upload_file 工具上传壁纸图片
2. **准备内容**：
   - title: 简短吸睛的标题
   - body: 根据文案模板生成的正文
   - tags: 话题标签列表
3. **发布**：
   - 调用小红书发布接口
   - 等待确认

### 发布时机

| 时段 | 适合内容 | 效果 |
|------|----------|------|
| 07:00-08:00 | 日出主题 | 契合主题，阅读量较高 |
| 12:00-13:00 | 简约风格 | 午间浏览，收藏率高 |
| 18:00-19:00 | 日落主题 | 黄金时段，互动率高 |
| 21:00-22:00 | 星空主题 | 契合主题，适合晚安 |

## 错误处理

### 错误类型与策略

| 错误 | 处理方式 |
|------|----------|
| 图片生成失败 | 更换提示词重试，使用备用模板 |
| API超时 | 等待5分钟后重试，降低请求频率 |
| 网络错误 | 立即重试×3，等待网络恢复 |
| 发布失败 | 等待10分钟后重试，保存草稿待手动 |
| 水印失败 | 跳过水印继续，记录日志 |
| 认证失效 | 重新授权，通知用户 |

### 重试配置

```python
RETRY_CONFIG = {
    "max_retries": 3,
    "retry_delay": 300,  # 5分钟
    "exponential_backoff": True
}
```

### 通知机制

**成功通知**：壁纸发布成功后发送确认
**失败通知**：包含错误原因、重试次数、预计下次尝试时间
**重试通知**：每次重试时发送进度更新

## 定时自动化配置

### 创建每日壁纸发布自动化

```
使用 automation_update 工具创建自动化任务：

name: 山野收容所-每日壁纸发布
prompt: 执行完整的壁纸生成与小红书发布流程，包括生成自然治愈风格壁纸、添加水印、发布内容
scheduleType: recurring
rrule: FREQ=DAILY;BYHOUR=8;BYMINUTE=0
cwds: [工作目录]
status: ACTIVE
validFrom: 2026-04-02
```

### 推荐发布时间

- **标准发布**：每天 08:00-09:00
- **备选发布**：每天 18:00-19:00
- **星空主题日**：每天 21:00-22:00

## 参考资源

| 文件 | 用途 |
|------|------|
| `references/prompt_templates.md` | 壁纸提示词模板库 |
| `references/xiaohongshu_content.md` | 小红书文案模板库 |
| `references/error_handling.md` | 错误处理与通知机制 |
| `scripts/generate_wallpaper.py` | 壁纸生成辅助脚本 |
| `scripts/add_watermark.py` | 水印添加工具脚本 |

## 使用示例

### 立即执行一次壁纸发布

1. 读取提示词模板，生成壁纸主题
2. 使用 image_gen 工具生成图片
3. 添加水印
4. 生成文案并发布到小红书

### 创建每日定时任务

1. 使用 automation_update 工具
2. 设置每天的发布时间
3. 启用自动化

### 处理发布失败

1. 检查错误日志
2. 根据 error_handling.md 确定策略
3. 执行重试或手动干预
4. 发送通知给用户
