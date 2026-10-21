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

专题参考：新发布 AI 模型/团队类文章写法见 `references/emerging-ai-model-articles.md`，用于把官方口径、媒体报道、第三方验证和存疑点分层，避免把宣传跑分写成已验证事实。若参考文章是“突发发布/性能炸场”但公开交叉验证不足，先看 `references/unverified-ai-model-release.md`，把主线转为“这个叙事反映的行业趋势”，不要把未验证细节写成事实。遇到“AI 逃出沙箱 / 自主越狱 / 突破安全环境”类热点，先读 `references/ai-agent-sandbox-incident-research.md`，区分容器逃逸、授权工具调用和环境配置错误，并用官方文档、Git 仓库与原始日志反查媒体标题。

GitHub 仓库: `https://github.com/qq7815480/autogongzhonghao` (fork of jiji262/wechat-publisher)

## 前置条件

已配置: AppID/AppSecret 已写入 `wechat-publisher.yaml`，API 连通已验证。
依赖: `requests`, `pyyaml` (已安装)。
生图: 必须走本地 OpenAI-compatible 生图 API，不走外部生图服务；默认使用 Hermes `local-openai-image / gpt-image-2（image2）` 路由，生成后保存本地文件。
生图细节: 参考当前 Hermes `image_gen.local-openai-image` 配置；历史 Codex OAuth 方案仅作旧方案排障参考，不能作为默认路径。
生图凭证: 永远读取当前 Hermes 配置中的 `local-openai-image.api_key`，不要在 prompt、临时脚本、日志、Skill 或文章目录中硬编码密钥。用户明确提供替换密钥时，视为后续默认凭证，持久化到 Hermes 配置后再验证 `/v1/models` 返回 200；报告时只说“已更新并验证”，不得复述完整密钥。若运行中的 `image_generate` 仍使用旧 provider 状态，按下方 `empty_response` 排障走“新进程读取当前配置”的有界批次，不重复调用旧状态。

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
   > 4. **加入作者位置，但不强制写“我”**：优先写用户真实提供的判断、经历、踩坑和困惑；没有亲历材料时，用信息取舍、证据边界和有依据的判断体现作者位置，严禁编造经历或为了人味硬塞第一人称
   > 5. **尽量一次问清真实细节**：你对这个话题有什么亲历的细节？踩过什么坑？有什么判断是别人没说过的？如果用户要求直接写，就继续研究并缩小没有材料支撑的部分，不反复追问
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

2. **真人层** (**重要**): 专门搜"真人讨论"作为语料库，让文章自然带上真人句式。用户如果强调“热议 / 网友热议 / 特别是讨论区 / 社区怎么看”，这一层必须优先、加量，不能只写官方事实或媒体通稿：
   - Reddit / HackerNews / V2EX / 即刻 / 少数派的帖子原话
   - X (Twitter) 上当事人 / 员工 / KOL 的发言原文
   - 小红书 / 知乎 / Threads / Facebook 的一线用户吐槽
   - GitHub issue / OpenAI Community / 产品论坛里的真实抱怨和 workaround
   - 写作时把热议分成“狂喜派 / 冷水派 / 算账派 / 工作流派 / 风险派”等几组，避免堆评论摘抄

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

> **⛔ 参考文章里的原图必须优先使用**: 如果用户给了参考文章，文章里的截图、对比图、数据图、产品界面等**必须直接用原图**，不能用 baoyu-article-illustrator 生成的抽象手绘图替代。原图承载的是具体信息（错误截图、对比结果、UI细节），AI 生成图无法替代。只有当参考文章中**没有对应视觉素材**的纯文字段落，才用 baoyu-article-illustrator 生成配图。

> **📋 提取参考文章原图的具体步骤**: 见 `references/extracting-reference-images.md`（JS提取URL → curl带Referer下载 → 用`screenshot-`前缀命名 → 文章中写**绝对路径**）。

### 阶段三: 撰写骨架稿 (第一轮)

目标: 按结构写出初稿。**允许这一稿有 AI 味**，下一阶段专门负责"人味化"。

#### 文章结构模板 (Markdown)

> Markdown 中的第一个 `# 标题` 会被 html_converter 自动跳过 (微信顶部已显示标题，不重复)。
> 正文不要写 `## 开篇` 这种模板小标题，摘要后直接进入内容；第一屏要像真实文章自然开场。

