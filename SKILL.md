---
name: wechat-publisher
description: |
  微信公众号文章自动创作与发布工具。给定话题或参考文章，自动搜索素材、撰写文章、生成配图、排版美化、反 AI 检测、发布到草稿箱。

  触发场景：
  - 用户提到"公众号"、"微信文章"、"推文"、"公号"、"发文"等关键词
  - 用户要求写文章并发布到微信
  - 用户要求搜索某个话题并写成公众号文章
  - 用户提到"草稿箱"、"群发"等微信公众号操作
---

# 微信公众号文章自动创作与发布

工作目录: `~/.hermes/skills/wechat-publisher/sunwork/`
脚本目录: `~/.hermes/skills/wechat-publisher/scripts/`

## 前置条件

已配置: AppID/AppSecret 已写入 `wechat-publisher.yaml`，API 连通已验证。
依赖: `requests`, `pyyaml` (已安装)。
生图: 使用 Hermes 内置 `image_generate` 工具，provider 为 `openai-codex` (GPT Image 2)。
生图细节: `references/codex-oauth-image-gen.md`

## 完整工作流程

### 阶段一: 理解需求与收集素材

目标: 搞清楚用户到底要什么，同时采集**真人味原料**。

1. **分析用户输入**
   - 用户给了参考文章/文档: 读完，提取核心观点、独特素材、数据、案例
   - 用户只给话题: 快速确认"这篇发哪个号?有没有个人亲历的细节可以加进去?"
   - **尽量问出用户能提供的具体细节**: 具体人名、时间、金额、产品版本、场景、踩过的坑 —— 这些是反 AI 检测的最重要原料。

   > **⛔ 参考文章是"原料"不是"模板"**
   >
   > 当用户给了参考文章（无论一篇还是多篇），**绝对不能**：
   > - 跟着参考文章的结构走（小节划分、标题顺序）
   > - 原文复制任何句子或段落（哪怕换几个词）
   > - 做"两篇文章的总结/整合"
   >
   > **必须做到**：
   > 1. **提取素材**：从参考文章中提取核心数据、独特案例、关键观点、有价值的引用
   > 2. **丢掉结构**：不看原文的小节划分，自己重新组织文章骨架
   > 3. **用自己的话讲**：所有内容必须用自己的句式重新表达，不是"换个说法"而是"重新讲述"
   > 4. **加入"我"**：必须有自己的判断、经历、踩坑、困惑 —— 这是区分"总结"和"创作"的关键
   > 5. **必须问用户**：你对这个话题有什么亲历的细节？踩过什么坑？有什么判断是别人没说过的？
   >
   > **判断标准**：如果读完文章，读者觉得"这是两篇参考文章的总结" → 失败。如果觉得"这是老孙/豌豆四喜写的" → 成功。

   > **⛔ 文章细节规范**：
   > - **时间**：不用具体时间点（如"上周三下午"），用"最近"、"今天"等模糊时间，让读者觉得是最近发生的
   > - **案例**：不用参考文章里的小众案例（如专有项目名），换成大众常见的通用场景（如微信、Python、API）
   > - **术语**：参考文章里的专业术语要替换成更接地气的通用内容，让普通读者也能看懂

2. **识别目标账号**: 根据话题自动选账号，并加载对应 voice。也可由用户显式指定。

3. **产出**: 写入 `~/.hermes/skills/wechat-publisher/sunwork/<date-slug>/brief.md`，包含话题、目标账号、3-5 个关键词、用户提供的真实细节清单。

> **辅助 (用户偏好)**: 用户偏好先结论后展开、像聊天不像答辩、实践导向有案例步骤可执行、数据必须真实不编造、允许不确定但不硬凹。

### 阶段二: 全网信息搜索与整理

目标: 既要权威数据，也要**真人语料**(反 AI 检测的第二重原料)。

1. **权威层** (`web_search` + `web_extract` / `mcp_jina_crawl4ai_jina_read`):
   - 最新资讯 + 数据 (优先 6 个月内)
   - 相关案例 / 故事
   - 专家观点 / 官方报告 / Release Notes

