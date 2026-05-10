# 公众号视觉风格指南

## 整体调性: 现代文艺杂志

封面和排版统一为"现代文艺"风格，避免封面文艺但正文科技蓝的割裂感。

## 封面图 (baoyu-cover-image)

| 维度 | 值 | 说明 |
|---|---|---|
| type | scene | 场景感，有叙事性 |
| palette | earth | 自然有机色调：森林绿、鼠尾草、大地棕 |
| rendering | hand-drawn | 手绘笔触，不完美线条，纸张质感 |
| text | title-only | 只显示文章标题 |
| mood | subtle | 低对比度，柔和克制 |
| aspect | 2.35:1 | 微信封面推荐比例 (900×383) |
| language | zh | 中文 |

配置文件: `~/.baoyu-skills/baoyu-cover-image/EXTEND.md`

## 排版主题: warm-editorial

| 元素 | 样式 |
|---|---|
| 背景 | 米白 `#fbf7f0` |
| 正文 | 宋体衬线, 15.5px, 行高 1.9 |
| 标题 | 栗色 `#5a2f1a`, 底部金色分割线 |
| 引用块 | 浅米黄底 + 金色左边框 + 斜体 |
| 代码块 | 深色 `#2b2420` |
| 强调 | 栗色加粗 + 金色下划线 |
| 链接 | 栗色 + 底部金色虚线 |

配置文件: `wechat-publisher.yaml` → `theme: "warm-editorial"`

## 配图风格

文章内插图使用 `hand-drawn-blue` 风格 (蓝色墨线手绘)。
贴图模式 (newspic) 使用 `infographic-warm` 风格。

## 视觉语言一致性原则

1. 封面 (hand-drawn earth) + 排版 (warm-editorial) = 同一"文艺杂志"调性
2. 配图 (hand-drawn blue) 是文章内插图，风格可以跟封面略有差异
3. 所有图片中的文字、标注、标题**必须是中文**