```markdown
# 标题 (抓眼球，15-25 字)

> 摘要引言 (1-2 句话，会显示在分享卡片中)

(直接用一个具体场景 / 具体数字 / 具体人物 / 具体对话切入，3-5 行抓住注意力。
禁止"随着 XX 的飞速发展"这类宏观铺垫，也不要加“开篇”小标题。)

![首屏配图描述](placeholder)

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
| `===` 或 `[SEC]` 单独一行 | 分节符 | 大段之间的呼吸符。注意：warm-editorial 主题会在二级标题前自动加分节符，正文里不要再手动写 `===`，否则草稿箱里会出现两行分割图标 |

**密度建议**: 每 500 字出现 **3-5 处** 行内标记，分散在不同段落，**至少混用 4 种不同的标记类型**。禁止整篇只有 `**加粗**` 一种。

#### 要避免的"AI 味"写法

- 不用"首先...其次...再次...最后..."这种教科书枚举
- 不用"值得一提的是"、"不可否认"、"毋庸置疑"、"综上所述"、"总而言之"、"由此可见"、"众所周知"
- 不用"一方面...另一方面..."、"不仅...而且..."
- 不用"在...的背景下"、"随着...的发展"、"站在...的角度"
- 不用过于工整的排比句
- 文末不做全面的"总结回顾"

产出 `article.md`

> **⛔ 阶段三完成后必须暂停，把文章全文发给用户审阅，等用户确认后再进入阶段四（配图）和阶段 4.5（封面）。即使用户一开始说“到草稿箱 / 生成草稿箱 / 直接发草稿”，也不能跳过正文确认；先给最终正文，等用户说“可以”“没问题”“继续”等确认词后，才开始排版、生图、封面和创建草稿。不要写完就直接生图。** 用户可能需要调整内容、长度、风格，配图前确认可以避免返工。

### 阶段 3.5: 人味化改写 pass (反 AI 检测核心)

这是整个流程最关键的一步，必须作为独立 pass 执行，不能和阶段三混在一起。

本阶段必须同时读取 `references/human-writing-integration.md`。该文件补充中文非虚构长文的材料门槛、段落推进、中文词序、去除表演性人味和语义级翻案腔检查。它只增强原始阶段一至三 + 3.5，不替代原始流程，也不改变用户先审稿再配图发布的规则。

> **材料 gate（写 1200 字以上现实题材时必做）**：动笔前在内部列出至少 5 件有来源的具体材料。五个抽象观点不算；同一观点换说法不算。材料不够时先研究，仍不够再一次问用户最多 3 个问题；用户要求直接写且研究后仍不足，就缩小题目或缩短篇幅，严禁编造用户经历、人物对白、天气、心理和所谓典型案例来填字数。

#### 先改内容，再改表面形状

人味首先来自材料、信息来路、判断依据和段落推进，不来自机械添加“我”、短句、自嘲、反悔句、问号、括号或破折号。执行顺序必须是：

1. 检查现实材料是否足够、是否可核验，删除无来源的亲历、现场、对白、心理和装饰性细节。
2. 检查每个新段落是否增加新事实、新动作、新例子、新区别或新后果；同一观点换说法不算推进。
3. 检查中文主干、连词密度、名词化、同义词循环、翻案腔和营销黑话。
4. 最后才调整句长与标点节奏；不能为了提高 burstiness 或 punctuation 分数硬插短句和标点。

`ai_score.py` 只是快速 gate，不是文章已经像真人写作的证明。即使分数 <35，仍要完成一次材料、段落推进、假细节和中文句法的人工冷读。外部中文写作 Skill `human-writing` 的组合方法与规则冲突处理见 `references/human-writing-integration.md`；可吸收其材料优先和中文改稿方法，但不要照搬“冒号/破折号全文清零”等绝对禁令。

> **快捷路径**: 如果在阶段三撰写时已主动应用了反 AI 检测清单，并且完成上述人工语义冷读，且 ai_score 检测结果 <35，可视为已通过人味化，跳过独立改写 pass。不能只凭分数跳过。

Claude 自己扮演"反 AI 检测审校"的角色，对骨架稿做 **三遍扫描**:
1. **第一遍: 15 条强制清单** — 逐条过，改掉所有 AI 痕迹
2. **第二遍: 灵魂注入** — 加回"人味"，让文章有体温
3. **第三遍: 终审** — 问自己"什么让这篇文章一看就是 AI 写的？"

---

#### 第一遍: 反 AI 检测强制清单 (15 条，逐条过)

##### A. 句式层面 (原 9 条，保留并强化)

**① Burstiness (句长节奏，只做自然度检查)**
- 复读连续几句都在相近长度、相同语法模板中的段落；如果读起来像机器匀速输出，再通过拆句、合句或调整信息顺序改善。
- 短句必须承担判断、停顿、转折或强调，不能按固定间隔机械插入，也不能为了分数硬加“我当时愣住了”“这事挺离谱”等表演性句子。
- 不规定相邻句子的字数差，也不规定每 3-4 句必须插一个短句。句长变化是诊断信号，不是写作配额。

**② 句式多样性 —— 禁用词清单**
在最终稿中全文搜索以下词，**命中 >1 次必须替换或删除**:
```
首先/其次/最后   不仅...而且   一方面...另一方面
值得一提的是     不可否认       毋庸置疑
综上所述         总而言之       由此可见
众所周知         不难发现       显而易见
在...的背景下    随着...的发展  站在...的角度
让我们一起来     归根结底       无论如何
值得注意的是     与此同时       无独有偶
```

**③ AI 高频词黑名单**
全文搜索以下词，**命中 >2 次必须替换**:
```
赋能 / 打造 / 聚焦 / 深度融合 / 生态 / 闭环 / 链路 / 抓手 /
价值链 / 护城河 / 方法论 / 底层逻辑 / 生态位 / 结构化思维 /
提升效率 / 助力 / 全链路 / 一站式 / 端到端 / 量变到质变 /
引领 / 颠覆 / 革命性 / 前所未有 / 核心竞争力 / 范式 /
降本增效 / 数字化转型 / 产业升级 / 破局 / 出圈 / 沉淀 /
深耕 / 蓝图 / 新篇章 / 玩法 / 愿景 / 重新定义 / 赋能 /
开辟新赛道 / 加速器 / 原生 / 新物种 / 新范式
```

**④ 开头破冰规则**
第一段**禁止**从宏观背景切入 ("近年来..."、"随着...的发展...")，也禁止反复使用固定自我感受模板（如"今天早上我刷 XX 材料，第一反应不是……而是……"）。用户明确指出这种开篇已经形成模板，太容易被判断为 AI 文。开篇要按题材换形态，优先从真实冲突、价格账单、用户吐槽、具体问题、反常识结论、一个微型案例切入。可选方向:
- 一个具体场景 ("最近剪视频的时候，我正在...")，但不能每篇都用"今天早上/我刷材料/第一反应"模式
- 一个具体数字 ("同样 100 万 token，Sol 输出价是 Luna 的 5 倍...")
- 一句具体的话或网友吐槽 ("有人在 Reddit 上问：按钮怎么还没亮？")
- 一个具体人物/公司动作 ("OpenAI 先把 GPT-5.6 放进 Codex，而不是直接丢给所有人聊天")
- 一个反常识结论 ("这次最值得看的不是 Sol，而是 Luna 的价格")

**⑤ 人称和立场——不设次数，不伪造亲历**
- 第一人称只在有真实来源时使用：用户明确提供的经历、作者真实做过的事、可说明的信息取舍或主观判断。
- 没有用户亲历材料时，可以写“我更相信哪种解释”“哪条资料改变了我的判断”“哪一块仍然存疑”，不能把搜索和推测写成亲身经历。
- 不再要求全文必须出现若干次“我”，也不为制造人味硬加“我当时愣住了”“说实话我后背发凉”等感受。
- 允许不确定表达，但要对应真实的不确定点，不能当口头装饰。

**⑥ 事实密度**
每 500 字内必须有 **≥1 个具体数字或专有名词** (时间 / 金额 / 版本号 / 人名 / 产品名 / 地名)。禁止"很多"、"大量"、"据说"、"相关研究表明"。

**⑦ 标点多样性——只提醒，不设最低配额**
- 破折号、问号、括号、感叹号和省略号按内容自然使用，不再规定必须出现几次。
- 禁止为了降低 AI 分数硬插问句、括号、破折号或省略号。
- 连续多段只有逗号和句号时可以提醒人工复读，但标点单调本身不直接证明是 AI。
- Markdown 标题、图片说明、链接、代码和排版标记不参与正文标点判断。

**⑧ 结构允许自然不规则，但不能表演“不完美”**
- 小节和段落不必等长，复杂处多说，已经讲明白的地方尽快过去。
- 自我修正、岔话、自嘲和“扯远了”只有在确有新信息、判断变化或真实经历时才能保留。
- 禁止按固定间隔主动添加“反悔句”“自嘲句”“短句停顿”来伪装真人。
- 每段必须增加新事实、新动作、新案例、新区别或新后果；只是换说法重复上一段，就合并或删除。

**⑨ 按账号 voice 做语气再一次过滤**
按当前账号的 voice 字段，把句子整体语气再过一遍。

##### B. 语义层面 (从 humanizer-zh 合并，适配中文公众号)

**⑩ 系动词回避 (Copula Avoidance)**
AI 倾向用"充当/扮演/作为/堪称"替代简单的"是/就是"。
- "这款工具堪称效率提升的利器" → "这工具挺好用的"
- "该功能充当了连接两端的桥梁" → "这个功能把两边连起来了"
- 检查方法: 搜索"堪称/充当/扮演/作为...的证明/标志/象征"，替换成直白句式

**⑪ 同义词循环 (Elegant Variation)**
AI 为了避免重复，会把同一个东西换着说法——读者反而困惑。
- 反面: "这个产品...该工具...这款软件...这个平台...该解决方案"（其实都在说同一个东西）
- 正面: 同一段落内同一个东西就用同一个称呼，不要追求"词汇丰富"
- 检查方法: 看一个段落里是否用 3 种以上不同称呼指代同一个东西

**⑫ 营销化/夸张语气**
AI 写作特别容易滑入广告腔，以下词出现即标红:
```
震撼 / 惊艳 / 史诗级 / 王炸 / 神器 / 宝藏 / 绝绝子 /
杀疯了 / 封神 / YYDS / 碾压 / 吊打 / 血洗 / 格局打开 /
令人叹为观止 / 拥有丰富底蕴 / 坐落在 / 作为...的焦点 /
无缝衔接 / 直观且充满活力
```
- 允许口语化的夸张 ("真的猛"、"离谱")，但禁止书面化的广告词

**⑬ 虚假对比范围 (False Ranges)**
AI 喜欢用"从 A 到 B"的结构，但 A 和 B 不在同一个维度上。
- 反面: "从小白到大佬，从入门到精通，从零到一"（堆砌排比）
- 反面: "从硅谷到中关村，从车库创业到纳斯达克上市"（假史诗叙事）
- 正面: 如果要用对比，两个端点必须在同一维度且有具体意义

**⑭ 无主语片段 / 被动语态滥用**
AI 经常用无主语的"名词+动词"碎片句，或过度使用被动语态隐藏动作发出者。
- 反面: "效率提升 300%。"（谁提升的？怎么测的？）
- 反面: "该方案已被广泛采用。"（谁在用？多少人在用？）
- 正面: 加上主语——"我测试下来效率提升了 3 倍"、"目前有 5 万开发者在用"

**⑮ 预告式宣告 + 泛泛正面结论**
AI 两种典型坏习惯:
- **预告**: "接下来让我们深入探讨..."、"下面我们将详细介绍..."——不用预告，直接讲
- **空洞结尾**: "未来可期"、"让我们拭目以待"、"相信在不久的将来"——结尾要么给一个具体行动建议，要么给一个你的真实感受，要么干脆不写"写在最后"

---

#### 第二遍: 灵魂注入 (Humanizer-zh 的 PERSONALITY AND SOUL)

光去掉 AI 痕迹不够，还得加回"人味"。检查以下几项:

**有观点，但要有依据**: 不只罗列事实，要说明哪些证据更可信、哪些限制会改变结论、作者最终如何取舍。口语可以自然，但不能为了显得有性格硬塞“离谱”“后背发凉”等反应。

**有节奏**: 短句长句交替不是为了应付规则，是为了让读者跟着你的呼吸走。该快的地方快，该慢的地方慢。

**有复杂判断**: 真人可能同时看到好处和代价。把两边各自的依据讲清楚，不要套“兼具优势与不足”，也不要机械使用“一方面……另一方面……”。

**有具体感受，但必须有来源**: 用户提供了真实场景和感受，就保留它的细节；用户没提供，不得补写“半夜刷到消息后背发凉”“我当时愣住了”之类假感受。没有亲历时，用信息取舍和有边界的判断体现作者位置。

**口头禅按真实 voice 使用**: 已有账号 voice 或用户样文中确实存在的表达可以自然保留，但不规定出现频率，也不临时发明一套口头禅。连续几篇重复同一开头、同一自嘲或同一转折时必须换掉。

**允许不完美，不表演不完美**: 段落长短可以不一，岔话必须带回新证据、尺度或判断变化。多说的两句如果没有增加内容，仍然要删，不能把松散本身当成人味。

---

#### 第三遍: 终审

Claude 问自己: **"如果我是一个读者，什么让这篇文章一看就是 AI 写的？"**

列出残余的 AI 痕迹（如果有的话），然后逐个修正。常见的残余:
- 段落间的过渡太整齐（"说完 X，我们来看看 Y"）
- 每个小节的结构太对称（都是"引入→展开→总结"三段式）
- 全文语气太统一（真人写作情绪有起伏，有的段落写得带劲，有的段落就是硬凑的）
- 结尾太"正能量"（"总之，这是一个值得期待的方向"）

修正后输出最终版 `article.md`。

---

#### 执行方式

Claude 明确说: "现在进入人味化改写 pass"。三遍扫描完成后，直接在 `article.md` 文件中原地改。不需要逐段输出对照（太长），只需要在改完后列出改动摘要: 哪些条命中了、改了什么、改了几处。

### 阶段四: 生成配图 (baoyu-article-illustrator)

使用 `baoyu-article-illustrator` skill 生成正文配图。它会分析文章结构、识别最佳插图位置、生成结构化 prompt（含文章实际数据），质量高于简单模板生图。

#### 前置步骤 (必须先执行)

1. 扫描 `article.md` 中已有图片引用：

```bash
grep -n '!\[' article.md
```

2. 按文件名判断处理方式：
   - `images/original-*` 或 `images/screenshot-*` → 原图，必须保留并跳过，不生成 AI 替代图
   - `images/01-*`、`images/02-*` 等 → 旧 AI 图，按需保留或替换
   - 没有图片的纯文字段落 → 才生成 AI 配图

> **⛔ 铁律**: 已经有 `original-*` 或 `screenshot-*` 原图的段落，绝对不能再用 AI 抽象图替代。原图承载的是具体信息（UI截图、数据对比、操作步骤）。

#### 生成步骤（只针对需要配图的纯文字段落）

1. 加载 `baoyu-article-illustrator` skill
2. 传入 `article.md`，分析文章结构和内容
3. 生成 `outline.md`（插图位置、目的、视觉内容），已标记跳过的原图段落不生成
4. 为每张图创建 prompt 文件（`prompts/NN-type-slug.md`）
5. 通过 Hermes 本地生图路由逐张生成：`local-openai-image / gpt-image-2`。**不要并行批量生成**，避免本地 API / 上游限流
6. 保存到本地 `images/` 目录
7. 插入图片引用时优先直接写绝对路径；如果已有相对路径，阶段四结束后必须统一转绝对路径
8. **逐张执行生成图片质量 gate**：按 `references/generated-image-quality-gate.md` 用视觉工具逐字核对中文、箭头方向、事实边界、额外口号、裁切和手机端可读性。发现硬伤必须先改 prompt 再重生成，重做后再次检查；生图接口成功不等于图片可发布。**手机可读性优先于横版统一**：横向信息图最多使用两列；三列以上、四步以上或含多行小字的流程图，默认改为竖版单列或上下两列。不能因为“点击可看原图”而放过正文首屏不可读的小字。
9. 原始素材为 SVG 时，优先用 `sips -s format png input.svg --out output.png` 做完整格式转换；不要优先用 `qlmanage -t` 缩略图导出，后者可能产生白边或裁切

#### ⛔ 阶段四完成后必须执行：路径转绝对

图片生成完毕后，立即验证 `article.md` 中没有相对图片路径：

```bash
grep -n '!\[' article.md
grep -n '](' article.md | grep '](images/' && echo '发现相对路径，必须修复'
```

修复规则：把 `](images/xxx.png)` 改为 `](/Users/sun/.hermes/skills/wechat-publisher/sunwork/<date-slug>/images/xxx.png)`。在 Hermes 环境里优先用 `patch` 工具精确替换；shell 场景可用：

```bash
sed -i '' "s|](images/|]($(pwd)/images/|g" article.md
```

**为什么**：publish.py 在 `scripts/` 目录下运行，相对路径会解析失败，导致所有图片被跳过（"跳过无效路径"）。这是最常见的发布失败原因。

#### 配置 (EXTEND.md)
- style: hand-drawn（暖色纸+手绘线条+柔和色块）
- palette: warm（暖色调，与 earth 封面色系协调）
- language: zh（中文文字标注）
- output: imgs-subdir（图片放在文章同级 imgs/ 目录）

**⚠️ 所有图片中的文字、标注、标题必须是中文。**

> 图片保存到 `sunwork/<date-slug>/images/` 目录后，publish.py --input 会自动处理：读取本地图片→上传微信 CDN→替换 URL。不需要手动上传。

### 阶段 4.5: 生成封面图 (baoyu-cover-image)

**每次发文必须单独生成封面图**，不要用文章配图代替。

使用 `baoyu-cover-image` skill，参数: `--quick --aspect 2.35:1 --lang zh --text title-only`

封面图尺寸: 微信公众号推荐 **900×383** (2.35:1 电影画幅)

**流程:**

1. 加载 `baoyu-cover-image` skill
2. 传入文章标题和主题，自动生成封面 prompt
3. **⛔ 必须在 prompt 中加入安全区要求**（见下方）
4. 通过 Hermes 本地生图路由 `local-openai-image / gpt-image-2` 生成封面图
5. **裁切到2.35:1**: `sips --cropToHeightWidth 653 1536 cover_raw.png --out cover.png`（GPT Image 2 只支持16:9，必须裁切）
6. **验证裁切结果**: 按 `references/generated-image-quality-gate.md` 用视觉工具检查封面，确保标题逐字准确、主要元素完整可见、没有被裁切；像素尺寸正确不等于视觉通过。如果调整 crop offset 后标题与主体只能保一个，优先回到 prompt 重生成，不要无限试裁切
7. 传给 `publish.py --cover`

**⛔ 封面图安全区规则（必须遵守）**

GPT Image 2 只支持 16:9 (1536×1024)，微信封面需要 2.35:1 (900×383)。裁切时会切掉上下边缘约 30% 的内容。微信部分入口还会使用中央方形缩略图，因此封面必须同时通过“横幅裁切”和“中央方形裁切”两种检查。

**在 prompt 中必须加入以下要求**：
```
【双安全区要求】
- 核心内容（标题文字、主要视觉元素）必须集中在画面中央 60% 的区域
- 上下各留 20% 的空白/背景区域（会被横幅裁切掉）
- 标题文字必须居中放置，不要靠近上下边缘
- 主要图形元素不要超出中央区域
- 标题与主要主体必须完整落在画面中央方形区域内，避免微信方形缩略图截断
- 长标题优先拆成 2～3 行，每行都不得超出中央方形安全区；不要用过细或过小字号
```

**验收硬门槛**：先检查 16:9 原图，再检查实际 1536×653 横幅终稿；同时模拟中央方形裁切。任一版本出现标题截断、主体丢失或手机缩略图文字不可读，都必须回到 prompt 重生成，不能靠反复移动裁切框硬救。

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
# 3. 通过 local-openai-image / gpt-image-2 生成封面原图
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

发布前先做正文配图 gate（详见 `references/body-image-prepublish-check.md`）。还必须执行图片真实格式与上传完整性检查（详见 `references/image-upload-integrity-gate.md`）：文件扩展名必须与 magic bytes 一致；任意正文图上传失败都必须停止，只有日志显示 `N/N` 全部成功才能创建草稿：

```bash
# 必须有正文图，除非用户明确要求纯文字
cd /path/to/article-dir
grep -n '!\[' article.md

