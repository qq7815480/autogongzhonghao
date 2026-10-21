# Claude Opus 5 上线素材库

用于写 Claude Opus 5 / Anthropic 新模型发布类公众号文章。写作时继续按 `emerging-ai-model-articles.md` 分层：官方事实、第三方验证、社区热议、存疑点。

## 官方事实

来源：Anthropic `Introducing Claude Opus 5`，Claude Platform Docs pricing / models overview。

- 发布时间：2026-07-24。
- API ID：`claude-opus-5`。
- 定位：接近 Claude Fable 5 的 frontier intelligence，但价格约为 Fable 5 一半；不是 Anthropic 总体最强模型，Fable/Mythos 仍在更高或更受控的层级。
- 产品入口：Claude Max 默认模型；Claude Pro 上最强模型；API、Bedrock、Google Cloud 有对应 ID。
- 价格：input $5 / MTok，output $25 / MTok；5m cache write $6.25 / MTok；1h cache write $10 / MTok；cache hit $0.50 / MTok。
- 上下文：1M tokens；max output 128k tokens。
- Thinking：Adaptive thinking = Yes；manual extended thinking (`thinking.type: enabled`) = No。
- Latency：官方模型表为 Moderate。
- Reliable knowledge cutoff：May 2026；training data cutoff：May 2026。

## 官方 benchmark 口径

- Frontier-Bench v0.1：官方称 Opus 5 surpasses all other models，并以更低 cost per task 超过 Opus 4.8 两倍以上。
- CursorBench 3.2：max effort 下距离 Fable 5 peak score 0.5% 内，但约半价 cost per task。
- ARC-AGI 3：官方称分数约为 next-best model 的 3 倍。
- Zapier AutomationBench：同等 cost per task 下 pass rate 约为 next-best model 的 1.5 倍；最低 effort 下也 pass more tasks than any other model。
- OSWorld 2.0：官方称任意给定成本下超过其他模型，并以 Fable 5 最佳结果约三分之一成本超过它。
- 官方主线：同 Opus 4.8 价格，提升长任务、coding、knowledge work、professional workflows 的效率和成功率。

## 第三方评分

来源：Artificial Analysis Claude Opus 5 Adaptive Reasoning Max Effort。

- Released July 2026。
- Intelligence Index：61，#1 / 190。
- Output speed：约 54.8 output tokens/s，#108 / 190。
- Price：input $5 / 1M，output $25 / 1M，#147 / 190。
- Cache：write $6.25 / 1M，hit $0.50 / 1M。
- Verbosity：Intelligence Index 评测中输出 100M tokens；同类平均约 63M。
- 评测成本：$3835.51。
- 第三方评价可概括为：leading intelligence，但 expensive、slower than average、very verbose。

## 社区热议

来源：Hacker News Claude Opus 5 讨论帖、Reddit 搜索片段。

- HN 抓取时：约 1365 points、142 comments。
- 典型问题：既然官方说 Opus 5 不比 Fable 5 overall 更强，那意义是什么？
- 高频回答：成本、可用性、Pro/Max 覆盖、Fable 太贵且存在更强 safeguard/fallback 约束。
- 常见工作流观点：Fable 用于 planning / hard exploration；Opus 5 用于 coding delegation / daily heavy work；Sonnet/Haiku 做轻任务。
- 争议点：贵模型若更快给正确答案，可能节省人的时间；但不是所有任务都需要最强模型。
- Reddit 片段：Fable 5 $10/$50 价格和 Max 额度消耗引发吐槽；核心不是“强不强”，而是“谁付得起、什么时候该用”。

## 推荐文章主线

不要写成“最强模型震撼上线”。更适合写：

> Opus 5 不是 Anthropic 的最强炫技模型，而是把接近 Fable 的能力下放到更日常、更可预算的 Opus 档：同 Opus 4.8 价格，更强的长任务、coding agent 和专业工作流表现。真正要看的不是单点跑分，而是成功任务成本、token 消耗、effort 档位和模型分层。

可分层建议：

- 普通聊天 / 轻总结：Sonnet / Haiku。
- 复杂代码、长 Agent、财务/法律/投研类专业分析：Opus 5。
- 极复杂规划、科研探索、边界任务：Fable / Mythos（注意价格和访问限制）。

## 公众号标题方向

- `Opus5到底强在哪`
- `Claude这次不是炫技`
- `Opus5最值得看的不是跑分`
- `Claude新模型先看账单`

注意微信标题长度限制，尽量控制在约 12 个中文字符内。