2. **真人层** (**重要**): 专门搜"真人讨论"作为语料库，让文章自然带上真人句式:
   - Reddit / HackerNews / V2EX / 即刻 / 少数派的帖子原话
   - X (Twitter) 上当事人 / 员工的发言原文
   - 小红书 / 知乎的一线用户吐槽
   - 产品具体的 commit message / issue 讨论

3. **信息筛选与交叉验证**: 关键数据多源交叉，具体到数字 / 名字 / 时间 / 产品版本号。

4. **产出**: `~/.hermes/skills/wechat-publisher/sunwork/<date-slug>/research.md`，每个素材标来源，区分"权威层"和"真人层"。

### 阶段 2.5: 素材分类与多媒体处理

在撰写文章之前，对阶段二收集到的素材做**媒体类型分类**，决定每类素材的处理方式。**核心原则: 有原图/原视频的，优先用原始素材，不要用 AI 生成的抽象图替代具体内容。**

#### 分类规则

| 素材类型 | 处理方式 | 理由 |
|---|---|---|
| **软件截图 / 产品界面 / 操作步骤截图** | 保留原图，下载后直接上传微信 CDN 嵌入文章 | 截图本身就是内容的一部分，AI 手绘图无法替代具体的 UI 细节和操作指引 |
| **视频内容 (YouTube/B站/腾讯视频等)** | 嵌入视频播放代码或视频截图+引导 | 视频信息密度远高于静态图 |
| **数据图表 / 信息图 / 对比图** | 保留原图 (如果清晰且有引用价值) | 原始数据可视化比 AI 重绘更准确 |
| **产品 Logo / 品牌素材** | 保留原图 | 品牌标识不应被 AI 重新绘制 |
| **纯文字观点 / 数据 / 概念** | 生成手绘配图 (baoyu-article-illustrator) | 没有现成视觉素材，需要 AI 辅助可视化 |
| **抽象场景 / 情绪描述** | 生成手绘配图 | 补充视觉叙事 |

#### 视频嵌入规则

微信公众号对外部视频有严格限制:

| 视频来源 | 处理方式 |
|---|---|
| **微信视频号** | 可直接嵌入 (最推荐) |
| **腾讯视频** | 用 `<iframe>` 嵌入 |
| **YouTube / B站 / 其他** | **不能直接嵌入**。改用: ① 视频封面截图 + 文字说明 + "阅读原文"放链接; 或 ② 如果有视频号搬运版则嵌入视频号 |

#### 执行方式

1. 从 `research.md` 中标记每条素材的媒体类型
2. 对需要保留原图的素材: 下载到 `images/` 目录，**必须用 `original-` 或 `screenshot-` 前缀命名**（如 `original-seed-benchmark.png`、`screenshot-wechat-settings.jpg`），以便阶段四识别
3. 对需要嵌入视频的: 记录视频源和嵌入方式
4. 在阶段三撰写时，在文章对应位置标注 `![描述](images/original-xxx.png)` 或视频嵌入标记
5. 阶段四 (baoyu-article-illustrator) 只为**没有原始视觉素材的段落**生成配图

> **⚠️ 不要犯的错误**: 文章讲的是某个软件的操作步骤，配图却是一张抽象手绘 —— 读者看不懂，内容和图对不上。

> **⛔ 参考文章里的原图必须优先使用**: 如果用户给了参考文章，文章里的截图、对比图、数据图、产品界面等**必须直接用原图**，不能用 baoyu-article-illustrator 生成的抽象手绘图替代。原图承载的是具体的信息（错误截图、对比结果、UI细节），AI 生成图无法替代。只有当参考文章中**没有对应视觉素材**的纯文字段落，才用 baoyu-article-illustrator 生成配图。

### 阶段三: 撰写骨架稿 (第一轮)

目标: 按结构写出初稿。**允许这一稿有 AI 味**，下一阶段专门负责"人味化"。

#### 文章结构模板 (Markdown)

> Markdown 中的第一个 `# 标题` 会被 html_converter 自动跳过 (微信顶部已显示标题，不重复)。

```markdown
# 标题 (抓眼球，15-25 字)

> 摘要引言 (1-2 句话，会显示在分享卡片中)

## 开篇
(用一个具体场景 / 具体数字 / 具体人物 / 具体对话切入，3-5 行抓住注意力。
禁止"随着 XX 的飞速发展"这类宏观铺垫。)

![开篇配图描述](placeholder)

## 小节一: xxx

## 小节二: xxx

## 小节三: xxx

(可选更多)

## 写在最后
```