# 必须没有相对图片路径
grep -n '](' article.md | grep '](images/' && echo '发现相对路径，必须修复'
```

如果 `grep -n '!\\[' article.md` 没有任何结果，不要直接发布；先回到阶段四补正文配图，或明确记录这是用户要求的纯文字文章。**例外**: 如果图片 API 不可用且用户明确确认"先发再补"（如回复"继续"、"先发吧"、"图片后面补"），可以用 PIL 临时封面发布纯文字草稿，告知用户图片后续补上。

```bash
cd ~/.hermes/skills/wechat-publisher/scripts
python3 publish.py \
  --account main \
  --input /path/to/article.md \
  --cover /path/to/cover.jpg \
  --title "文章标题" \
  --digest "120字以内摘要"
```

`publish.py` 输出必须出现 `发现 N 张图片，开始处理...`，并最终显示 `N/N 张成功上传`。只出现部分 `正文图片上传成功:` 不算通过；如果任何一张返回 `40137 invalid image format` 或其他错误，必须停止草稿创建，先用 magic bytes 检查真实格式、转成标准 JPEG/PNG 并单独试传。不得因为后续显示“草稿创建成功”就把缺图草稿报告为成功。

publish.py 会自动:
1. 从 `wechat-publisher.yaml` 读取对应账号的 `author` 和 `theme`
2. 按 theme 加载对应主题排版
3. 跑 AI 味 gate，不过就停
4. 处理图片 → HTML 转换 → 封面上传 → 创建草稿
5. 返回 `media_id`

#### 创建后回读验收（必须）

拿 `publish.py` 返回的精确 `media_id` 运行通用验收脚本，不要只相信“草稿创建成功”，也不要用刚创建后的标题列表查询代替 `draft/get`：

```bash
cd ~/.hermes/skills/wechat-publisher/scripts
python3 verify_draft.py \
  --account main \
  --media-id '精确media_id' \
  --title '精确标题' \
  --author '豌豆' \
  --digest '精确摘要' \
  --image-count 5
