# DeepSeek 降价 / 融资 / Code Harness 素材库（2026-05）

用于写 DeepSeek V4、API 降价、AI Coding、代码智能体、Claude Code 对标、国产模型产品化等话题。注意：部分融资与团队信息来自媒体援引知情人士，未官宣，写作时必须用“据称/传闻/如果落地”。

## 核心事实

- DeepSeek API 价格页公开信息：
  - `deepseek-v4-flash`：缓存命中输入约 0.02 元 / 百万 tokens。
  - `deepseek-v4-pro`：优惠口径下缓存命中输入约 0.025 元 / 百万 tokens，缓存未命中输入约 3 元 / 百万 tokens，输出约 6 元 / 百万 tokens。
  - V4-Pro 的 2.5 折活动结束后，媒体报道称将正式调为原定价的 1/4，而不是恢复原价。
- 多家媒体报道：4 月 25 日 V4-Pro 开启限时 2.5 折；4 月 26 日全系列输入缓存命中价格降至原有价格 1/10。
- 东方财富/每日经济新闻口径：OpenRouter 数据称 4 月 25 日 V4-Pro 调用量约 136 亿 Token，较前一日增长近四倍；V4-Flash 约 502 亿 Token，增长 85.9%。
- 技术报告/媒体摘要：DeepSeek V4 引入 CSA/HCA 混合注意力架构；在 1M token 场景，V4-Pro FLOPs 约为 V3.2 的 27%，KV 缓存约 10%；V4-Flash FLOPs 约 10%，KV 缓存约 7%。

## 融资传闻

- 彭博社/新浪科技等媒体援引知情人士：DeepSeek 正推进约 700 亿元人民币融资，投前估值可能约 450 亿美元。
- 被提到的潜在投资方包括腾讯、IDG、砺思资本等；另有说法称梁文锋个人或注资约 200 亿元。
- 写作约束：这不是官宣，不能写成“已经融了 700 亿”。建议表达：“如果这轮融资最终落地”“媒体报道称”“据知情人士称”。

## Code Harness / AI Coding

- 甲子光年、IT之家、财联社等媒体称，DeepSeek 正在组建 Harness 团队，方向是代码智能体产品，内部对标 Anthropic 的 Claude Code。
- 报道称 DeepSeek 资深研究员陈德里提到“对标 Claude Code，做 DeepSeek Code Harness”。
- 招聘岗位包括 Harness 产品经理、Harness 研发工程师，工作地点北京。
- DeepSeek API Docs 已提供接入 Claude Code 的 Anthropic API 兼容配置，可将模型设为 `deepseek-v4-pro[1m]`、`deepseek-v4-flash` 等。

## 写作角度

推荐把三件事连起来写，而不是分散写新闻摘要：

1. 降价：解决 Agent 的燃料成本问题。
2. 融资：解决长期研发、基础设施、产品化弹药问题。
3. Code Harness：解决从模型能力到开发者工作流入口的问题。

核心判断句：DeepSeek 这次真正要抢的不是模型排行榜，而是 AI Coding / 开发者工作流入口。

## 风险与平衡

- 便宜不等于最后一定省钱。真实成本应按“完成一个任务的总成本”看：如果昂贵模型一轮通过，便宜模型需要五轮修复，账单未必更低。
- Code Harness 尚未正式发布，不能写成已经上线或已经打败 Claude Code。
- Claude Code 的优势在产品手感、工具链配合、真实场景积累；DeepSeek 的优势在低价、长上下文、国内可访问、开源生态、模型与 Harness 共同进化的潜力。

## 可复用标题方向

- DeepSeek 这次不是降价，是抢代码入口
- DeepSeek 真正要打的，不是价格战
- 700 亿传闻背后，DeepSeek 开始补最后一块短板
- Code Harness 才是 DeepSeek 最近最该盯的消息
