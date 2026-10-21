# GPT-5 原始发布素材库（更新至 2026-08-13）

适用场景：用户要求围绕 GPT-5（2025-08-07 发布，非 GPT-5.6）写公众号文章，特别是"回头看"型回顾文章、博士级专家对话争议、AI 模型发布与社区反应分析。

## 官方事实（已交叉验证）

### 发布信息
- 发布日期：2025-08-07，OpenAI 官方直播 "LIVE5TREAM"
- Sam Altman 原话："like having a team of PhD-level experts in your pocket"
- 官方定位："smartest, fastest, most useful model yet"
- 内置推理（thinking），取消模型选择器，统一入口
- 免费用户首次可用推理模型，Plus 用户触顶后回落到 GPT-5 mini
- GPT-5 Pro 替代 o3-pro，使用"扩展但高效的并行测试时计算"

### 架构变化
- 统一模型：GPT-5 + GPT-5 mini + GPT-5 nano 三档
- 定价（每百万 token）：
  - GPT-5（高推理）：$2 input / $8 output
  - GPT-5 mini：$0.40 / $1.60
  - GPT-5 nano：$0.10 / $0.40
- Prompt caching 支持显式 cache breakpoints，最低 30 分钟缓存寿命
- 微软 Azure AI 超级计算机上训练

### 官方基准测试（GPT-5 high reasoning）
| 基准 | GPT-5 | GPT-5 mini | GPT-5 nano | o3 | o4-mini |
|---|---|---|---|---|---|
| AIME '25 (no tools) | 94.6% | 91.1% | 85.2% | 88.9% | 92.7% |
| SWE-bench Verified | 74.9% | — | — | — | — |
| GPQA Diamond (no tools) | 85.7% | 82.3% | 71.2% | 83.3% | 81.4% |
| GPQA (Pro) | 88.4% SOTA | — | — | — | — |
| MMMU | 84.2% | — | — | — | — |
| HealthBench Hard | 46.2% | — | — | — | — |
| HLE | 24.8% | 16.7% | 8.7% | 20.2% | 14.7% |
| Aider-Polyglot | 88% | — | — | — | — |

### 编程能力
- 官方："最强编程模型"，针对 Cursor、Windsurf、GitHub Copilot、Codex CLI 微调
- 开发者页面声称在 o3 之上全面提升
- 开放 API 后 48 小时内流量翻倍，受限于算力

### 后续迭代时间线
- 2025-09-15：GPT-5-Codex 发布
- 2025-10-03：GPT-5 更新
- 2025-10-07：DevDay 发布 GPT-5 Pro + App SDK
- 2025-11-19：GPT-5-Codex-Max 发布
- 2025-12：GPT-5.1、5.2 相继发布
- 2026-01-22：5.2 Personality System Prompt 更新
- 2026-02-05：GPT-5.3-Codex 发布
- 2026-02-13：GPT-5、GPT-4o、GPT-4.1、o4-mini 同时退役

## 社区反应（已验证来源）

### Reddit 反弹
- r/OpenAI "GPT-5 is horrible" 帖子：4600 赞、1700 评论
- 核心抱怨：回复变短变冷、丧失 GPT-4o "聊天感"、Plus 用户一小时撞上限
- 原话引用："GPT-4o had this warmth. Now? Everything's so sterile."
- r/LocalLLaMA：响应时间长、文本框不工作
- r/singularity 反驳帖："4-5x more useful than gpt-4"

### 预测市场
- Polymarket "哪个公司 8 月底前拥有最强模型"：OpenAI 从 75% 暴跌到 14%（发布会后一小时内）

### 权威评论
- Gary Marcus（认知科学家）Substack："迟到的、过度炒作的、令人失望的"
- Marcus 判断：进步明显但非巨大飞跃
- Fireship YouTube（131 万播放）：ARC-AGI 基准输给 Grok，排名第五；发布会图表有选择性展示问题
- OpenAI 发布页未提 ARC-AGI

### 编程评测分裂
- Latent Space："毫无疑问是世界上最好的编程模型"，能可靠当大型代码库协作伙伴
- 16x Engineer：默认设置下表现不稳定，部分任务不如 o3；高推理强度下成绩明显提升
- OpenAI 开发者社区：有用户称 GPT-5 对其用例"真的很好"，也有用户说"一团糟"
- Theo Browne（YouTube）：发布前测试惊艳，发布后体验"nowhere near as good"

## 后续竞争格局

### Claude Opus 4.5（2025-11-24）
- SWE-bench Verified：80.9%（超过 GPT-5 的 74.9%）
- AIME 2025 (with tools)：100%
- 定价：$5/$25 per million tokens
- Terminal-bench 2.0：59.3%

### Gemini 3 Pro（2025-11-18）
- AIME 2025 (with code)：100%
- GPQA Diamond：91.9%
- SWE-bench Verified：76.2%
- 上下文窗口：1M tokens（行业领先）
- 定价：$2/$12 per million tokens

### 三巨头对比要点
- GPT-5 发布时的领先优势在数月内被追平甚至反超
- Claude 在架构判断和 terminal 任务上领先
- Gemini 在长上下文和数学（配合代码执行）上领先
- GPT-5 在统一推理架构和生态整合上领先

## "博士级专家"说法的准确解读

- Altman 原话是"like having a team of PhD-level experts in your pocket"
- BBC、CBS、Fox Business 等均报道为"PhD-level expertise"
- 实际含义：在特定领域、特定任务上能给出专业级回答（数学、编程、科学推理）
- 不意味着每次对话都稳定输出专家水准
- 更准确的理解：用户第一次可以按需调用不同深度的推理能力
- 这个"按需调用不同智力水平"的能力才是真正的范式变化

## 推荐文章主线

适合"回头看"型回顾文章：
> GPT-5 的意义不只是某个时间点的跑分数字。它证明了把不同强度的推理能力塞进同一个模型、让用户按需调用这条路走得通。后来的所有前沿模型都在沿这个方向走。

可用标题方向：
- GPT-5 发布一年了，博士级专家对话实现了多少
- 那个被骂惨的 GPT-5，其实改变了整个行业
- 从 GPT-5 到 GPT-5.6：一年五个大版本背后的故事
- "博士级专家"这个说法，OpenAI 赌对了吗

## 写作注意

- 区分三层信息：官方事实、媒体报道、社区传闻
- 跑分数据注明日期和测试条件
- 社区反应引用原话，不概括性描述
- 对比 Claude/Gemini 时注明发布日期差异（GPT-5 是 8 月，另外两家是 11-12 月）
- "回头看"文章可以用当前日期作为时间锚点，增加视角感
- 结尾避免空洞总结，给具体判断