```

脚本使用 UTF-8 安全解码，并核对标题、作者、摘要、封面、正文 `<img>` 数量、微信 CDN 图片数量，以及正文中是否残留 `/Users/` 或 `file://` 本地路径。只有输出 `status=verified` 才能向用户报告完成。正文图数量必须传本篇文章实际值，不要固定写 5。

**⛔ 必须用 `--input` (markdown 模式)，不能用 `--html`**。`--html` 模式跳过正文图片上传，只有封面图会被处理。

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

## 研究阶段降级模式

当 `web_extract`（返回 private/internal network 错误）和 `browser_navigate`（Camofox 不可用）同时失效时，仍可完成研究：

1. **`web_search` 结果摘要本身就是有效素材**：主流媒体（Wired、Engadget、TechCrunch、Bloomberg、SCMP 等）的搜索结果 `description` 字段通常包含 150-300 字的原文摘录，包含直接引语、关键数字和事实。3 轮不同角度的搜索（中文关键词、英文关键词、社区/Reddit）通常能拼出足够的事实。
2. **事实交叉验证**：搜索结果中有 ≥2 个独立来源报道同一细节（如人名引语、时间、技术细节），视为可信。
3. **社区热议可从搜索摘要中提取**：`site:reddit.com` 搜索结果自带标题和 1-2 句摘要，足够分组（兴奋派/冷水派/算账派等）。
4. **向用户透明报告降级**：告知用户哪些源无法精读、为什么、以及当前素材的置信度。不要假装完成了深度原文阅读。
5. **仍需遵守材料 gate**：降级不能降低事实密度要求；如果搜索摘要无法提供足够具体材料，缩小题目或缩短篇幅。