#### 文章规模 (柔性指南，不要机械)

- **小节数量: 3-6 个**，按话题决定，**不要强行凑对称**。有的小节 1000 字，有的 200 字都可以 —— 真人写作就是这样不均匀。
- **配图数量: 6-10 张**，每个小节至少 1 张。
- **总字数目标: 2500-5000 字**，有话则长无话则短。
- **⛔ 参考文章长度约束**: 如果有参考文章，改写后的文章总字数必须在参考文章的 **±10%** 以内。参考文章 3000 字 → 改写 2700-3300 字。超出即为"扩写"或"缩写"，不合格。**这是用户反复纠正过的重点。**
- **外链规范**: 每 1000 字最多 1-2 个外链，优先权威来源（官方文档、白皮书、GitHub），避免堆砌。微信公众号外链需放在"阅读原文"或原文链接中，正文内不能直接点击跳转。

#### 写作风格 (按账号 voice 区分)

**main (老孙 / 豌豆四喜)**: 实践导向，先结论后展开，像聊天不像答辩，允许不确定但不硬凹，没有独家判断时不硬写全景综述。

> **辅助 (用户偏好补充)**: 反感套话/过度分点、实践导向有案例步骤可执行、数据必须真实不编造、允许不确定但不硬凹。

无论哪个号，都要遵守 **阶段 3.5 的反 AI 检测清单** (下一节)。

#### 排版增强标记 (行内标色)

骨架稿阶段就要**主动混用**多种行内标记，让段内文字有丰富的颜色变化。整篇只用一种 `**加粗**` 是最典型的 AI 公众号指纹。

| 标记 | 效果 | 什么时候用 |
|---|---|---|
| `**文本**` | 主加粗 (深色 + 黄下划线) | 最重要的一句结论，一段最多 1 次 |
| `==文本==` | 黄色背景高亮 | 关键数据 / 核心论点 / 名言 |
| `++文本++` | 蓝色背景高亮 | 概念定义 / 工具名 / 平台名 |
| `%%文本%%` | 粉色背景高亮 | 警示 / 陷阱 / 反面案例 |
| `&&文本&&` | 绿色背景高亮 | 正面结果 / 推荐做法 |
| `!!文本!!` | 红色强调 (不加背景) | 警告 / 反对 / 关键负面数字 |
| `@@文本@@` | 蓝色强调 (不加背景) | 术语 / 专有名词 / 产品名 |
| `^^文本^^` | 橙色强调 | 温暖点缀 / 小惊喜 |
| `> ...` | 引用块 | 金句、关键数据、一段独立有力的话 |
| `===` 或 `[SEC]` 单独一行 | 分节符 | 大段之间的呼吸符 |

**密度建议**: 每 500 字出现 **3-5 处** 行内标记，分散在不同段落，**至少混用 4 种不同的标记类型**。禁止整篇只有 `**加粗**` 一种。

#### 要避免的"AI 味"写法

- 不用"首先...其次...再次...最后..."这种教科书枚举
- 不用"值得一提的是"、"不可否认"、"毋庸置疑"、"综上所述"、"总而言之"、"由此可见"、"众所周知"
- 不用"一方面...另一方面..."、"不仅...而且..."
- 不用"在...的背景下"、"随着...的发展"、"站在...的角度"
- 不用过于工整的排比句
- 文末不做全面的"总结回顾"

产出 `article.md`

> **⛔ 阶段三完成后必须暂停，把文章全文发给用户审阅，等用户确认后再进入阶段四（配图）和阶段 4.5（封面）。用户说"可以"、"没问题"、"继续"等确认词后才往下走。不要写完就直接生图。** 用户可能需要调整内容、长度、风格，配图前确认可以避免返工。

### 阶段 3.5: 人味化改写 pass (反 AI 检测核心)

这是整个流程最关键的一步，必须作为独立 pass 执行，不能和阶段三混在一起。

> **快捷路径**: 如果在阶段三撰写时已主动应用了反 AI 检测清单的全部 9 条规则（特别是 burstiness、禁用词、人称立场、事实密度），且 ai_score 检测结果 <35，可视为已通过人味化，跳过独立改写 pass。判断标准：ai_score 分数，不是主观感觉。

