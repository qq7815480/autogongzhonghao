# Image Prompt Templates

## GPT Image 2 Prompt 最佳实践

### 中文内容要求

所有图片中的文字、标注、标题必须是中文。prompt 末尾必须加：
```
所有文字标注必须使用中文。
```

### 手绘信息图模板

```
A hand-drawn infographic illustration about [主题].
Style: hand-drawn sketch with ink on cream paper, clean lines,
simple icons and diagrams, professional infographic layout.
Key data points: [具体数字/术语]
All text labels must be in Chinese (中文).
```

### 文艺手绘场景模板 (与 warm-editorial 排版匹配)

```
A hand-drawn illustration about [主题].
Style: warm cream paper background, black ink lines with slight wobble,
soft pastel color blocks, sketch-notes aesthetic.
Atmosphere: literary, gentle, magazine-like.
Elements: [具体视觉元素]
All text must be in Chinese (中文).
```

## baoyu-article-illustrator Prompt 结构

baoyu-article-illustrator 会自动生成结构化 prompt，包含：

- **ZONES**: 信息分区（数据、对比、总结）
- **LABELS**: 文章实际数据（数字、术语、引用）
- **COLORS**: 语义色彩映射（红色=警告，绿色=增长）
- **STYLE**: 风格特征
- **ASPECT**: 宽高比

不需要手动写 prompt，skill 会自动处理。

## 封面图 Prompt

baoyu-cover-image 自动生成，包含：
- 文章标题（中文）
- 视觉隐喻（基于文章主题）
- 风格配置（scene + earth + hand-drawn）
- 2.35:1 宽高比