## 参考文件

- `references/extracting-reference-images.md` — **从参考文章提取原图的完整流程**（JS提取URL + curl下载 + 绝对路径插入）
- `WORKFLOW.md` — **完整工作流文档**（阶段一~六的详细步骤、常见坑、命令参考，适合直接发给用户或新 Agent 阅读）
- `references/setup-notes.md` — 安装踩坑、API 验证流程、生图适配方案
- `references/codex-oauth-image-gen.md` — 历史旧方案排障参考（Codex OAuth），默认流程不要使用
- `references/baoyu-skills-integration.md` — baoyu-cover-image 和 baoyu-article-illustrator 集成详情
- `references/image-prompts.md` — 生图 prompt 模板和最佳实践
- `references/local-image-generation.md` — 本地 OpenAI-compatible 生图 API 约定；默认 `local-openai-image / gpt-image-2`，不走外部生图服务
- `references/manual-publish-workflow.md` — publish.py 超时时的手动分步发布流程
- `references/manual-publish-workflow-v2.md` — **推荐**：经实战验证的可恢复分步发布流程（大图逐张上传、状态 JSON 复用、html_converter 正确用法、按 media_id UTF-8 回读验收）
- `references/draft-image-reupload-checklist.md` — **正文配图失败后的重传检查清单**：必须插入 Markdown、上传正文图到微信 CDN、断言 HTML 中含 `mmbiz.qpic.cn`
- `references/body-image-repair-workflow.md` — **正文配图失败修复流程**：补图、绝对路径插入、上传微信 CDN、HTML 前替换、本地路径校验、重新创建新草稿
- `references/draft-update-repair.md` — **缺图草稿原地修复**：已知精确 media_id 时串行补传 N/N 正文图，用 `draft/update` 覆盖并以 `draft/get` UTF-8 回读验收，避免删除重建和同标题重复草稿
- `references/deterministic-pil-assets.md` — **确定性 PIL 配图兜底方案**：生图不可用或需要精确中文信息卡时，用 Pillow 生成暖色公众号正文卡片和安全裁切封面。注意：这只能作为临时兜底或用户明确同意的确定性风格，不能替代 baoyu 默认视觉体系。
- `references/pil-body-cover-fallback.md` — **PIL 正文图+封面兜底流程**：生图超时后保留已成功图片，其余用 1536×1024 信息卡和 1536×653 安全裁切封面补齐，保证草稿发布不中断。注意：如果用户要求“之前 baoyu 的封面图和信息图风格”，必须回到 baoyu-cover-image / baoyu-article-illustrator 重做并重新发草稿。
- `references/baoyu-image-style-recovery.md` — **baoyu 正文图/封面风格恢复流程**：用户指出默认卡片风/PIL兜底不符合 baoyu 风格时，保留原图、重做 `baoyu-*` 暖色手绘正文图和封面、替换绝对路径并重新创建新版草稿；含本地 `image_generate` 502 但直连 `/images/generations` 可用时的恢复模式。
- `references/direct-local-image-api-workaround.md` — **本地生图 API 直连兜底**：当 Hermes `image_generate` 返回 502 但本地 OpenAI-compatible `/images/generations` 可用时，读取 `~/.hermes/config.yaml` 的 base_url/api_key，按已保存 prompt 文件串行直连生成；正文 PNG 可转 1280px JPG 降低 publish.py 上传超时风险。
- `references/software-tutorial-infographic-fallback.md` — **软件教程截图式信息图兜底**：当用户要求“软件截图教程类”或指出抽象图不对时，用 Pillow/HTML/SVG 确定性生成带真实界面元素的教程信息图，并按小节补齐正文图后重新发布。
- `references/body-image-prepublish-check.md` — **正文配图发布前检查**：创建草稿前确认 `article.md` 有正文图片引用、路径为绝对路径、`publish.py` 输出显示正文图上传成功，避免只发封面不发正文图
- `references/reference-article-writing.md` — 参考文章写作规范：原料vs模板、案例/时间/术语替换、用户反馈常见问题
- `references/wechat-cdn-anti-hotlinking.md` — 微信CDN图片防盗链完整方案（Referer + magic bytes + curl备用）
- `references/first-article-workflow.md` — 首篇完整文章的执行日志、pitfalls、AI味检测结果
- `references/multi-reference-articles.md` — 多篇参考文章的处理流程（提取→丢结构→融合改写），微信文章抓取技巧
- `references/anti-ai-detection-history.md` — **反 AI 检测演进记录**：humanizer-zh 合并历史、新增 6 条模式来源、ai_score.py 更新日志
- `references/human-writing-integration.md` — **中文公众号人味化增强规则**：吸收 human-writing 的材料门槛、逐段推进、中文词序、去除表演性人味和语义级翻案腔检查；只增强原始阶段一至三 + 3.5，不替代原流程
- `references/local-ai-deployment-research-checklist.md` — **本地 AI 模型部署类文章核查清单**：拆解完整产品链路，区分开放权重与完整开源，按官方/社区/极限三层核验硬件，检查许可证、平台适配和“能跑”与“能用”的差别；附 MiniMax H3 案例要点
- `references/image-generation-pitfalls.md` — **配图生成坑点**：并发超时（必须串行）、大文件publish.py超时、cover.jpg格式问题
- `references/generated-image-quality-gate.md` — **生成图片质量 gate**：逐字核对中文、箭头与事实边界、禁止模型擅加口号、SVG用sips完整转换、封面裁切后二次视觉验收
- `templates/wechat-publisher.yaml.template` — 配置模板