Claude 自己扮演"反 AI 检测审校"的角色，对骨架稿做 **9 条强制清单** 检查，逐项改写。

#### 反 AI 检测强制清单 (写完后逐条过)

**① Burstiness (句长抖动)**
- 相邻三句的字数差必须出现至少一次 **>15 字**。
- 每写 3-4 个长句，强制插入一个 **5-12 字的短句**。例如: "对。" "我当时愣住了。" "这事挺离谱。" "先别急。"
- 禁止连续 4 句都是 25-40 字的"标准长句"。

**② 句式多样性 —— 禁用词清单**
在最终稿中全文搜索以下词，**命中 >1 次必须替换或删除**:
```
首先/其次/最后   不仅...而且   一方面...另一方面
值得一提的是     不可否认       毋庸置疑
综上所述         总而言之       由此可见
众所周知         不难发现       显而易见
在...的背景下    随着...的发展  站在...的角度
让我们一起来     归根结底       无论如何
```

**③ AI 高频词黑名单**
全文搜索以下词，**命中 >2 次必须替换**:
```
赋能 / 打造 / 聚焦 / 深度融合 / 生态 / 闭环 / 链路 / 抓手 /
价值链 / 护城河 / 方法论 / 底层逻辑 / 生态位 / 结构化思维 /
提升效率 / 助力 / 全链路 / 一站式 / 端到端 / 量变到质变 /
引领 / 颠覆 / 革命性 / 前所未有 / 核心竞争力 / 范式 /
降本增效 / 数字化转型 / 产业升级 / 破局 / 出圈 / 沉淀 /
深耕 / 蓝图 / 新篇章
```

**④ 开头破冰规则**
第一段**禁止**从宏观背景切入 ("近年来..."、"随着...的发展...")。改为:
- 一个具体场景 ("最近剪视频的时候，我正在...")
- 一个具体数字 ("我给一篇 5000 字的稿子配图花了 2 小时 47 分...")
- 一句具体的话 ("同事昨天跟我说:'你这个工具能开源吗?'")
- 一个具体的人物 ("OpenAI 的 Greg Brockman 在周六凌晨发了一条 tweet...")

**⑤ 人称和立场**
- 全文**必须**出现 ≥3 次第一人称 ("我") 的主观表达，包含: 个人经历 / 判断 / 失败 / 困惑。
- 允许不确定表达: "我可能说错了"、"我还没完全想明白"、"这只是我的感觉"、"存疑"。
- 禁止全程"全知冷静陈述"。

**⑥ 事实密度**
每 500 字内必须有 **≥1 个具体数字或专有名词** (时间 / 金额 / 版本号 / 人名 / 产品名 / 地名)。禁止"很多"、"大量"、"据说"、"相关研究表明"。

**⑦ 标点多样性**
全文必须出现:
- 破折号 `——` ≥1 次 (用于插入语或强调)
- 问号 ≥2 次 (包括设问句)
- 括号插入 `(...)` ≥1 次
- 省略号 `...` ≤3 次 (多了也是 AI 味)
禁止整篇只有句号和逗号。

**⑧ 结构的"不完美"**
允许并鼓励:
- 在某一小节末尾补"扯远了，回到主题"
- 反悔句: "上面这点我收回，想了一下其实..."
- 自嘲: "写到这里我自己都怀疑我在扯淡"
- 小节长度明显不对称
这些是真人写作的天然痕迹，AI 默认不会产生。

**⑨ 按账号 voice 做语气再一次过滤**
按当前账号的 voice 字段，把句子整体语气再过一遍。

#### 执行方式

Claude 明确说: "现在进入人味化改写 pass"。对骨架稿**逐段**过一遍，每段输出"原文 → 改写"对照，确保覆盖了上面 9 条。可以直接在 `article.md` 文件中原地改。

### 阶段四: 生成配图 (baoyu-article-illustrator)

使用 `baoyu-article-illustrator` skill 生成正文配图，替代原有的简单模板生图。

**为什么替换**: baoyu-article-illustrator 会分析文章结构、识别最佳插图位置、生成结构化 prompt（含文章实际数据），配图质量远高于简单模板。

