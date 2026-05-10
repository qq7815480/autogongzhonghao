# Baoyu Skills Integration

## 安装的外部 skills

### baoyu-cover-image (封面图)

- 路径: `~/.hermes/skills/baoyu-cover-image/`
- 配置: `~/.baoyu-skills/baoyu-cover-image/EXTEND.md`
- 来源: `https://github.com/JimLiu/baoyu-skills/tree/main/skills/baoyu-cover-image`

**当前配置** (文艺手绘风格):
```yaml
preferred_type: scene          # 场景叙事
preferred_palette: earth       # 自然有机色调
preferred_rendering: hand-drawn # 手绘笔触
preferred_text: title-only     # 只显示标题
preferred_mood: subtle         # 低对比度柔和
default_aspect: "2.35:1"      # 微信封面 900×383
quick_mode: true
language: zh
preferred_image_backend: auto
```

**调用**: `--quick --aspect 2.35:1 --lang zh --text title-only`

### baoyu-article-illustrator (正文配图)

- 路径: `~/.hermes/skills/baoyu-article-illustrator/`
- 配置: `~/.baoyu-skills/baoyu-article-illustrator/EXTEND.md`
- 来源: `https://github.com/JimLiu/baoyu-skills/tree/main/skills/baoyu-article-illustrator`

**当前配置** (手绘笔记风):
```yaml
preferred_style:
  name: hand-drawn
preferred_palette: warm
language: zh
default_output_dir: imgs-subdir
preferred_image_backend: auto
```

**调用**: 传入 article.md 路径，`--quick` 模式自动分析并生成配图

## 安装方法

```bash
cd ~/.hermes/skills
git clone --depth 1 --filter=blob:none --sparse https://github.com/JimLiu/baoyu-skills.git baoyu-skills-tmp
cd baoyu-skills-tmp
git sparse-checkout set skills/baoyu-cover-image skills/baoyu-article-illustrator
cp -R skills/baoyu-cover-image ~/.hermes/skills/
cp -R skills/baoyu-article-illustrator ~/.hermes/skills/
rm -rf ~/.hermes/skills/baoyu-skills-tmp
```

## 风格协调原则

封面、正文配图、排版三者必须视觉语言统一：

| 用户偏好 | 封面 (cover-image) | 配图 (article-illustrator) | 排版 (theme) |
|---|---|---|---|
| 文艺手绘 | scene+earth+hand-drawn | hand-drawn+warm | warm-editorial |
| 科技感 | hero+cool+digital | vector+cool | refined-blue |
| 极简高级 | minimal+mono+flat-vector | minimal-flat+mono | minimal-mono |

用户选择封面风格后，自动推导配图和排版风格。