## 视觉风格体系

公众号视觉语言统一为"暖色文艺杂志"调性：

| 组件 | 工具 | 风格配置 |
|---|---|---|
| **封面图** | baoyu-cover-image | scene + earth + hand-drawn + subtle |
| **正文配图** | baoyu-article-illustrator | hand-drawn + warm |
| **排版主题** | xinjuhui | 深藏青 + 亮青 + 彩色卡片，现代科技风（芯矩慧专用） |
| **排版主题** | warm-editorial | 栗色暖调 + 米白纸 + 宋体 |
| **生图后端** | GPT Image 2 | local-openai-image（本地 OpenAI-compatible API） |

三者协调：暖色 + 手感 + 文艺杂志感，视觉语言完全统一。

### 外部 skill 依赖

- `baoyu-cover-image` — 安装在 `~/.hermes/skills/baoyu-cover-image/`
  - 配置: `~/.baoyu-skills/baoyu-cover-image/EXTEND.md`
  - 微信封面尺寸 2.35:1，language=zh，quick_mode=true
- `baoyu-article-illustrator` — 安装在 `~/.hermes/skills/baoyu-article-illustrator/`
  - 配置: `~/.baoyu-skills/baoyu-article-illustrator/EXTEND.md`
  - style=hand-drawn，palette=warm，language=zh，output=imgs-subdir

## 推送到 GitHub

仓库地址: `https://github.com/qq7815480/autogongzhonghao.git`（fork of jiji262/wechat-publisher）

推送前必须确保 GitHub 凭证已配置（token 或 SSH key）。`wechat-publisher.yaml` 已在 `.gitignore` 中，不会被提交。`sunwork/` 目录也已排除。

```bash
cd ~/.hermes/skills/wechat-publisher
git add -A
git commit -m "type: 描述"
git push origin main
```

## 话题素材库

已有素材库（写相关话题时直接加载）：
- `references/agent-model-routing-research.md` — Agent 产品从单模型走向模型路由系统的素材库：RouteLLM、OpenRouter、LiteLLM、Cloudflare/Vercel AI Gateway、缓存粘性、工具兼容、fallback、评测，以及 HN/Reddit 对路由成本与上下文漂移的争论
- `references/agent-harness-deepseek-benchmark-research.md` — Agent Harness 横评素材库：Composio 用同一 DeepSeek V4 Flash 测试 Pi、Claude Code、Codex、OpenCode、Hermes 等8种 Harness 的口径、关键数据、社区争议与事实边界；写“Pi最强/Claude最快/DeepSeek最省”前必须先读，严格区分模型、Harness、Provider 和任务集
- `references/claude-riemann-zeta-research.md` — Claude 将黎曼 ζ 函数临界线零点比例无条件下界从约 41.6% 推至 67.25% 的素材库：官方论文、Lean 形式化、3100 万 token / 60 子代理工作流、真人讨论与“并未证明黎曼猜想”的事实边界
- `references/ai-coding-limits-research.md` — AI Coding Agent 额度/限流/订阅热议素材库：Codex 5小时限制、Fable 5 延期、usage credits、Reddit/HN/X 热议分组和“默认入口争夺”文章主线
- `references/ai-relay-station-research.md` — AI中转站：数据、玩家、检测方法、管控时间线、Token出口机会
- `references/deepseek-agent-price-research.md` — DeepSeek V4 降价、700亿融资传闻、Code Harness/AI Coding 入口争夺素材库（注意未官宣信息需标注传闻）
- `references/wechat-ai-agent-research.md` — 微信 AI / 小程序 Agent 生态接入素材库：官方小程序 AI 开发模式、SKILL/MCP 接入、京东/美团/滴滴/携程等首批接入、入口重排与流量分配风险
- `references/gpt-5-6-release-research.md` — GPT-5.6 Sol/Terra/Luna 有限预览素材库：官方事实、媒体转述、社区传闻分层，以及“最强模型上锁/前沿模型受控基础设施化”文章主线
- `references/gpt-5-original-release-research.md` — GPT-5 原始发布（2025-08-07）素材库：官方基准、Reddit/PolyMarket 社区反弹、编程评测分裂、Claude/Gemini 后续追赶数据、"博士级专家"说法解读，以及"回头看"型回顾文章主线
- `references/claude-opus-5-research.md` — Claude Opus 5 上线素材库：官方发布、价格/token、Artificial Analysis 评分、HN/Reddit 热议，以及“不是最强炫技模型，而是日常重活模型”文章主线
- `references/hy3-preview-research.md` — 腾讯混元 Hy3 preview 发布与开源素材库：参数架构、产品应用、OpenRouter 热议、第三方观察、官方评测图原图链接与压缩建议

## 常见坑