**风格**: `hand-drawn`（暖色手绘笔记风），与 warm-editorial 排版和文艺手绘封面统一。

**流程:**

**⚠️ 前置步骤（必须先执行）: 检测已有原图**

```bash
# 扫描 article.md 中已有的图片引用
grep -oP '!\[.*?\]\((.*?)\)' ~/.hermes/skills/wechat-publisher/sunwork/<date-slug>/article.md
```

1. 扫描 `article.md`，提取所有已存在的 `![...](...)` 图片引用
2. 将已有图片分类：
   - `images/original-*` 或 `images/screenshot-*` → **原图**（来自阶段2.5下载）
   - `images/01-*.png`、`images/02-*.png` 等 → **AI生成图**（来自之前流程）
3. 标记已有原图的段落为「**跳过**」，不需要再生成配图
4. **只为没有原图的纯文字段落**生成AI配图

> **⛔ 铁律**: 如果一个段落已经有了 `images/original-*.png` 或 `images/screenshot-*.png` 等原图，**绝对不能再用 baoyu-article-illustrator 生成替代图**。原图承载的是具体信息（UI截图、数据对比、操作步骤），AI 抽象图无法替代。

**生成步骤（对需要配图的段落）:**

1. 加载 `baoyu-article-illustrator` skill
2. 传入 `article.md`，skill 自动分析文章结构和内容
3. 生成 `outline.md`（插图位置、目的、视觉内容）—— **已标记跳过的段落不生成**
4. 为每张图创建 prompt 文件（`prompts/NN-type-slug.md`）
5. 调用 `image_generate` 逐张生成（可并行：多个 `image_generate` 调用互不依赖时，放在同一个 function_calls 块中并发执行，6 张图约 7 分钟完成）
6. 下载到本地 `images/` 目录
7. 在 `article.md` 中插入图片引用（只插入到没有原图的段落）

**配置** (EXTEND.md):
- style: hand-drawn（暖色纸+手绘线条+柔和色块）
- palette: warm（暖色调，与 earth 封面色系协调）
- language: zh（中文文字标注）
- output: imgs-subdir（图片放在文章同级 imgs/ 目录）

**⚠️ 所有图片中的文字、标注、标题必须是中文。**

**Provider**: `openai-codex` (GPT Image 2)，通过 Codex OAuth 认证，不需要 API Key。

**简化调用** (在 wechat-publisher 流程中):

```
加载 baoyu-article-illustrator skill，传入 article.md 路径，使用 --quick 模式自动分析并生成配图。
```

> 图片保存到 `sunwork/<date-slug>/imgs/` 目录后，publish.py 会自动处理：下载→上传微信 CDN→替换 URL。不需要手动上传。

### 阶段 4.5: 生成封面图 (baoyu-cover-image)

**每次发文必须单独生成封面图**，不要用文章配图代替。

使用 `baoyu-cover-image` skill，参数: `--quick --aspect 2.35:1 --lang zh --text title-only`

封面图尺寸: 微信公众号推荐 **900×383** (2.35:1 电影画幅)

**流程:**

1. 加载 `baoyu-cover-image` skill
2. 传入文章标题和主题，自动生成封面 prompt
3. **⛔ 必须在 prompt 中加入安全区要求**（见下方）
4. 调用 `image_generate` 生成封面图
5. **裁切到2.35:1**: `sips --cropToHeightWidth 653 1536 cover_raw.png --out cover.png`（GPT Image 2 只支持16:9，必须裁切）
6. **验证裁切结果**: 检查封面图，确保标题和主要元素完整可见，没有被裁切掉
7. 传给 `publish.py --cover`

**⛔ 封面图安全区规则（必须遵守）**

GPT Image 2 只支持 16:9 (1536×1024)，微信封面需要 2.35:1 (900×383)。裁切时会切掉上下边缘约 30% 的内容。

**在 prompt 中必须加入以下要求**：
```
【安全区要求】
- 核心内容（标题文字、主要视觉元素）必须集中在画面中央 60% 的区域
- 上下各留 20% 的空白/背景区域（会被裁切掉）
- 标题文字必须居中放置，不要靠近上下边缘
- 主要图形元素不要超出中央区域
```

**示例 prompt 结构**：
```
封面图：[描述画面内容]
标题文字："[文章标题]"（居中放置）
【安全区要求】核心内容集中在画面中央60%区域，上下各留20%空白背景。
风格：文艺手绘，暖色调，奶油色纸张背景。
```

```bash
# 示例: 基于文章标题生成封面
# baoyu-cover-image 会自动:
# 1. 分析文章内容，提取主题和关键词
# 2. 生成封面 prompt (含标题文字)
# 3. 调用 image_generate 生成 2.35:1 封面
# 4. 保存到 cover.jpg
```

**封面风格默认值** (在 EXTEND.md 中配置):
- type: scene (场景感，有叙事性)
- palette: earth (自然有机色调)
- rendering: hand-drawn (手绘笔触)
- text: title-only (只显示标题)
- mood: subtle (低对比度，柔和文艺)
- language: zh (中文)
- quick_mode: true (全自动)

### 阶段五: AI 味自检 gate + 格式转换与发布

**publish.py 内置强制 gate**: 在调用草稿接口之前会自动调用 `ai_score.check_ai_score()`，分数 ≥ 阈值 (默认 45) 直接拦住，不会发草稿。

#### 手动预检 (推荐)

```bash
cd ~/.hermes/skills/wechat-publisher/scripts
python3 ai_score.py /path/to/article.md --threshold 45
```

阈值约定:
- **< 35**: 🟢 PASS，可以发
- **35-45**: 🟡 WARN，能发但建议再改一轮
- **≥ 45**: 🔴 FAIL，publish.py 会拒绝发送，**必须回到阶段 3.5 重写命中的段落**

脚本命中时: 读取命中列表 → 在文章里定位句子 → 重写整个句式 (不只是替换词) → 重跑直到通过。

#### 一键发布

```bash
cd ~/.hermes/skills/wechat-publisher/scripts
python3 publish.py \
  --account main \
  --input /path/to/article.md \
  --cover /path/to/cover.jpg \
  --title "文章标题" \
  --digest "120字以内摘要"
```

publish.py 会自动:
1. 从 `wechat-publisher.yaml` 读取对应账号的 `author` 和 `theme`
2. 按 theme 加载对应主题排版
3. 跑 AI 味 gate，不过就停
4. 处理图片 → HTML 转换 → 封面上传 → 创建草稿
5. 返回 `media_id`

**不需要手动传 `--theme` 或 `--author`** —— 账号配置会自动带入。

> 极少数情况下需强制绕过 AI 味检测 (人工已审校确认): `--skip-ai-score`

### 阶段六: 告知用户

发布成功后:
- 告知草稿已保存
- 提醒用户登录 mp.weixin.qq.com 查看草稿箱并手动确认发布
- 文章不会自动群发

## 贴图模式 (newspic)

适合: 观点串、技巧卡、金句，文字少靠图主导。

```bash
cd ~/.hermes/skills/wechat-publisher/scripts
python3 publish.py --account main --type newspic --brief /path/to/brief.md
```

## 常用命令

```bash
SCRIPTS=~/.hermes/skills/wechat-publisher/scripts

# 列出已配置账号
python3 $SCRIPTS/wechat_api.py list-accounts

# 列出排版主题
python3 $SCRIPTS/html_converter.py --help

# 只做格式转换
python3 $SCRIPTS/html_converter.py article.md --theme warm-editorial -o article.html

# 上传图片到微信 CDN
python3 $SCRIPTS/image_handler.py upload photo.jpg

# 批量处理图片链接
python3 $SCRIPTS/image_handler.py process article.md -o article_processed.md

# AI 味检测
python3 $SCRIPTS/ai_score.py article.md --threshold 45
```

## 路径约定

所有文件放在 `~/.hermes/skills/wechat-publisher/sunwork/<date-slug>/`:
```
sunwork/<date-slug>/
├── brief.md
├── research.md
├── article.md
├── article.html     (临时)
├── images/
│   ├── 01.png
│   └── ...
└── cover.jpg
```

`<date-slug>` 格式: `20260504-topic-slug` (日期+短横线+语义化)

## 错误处理