- `wechat-publisher.yaml` 必须在仓库根目录，不在 scripts/ 下
- macOS 系统 Python 装依赖: `python3 -m pip install requests pyyaml` (不要 `--break-system-packages`)
- 生图脚本 `generate_image.py` 需要 `bun`，Hermes 环境下跳过它，走本地 OpenAI-compatible 生图路由 `local-openai-image / gpt-image-2`
- **⛔ 不要把 PIL 信息卡/默认卡片当 baoyu 风格**：PIL/确定性卡片只适合生图完全不可用、需要精确中文信息卡、或用户明确接受兜底时使用。默认发文视觉必须优先 baoyu-cover-image（封面）+ baoyu-article-illustrator（正文信息图）。如果用户明确要求“baoyu 那个 skill / 之前 baoyu 的风格 / 不要默认风格”，严禁用默认信息卡风格发布；如果已经发出默认卡片风草稿，立即按 `references/baoyu-image-style-recovery.md` 重做：保留 `original-*`/`screenshot-*` 原图，只替换 AI 信息图和封面为 `baoyu-*` 暖色手绘杂志风，替换 article.md 绝对路径，重新创建新版草稿，并提醒旧草稿不要用。
- **⛔ 所有公众号配图必须用 `$imagegen` / `image_generate` 工具生成，严禁用 PIL/Pillow/Python 手写脚本画图替代**：用户明确纠正过——"生成的所有图片请用 $imagegen 工具来生成"。PIL 画卡片、手绘矩形、文字渲染这些统统不算数。即使本地 API 暂时 502/限流，也要等 API 恢复或明确问用户是否接受 PIL 兜底，不能自作主张用 PIL 替代。`image_generate` 走的是本地 OpenAI-compatible API（`local-openai-image / gpt-image-2`），不是外部服务。
- 新闻图片模式 (newspic) 每张图都占永久素材名额，5-10 张/次
- 正文图和封面图的上传接口不同，名额计算也不同
- **旧方案排障**: `openai-codex` / Codex OAuth 只作为历史参考，不是默认生图路径。默认生图必须走 `local-openai-image / gpt-image-2`
- **封面图不要用文章配图代替**: 必须用 baoyu-cover-image 单独生成 2.35:1 封面
- **排版主题在 wechat-publisher.yaml 中配置**: `theme: "warm-editorial"`，不要在 publish.py 命令行覆盖
- **芯矩慧模板**: 用户说"使用芯矩慧的样式"时，用 `theme: "xinjuhui"`（深藏青+亮青+彩色卡片，科技教育风）。主题文件在 `assets/themes/xinjuhui.json`
- `publish.py` 会自动重新处理文章中的所有图片 (下载→上传微信 CDN)，不需要在阶段四手动上传 CDN
- **⛔ publish.py 的 `--html` 模式不会上传正文配图**: 如果用 `--html article.html` 传入预转换的 HTML，脚本**只上传封面图**，不会扫描和上传正文中的本地图片。正文图片会保持本地路径，在微信中显示为空白。必须使用 `--input article.md`（markdown 模式），脚本才会自动检测 `![](...)` 引用、上传到微信 CDN、替换 URL。如果已经用 `--html` 发了且正文图缺失，删掉草稿，用 `--input` 重新发布
- **图片相对路径陷阱**: publish.py 从 `scripts/` 目录运行，但文章中图片引用如 `![desc](images/01-xxx.png)` 是相对路径，会被解析为 `scripts/images/01-xxx.png` 导致全部跳过（"跳过无效路径"）。**解决方案**: 在 article.md 中使用**绝对路径**引用图片，如 `![desc](/Users/sun/.hermes/skills/wechat-publisher/sunwork/<date-slug>/images/01-xxx.png)`。或者在阶段四插入图片引用时，直接写绝对路径而非相对路径。
- `image_handler.py upload` 输出有中文前缀 `正文图片上传成功: `，解析 JSON 会失败，需正则提取 URL
- urllib3 在 macOS LibreSSL 下会报警告，可忽略
- **微信草稿 API 标题长度限制**: 实测约 36 字节 UTF-8（约12个中文字符），比官方文档说的 64 字节短很多。标题超长会报 45003。摘要(digest)限制约 41 字节，超长报 45004
- **publish.py 大文件超时**: 当文章含多张大图（3MB+）时容易超时。解决方案：分步执行——先手动调 upload_thumb_image() 上传封面，再逐张调 upload_content_image() 上传正文图，然后用 html_converter.py 转 HTML，最后调 api.add_draft() 创建草稿。注意：必须用 api.add_draft()，不能用 requests.post(json=data)
- **⛔ 分步发布时 html_converter 的正确用法**: 函数名是 `convert_markdown_to_wechat_html`（不是 `convert_markdown_to_html`）。签名：`(markdown_text, styles=None, highlights=None, divider_text=None, list_style=None)`。`load_theme('warm-editorial')` 返回的是 **4元素元组** `(styles_dict, highlights, divider_text, list_style)`，必须解包后传入：
  ```python
  from html_converter import convert_markdown_to_wechat_html, load_theme
  styles, highlights, divider, list_style = load_theme('warm-editorial')
  html = convert_markdown_to_wechat_html(md, styles=styles, highlights=highlights, divider_text=divider, list_style=list_style)
  ```
  直接 `styles=load_theme(...)` 会报 `TypeError: tuple indices must be integers`。