| 错误 | 原因 | 解决 |
|---|---|---|
| `40164` IP 不在白名单 | 机器 IP 未加白名单 | 当前 IP: `64.118.158.198`，去公众平台加白名单 |
| `40001` token 无效 | 凭证错 | 检查 wechat-publisher.yaml |
| `48001` 接口未授权 | 公众号类型不支持 | 需已认证的服务号/订阅号 |

## 参考文件

- `references/setup-notes.md` — 安装踩坑、API 验证流程、生图适配方案
- `references/codex-oauth-image-gen.md` — Codex OAuth token 管理（GPT Image 2 认证）
- `references/baoyu-skills-integration.md` — baoyu-cover-image 和 baoyu-article-illustrator 集成详情
- `references/image-prompts.md` — 生图 prompt 模板和最佳实践
- `references/manual-publish-workflow.md` — publish.py 超时时的手动分步发布流程
- `references/reference-article-writing.md` — 参考文章写作规范：原料vs模板、案例/时间/术语替换、用户反馈常见问题
- `references/wechat-cdn-anti-hotlinking.md` — 微信CDN图片防盗链完整方案（Referer + magic bytes + curl备用）
- `references/first-article-workflow.md` — 首篇完整文章的执行日志、pitfalls、AI味检测结果
- `templates/wechat-publisher.yaml.template` — 配置模板

## 视觉风格体系

公众号视觉语言统一为"暖色文艺杂志"调性：

| 组件 | 工具 | 风格配置 |
|---|---|---|
| **封面图** | baoyu-cover-image | scene + earth + hand-drawn + subtle |
| **正文配图** | baoyu-article-illustrator | hand-drawn + warm |
| **排版主题** | warm-editorial | 栗色暖调 + 米白纸 + 宋体 |
| **生图后端** | GPT Image 2 | openai-codex (Codex OAuth) |

三者协调：暖色 + 手感 + 文艺杂志感，视觉语言完全统一。

### 外部 skill 依赖

- `baoyu-cover-image` — 安装在 `~/.hermes/skills/baoyu-cover-image/`
  - 配置: `~/.baoyu-skills/baoyu-cover-image/EXTEND.md`
  - 微信封面尺寸 2.35:1，language=zh，quick_mode=true
- `baoyu-article-illustrator` — 安装在 `~/.hermes/skills/baoyu-article-illustrator/`
  - 配置: `~/.baoyu-skills/baoyu-article-illustrator/EXTEND.md`
  - style=hand-drawn，palette=warm，language=zh，output=imgs-subdir

## 常见坑

- `wechat-publisher.yaml` 必须在仓库根目录，不在 scripts/ 下
- macOS 系统 Python 装依赖: `python3 -m pip install requests pyyaml` (不要 `--break-system-packages`)
- 生图脚本 `generate_image.py` 需要 `bun`，Hermes 环境下跳过它，直接用 `image_generate` 工具
- 新闻图片模式 (newspic) 每张图都占永久素材名额，5-10 张/次
- 正文图和封面图的上传接口不同，名额计算也不同
- **Codex OAuth token 有两套存储**: `providers.openai-codex` 和 `credential_pool.openai-codex`。插件优先读 pool，refresh 时两处都要更新
- **Codex OAuth client_id**: `app_EMoamEEZ73f0CkXaXp7hrann`（注意大小写），token endpoint: `https://auth.openai.com/oauth/token`
- **封面图不要用文章配图代替**: 必须用 baoyu-cover-image 单独生成 2.35:1 封面
- **排版主题在 wechat-publisher.yaml 中配置**: `theme: "warm-editorial"`，不要在 publish.py 命令行覆盖
- `publish.py` 会自动重新处理文章中的所有图片 (下载→上传微信 CDN)，不需要在阶段四手动上传 CDN
- **图片相对路径陷阱**: publish.py 从 `scripts/` 目录运行，但文章中图片引用如 `![desc](images/01-xxx.png)` 是相对路径，会被解析为 `scripts/images/01-xxx.png` 导致全部跳过（"跳过无效路径"）。**解决方案**: 在 article.md 中使用**绝对路径**引用图片，如 `![desc](/Users/sun/.hermes/skills/wechat-publisher/sunwork/<date-slug>/images/01-xxx.png)`。或者在阶段四插入图片引用时，直接写绝对路径而非相对路径。
- `image_handler.py upload` 输出有中文前缀 `正文图片上传成功: `，解析 JSON 会失败，需正则提取 URL
- urllib3 在 macOS LibreSSL 下会报警告，可忽略
- **微信草稿 API 标题长度限制**: 实测约 36 字节 UTF-8（约12个中文字符），比官方文档说的 64 字节短很多。标题超长会报 45003。摘要(digest)限制约 41 字节，超长报 45004
- **publish.py 大文件超时**: 当文章含多张大图（3MB+）时容易超时。解决方案：分步执行——先手动调 upload_thumb_image() 上传封面，再逐张调 upload_content_image() 上传正文图，然后用 html_converter.py 转 HTML，最后调 api.add_draft() 创建草稿。注意：必须用 api.add_draft()，不能用 requests.post(json=data)
- **封面图比例裁切**: GPT Image 2 只支持 16:9/9:16/1:1，无法直接生成2.35:1。生成后必须用 `sips --cropToHeightWidth 653 1536 input.png --out cover.png` 裁切到2.35:1（以1536宽度为基准，高度653）
- **⛔ 图片路径必须用绝对路径**: article.md 中的图片引用必须使用绝对路径（如 `/Users/sun/.hermes/skills/wechat-publisher/sunwork/xxx/images/01.png`），不能用相对路径（如 `images/01.png`）。publish.py 在 scripts/ 目录下运行时，相对路径会解析失败导致图片全部跳过。写完 article.md 后，必须用 `patch` 工具将所有 `images/` 替换为绝对路径前缀
- **⛔ 微信公众号图片防盗链（已修复）**: `download_image` 函数已增强，自动处理微信 CDN 防盗链：① 自动添加 `Referer: https://mp.weixin.qq.com/` 头；② 下载后用 magic bytes 验证是否为真图片（防止 HTML 错误页被当图片上传）；③ 如果 requests 下载失败，自动用 curl 带完整浏览器 headers 作为备用方案。理论上不再需要手动下载图片
- **ai_score.py 会检测"在...的背景下"为 AI 套话**: 即使语境具体也会命中。改用口语化表达
- **新闻/评论类文章（无参考截图）可跳过阶段2.5和阶段四**，直接从骨架稿到人味化改写再到发布。配图按需生成，不必强制6-10张
- **⛔ 改写文章长度超标**: 用户多次纠正——改写后的文章不能比参考文章长太多。参考文章 3000 字，改写 3800 字就是失败。必须控制在 ±10% 以内。写完后用 `wc -m` 或手动估算字数，超了就删减
- **⛔ 写完文章直接生图**: 用户明确要求先审阅文章再配图。阶段三完成后必须暂停等用户确认

## ⛔ 严禁事项 (发布相关)

### 1. 中文编码：必须用 api.add_draft()，严禁直接 requests.post(json=data)

原因: requests.post(json=data) 默认 ensure_ascii=True，把中文编码成 \uXXXX 转义序列，微信解析后中文全部乱码。

正确方式:
```python
from api import set_account, add_draft
set_account('main')
media_id = add_draft({
    'title': '...', 'author': '...', 'digest': '...',
    'content': html,
    'thumb_media_id': '...',
    'need_open_comment': 1,
})
```
api.add_draft() 内部用 json.dumps(ensure_ascii=False).encode('utf-8')，中文不会被转义。

如果必须直接调 requests:
```python
resp = requests.post(url,
    data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
    headers={"Content-Type": "application/json; charset=utf-8"})
```
绝对不能用 requests.post(url, json=data)。

### 2. 防止重复草稿：发布前检查，清理用精确 media_id

发布前检查:
- 创建草稿前，先用 draft/batchget 检查是否已有同标题草稿
- 如果已存在，询问用户是覆盖（删除旧的再创建）还是跳过

清理草稿时:
- 严禁用关键词模糊匹配删除（如标题含某词就删）
- 必须用精确的 media_id 删除
- 删除前打印确认列表，逐条核对

调试期间:
- 测试 API 时用 content: '<p>test</p>' + 标题含 'test'，测试完立即删除
- 不要用正式标题和正式内容做测试
- 每次发布前在草稿箱确认没有同名草稿再创建