- **分步发布的图片路径替换**: 在调用 `convert_markdown_to_wechat_html` 之前，必须先把 article.md 中的本地绝对路径替换为微信 CDN URL（upload_content_image 返回的），否则 HTML 中的图片引用还是本地路径，publish 不会再处理。
- **正文配图失败/缺失修复**: 如果用户反馈草稿正文图失败，优先按 `references/body-image-repair-workflow.md` 操作：确认 `article.md` 是否有图片引用；补齐正文图并用绝对路径插入；逐张上传 `upload_content_image()`；HTML 转换前替换为微信 CDN；正则验证所有 `![](...)` 都是 `https://mmbiz.qpic.cn/`；重新创建新草稿并提醒用户看最新草稿、旧草稿可删。
- **正文信息图说明文字过松/多一行**: `html_converter.py` 会把 Markdown 图片 alt 文本渲染成图片下方 caption 段落。若用户觉得每张信息图下面的文字描述单独换行、不紧凑，发布前把正文图写成空 alt：`![](/abs/path.jpg)`，不要写 `![说明](/abs/path.jpg)`，这样保留图片但不生成 caption。
- **正文信息图与分割图标间距过大**: warm-editorial 主题下，图片下方紧跟自动分节符时，要控制三处间距：纯图片段落 margin、`styles.img` 的 bottom margin、`styles.section_divider` 的 top margin。当前已调为图片段落 `margin:14px 0 4px`、warm-editorial 图片 `margin:18px auto 6px`、分节符 `margin:16px 0 34px`，避免看起来多一行空白。
- **正文配图“继续完成”不是只补一两张**: 如果用户在已补过少量图后继续要求“完成配图任务”，要回到文章结构按主要小节补齐覆盖。新闻/评论长文通常至少覆盖开篇核心概念、入口变化、模式/边界、服务履约、开发者行动、流量分配等关键段落；补图后用 `grep -n '!\[' article.md` 核对插图分布，不要只确认文件存在。详见 `references/body-image-completion-checklist.md`。
- **api.py 可用函数清单**: `set_account`, `get_access_token`, `add_draft`, `add_newspic_draft`, `upload_thumb_image`, `upload_content_image`, `upload_newspic_image`, `publish_article`, `publish_newspic`。没有 `get_token`，是 `get_access_token`。
- **封面图比例裁切**: GPT Image 2 只支持 16:9/9:16/1:1，无法直接生成2.35:1。生成后必须用 `sips --cropToHeightWidth 653 1536 input.png --out cover.png` 裁切到2.35:1（以1536宽度为基准，高度653）
- **⛔ 图片路径必须用绝对路径**: article.md 中的图片引用必须使用绝对路径（如 `/Users/sun/.hermes/skills/wechat-publisher/sunwork/xxx/images/01.png`），不能用相对路径（如 `images/01.png`）。publish.py 在 scripts/ 目录下运行时，相对路径会解析失败导致图片全部跳过。写完 article.md 后，必须用 `patch` 工具将所有 `images/` 替换为绝对路径前缀
- **⛔ MEDIA标签必须转为markdown图片语法**: 如果文章中有 `MEDIA:/path/to/img.png`（Hermes飞书投递格式），publish.py 的 image_handler 识别不了这种格式，图片会被静默跳过。发布前必须转成 `![描述](/path/to/img.png)`。转换命令：`sed -i '' 's|MEDIA:\\(.*\\)|![配图](\\1)|g' article.md`。常见场景：跨上下文续写时，前一个上下文用 MEDIA 标签投递图片给用户，文章草稿中保留了该格式
- **⛔ 软件教程类文章的信息图必须包含实际软件界面**: 当文章主题是某个具体工具/软件的功能介绍时，信息图/配图必须展示该软件的真实操作界面和工作流步骤，不能用泛泛的"AI应用场景"抽象图替代。用户原话："生成的信息图不是软件截图教程类的"。正确做法：prompt 中明确指定软件名称、具体操作步骤、每个步骤对应的 UI 元素（如菜单名、按钮名、窗口标题），并要求 macOS/Windows 窗口 chrome 样式。错误做法：生成通用的"办公效率/内容创作/编程开发"场景图。若本地生图 API 持续失败，别卡在重试；改用 `references/software-tutorial-infographic-fallback.md` 的确定性 Pillow/HTML/SVG 方案，画出截图式教程界面，并按文章小节补齐多张正文图后用 `publish.py --input` 重新发新版草稿。
- **封面图生成失败的临时方案**: 当本地生图 API 限流或失败时，先等待 20-60 秒重试；仍失败时，有三个降级选项（按优先级）：① 用 PIL 生成临时纯文字封面（见 `references/deterministic-pil-assets.md`），先发草稿，等 API 恢复后重做 baoyu 风格封面替换；② 用之前文章的封面图作为 `--cover` 参数先发布；③ 后续在微信公众平台手动替换。不要切回 `openai-codex` 作为默认方案。
- **⛔ 诊断 image_generate 502：先区分 proxy-down vs upstream-down**: 当 `image_generate` 返回 502 时，用 `curl -s -o /dev/null -w "%{http_code}" http://localhost:53915/v1/models` 检查 proxy 状态。**返回 401 = proxy 活着，上游 ChatGPT API 故障**（常见：EOF、timeout），重启 Cockpit Tools.app 无用，等上游恢复或用 PIL 兜底。**返回 502 = proxy 本身挂了**，重启 Cockpit Tools.app 可修复。不要在 upstream-down 时反复重启 proxy。
- **⛔ `image_generate` 返回 `empty_response` 时不要按 502 处理**: 先用当前配置直连 `/images/generations`，只打印状态码、响应键名、`data` 长度和 item 键名。若直连 200 且有 `data[0].b64_json`，再用 Hermes venv 在新 Python 进程中加载 `plugins/image_gen/local-openai-image/__init__.py` 并调用 `LocalOpenAIImageGenProvider().generate()`。若新进程成功、当前工具仍报空结果，说明是运行中进程的 provider/module 状态未刷新，不是上游故障，也不是响应结构不匹配。当前有界批次可以继续使用同一 provider/model 的新进程生成，随后在保存任务状态后重载 Gateway；不要重复相同的 `image_generate` 调用。严禁为诊断打印完整配置或 `api_key`。详细步骤和脚本见 `apikey-image-gen/references/local-image-api-troubleshooting.md` 与 `scripts/generate-via-fresh-plugin.py`。
- **⛔ 微信公众号图片防盗链（已修复）**: `download_image` 函数已增强，自动处理微信 CDN 防盗链：① 自动添加 `Referer: https://mp.weixin.qq.com/` 头；② 下载后用 magic bytes 验证是否为真图片（防止 HTML 错误页被当图片上传）；③ 如果 requests 下载失败，自动用 curl 带完整浏览器 headers 作为备用方案。理论上不再需要手动下载图片
- **ai_score.py 会检测"在...的背景下"为 AI 套话**: 即使语境具体也会命中。改用口语化表达
- **微信公众号文章抓取**: `web_extract` 和 `jina_read`/`crawl4ai` 都会被拦截。优先用 `browser_navigate`；如果 Camofox 没运行则用 `curl -sL -A 'Chrome/126...'` + python3 正则提取 `<div id="js_content">` 内容。详见 `references/multi-reference-articles.md`
- **新闻/评论类文章（无参考截图）可跳过阶段2.5和阶段四**，直接从骨架稿到人味化改写再到发布。配图按需生成，不必强制6-10张
- **⛔ 改写文章长度超标**: 用户多次纠正——改写后的文章不能比参考文章长太多。参考文章 3000 字，改写 3800 字就是失败。必须控制在 ±10% 以内。写完后用 `wc -m` 或手动估算字数，超了就删减
- **⛔ 写完文章直接生图**: 用户明确要求先审阅文章再配图。阶段三完成后必须暂停等用户确认
- **用户确认后不要二次确认**: 用户回复“确认 / 继续 / 可以 / 没问题”后，视为已授权进入配图、封面、排版、草稿箱发布流程。除非遇到密码、支付、删除草稿等高风险动作，不要再问一遍。
- **审批敏感环境下改稿优先用 patch/write_file**: 在 Feishu/cron/需要审批的运行环境里，`execute_code` 或 `terminal` heredoc 执行本地 Python 改 `article.md` 可能被审批拦截。插入图片、替换路径、轻量文本改动时，优先用 `patch` 精确替换或 `write_file` 重写已读入的完整稿件；避免为了简单 Markdown 编辑调用可执行脚本，减少流程中断。

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
- 创建草稿前，先用 `scripts/check_draft_title.py` 调 `draft/batchget` 检查是否已有**完全同标题**草稿：
  ```bash
  cd ~/.hermes/skills/wechat-publisher/scripts
  python3 check_draft_title.py --account main --title "文章标题"
  ```
  输出 JSON 中 `count=0` 且退出码 0 才能继续；命中同标题时退出码 2，并返回精确 `media_ids`。该脚本已强制按 UTF-8 解码微信响应，不能改回 `response.json()`，否则中文标题可能乱码并造成漏检。
- `draft/batchget` 可能存在短暂列表延迟，所以“创建后立即查标题返回 0”不能证明草稿不存在。创建成功后必须拿 `add_draft()` 返回的精确 media_id 调 `draft/get` 回读，并核对标题、作者、摘要、封面与正文 `<img>` 数量；回读同样使用 `json.loads(resp.content.decode('utf-8'))`。
- 如果已存在，询问用户是覆盖（删除旧的再创建）还是跳过；不要自动删除或创建重复草稿。

清理草稿时:
- 严禁用关键词模糊匹配删除（如标题含某词就删）
- 必须用精确的 media_id 删除
- 删除前打印确认列表，逐条核对

调试期间:
- 测试 API 时用 content: '<p>test</p>' + 标题含 'test'，测试完立即删除
- 不要用正式标题和正式内容做测试
- 每次发布前在草稿箱确认没有同名草稿再创建
