# Agent Harness × DeepSeek V4 Flash 测评素材

适用话题：Pi、Claude Code、Codex、OpenCode、Hermes 等 Agent Harness 对比；“同一模型换 Harness 为什么结果不同”；低价模型在 Agent 工作流中的真实成本。

## 原始测评口径

核心来源：Composio《Finding the Best Harness for DeepSeek V4 Flash》及其官方 X 线程。

- 共同底模：DeepSeek V4 Flash。
- 8 种 Harness：Pi Agent、Prime Agent、OMP、Claude Code、Codex、DeepAgents、Hermes Agent、OpenCode。
- 共同条件：同一批任务、同一套 hosted Composio MCP tools、相同应用数据；单任务最长 900 秒。
- 30 个高难度跨 SaaS 工作流，涉及 Airtable、Gmail、Google Calendar、Google Sheets、GitHub、Slack、PostHog。
- 典型任务不是写 Demo，而是筛选邮件、更新表格、回复正确账号、在指定 Slack 线程报告，并避开诱饵数据。

关键结果：

| Harness | 通过率 | 中位耗时 | 成功一次成本 |
|---|---:|---:|---:|
| Pi Agent | 66.7%（20/30） | 132.2s | $0.028 |
| Prime Agent | 62.5%（15/24 有效运行） | 242.1s | $0.131 |
| OMP | 56.7% | 272.4s | $0.103 |
| Claude Code | 53.3%（16/30） | 122.7s | $0.195 |
| Codex | 53.3% | 245.0s | $0.081 |
| DeepAgents | 53.3% | 187.1s | $0.045 |
| Hermes Agent | 50.0% | 175.5s | $0.056+ |
| OpenCode | 46.7% | 129.7s | $0.073 |

Pi 平均每任务约 558,885 tokens、总成本 $0.56；Claude Code 约 741,659 tokens、总成本 $3.12。Hermes 有两次超时缺少完整用量，因此成本只是下界。Prime 有 6 次无效运行被排除，不能把其百分比当成和完整 30 次运行同等精度的结果。

## 必须守住的事实边界

1. “Pi 最强”只表示这 30 个 SaaS 工具工作流里单次通过率最高，不能外推到所有代码库、终端任务和底模。
2. “Claude Code 最快”只表示该测试中位完成时间最短，比 Pi 快约 9.5 秒，不代表所有 Provider 和网络环境。
3. DeepSeek 不是这张 Harness 榜里的参赛 Harness；8 组都使用 DeepSeek。准确写法是“DeepSeek 提供低价底模，Pi 在该测试中把它用得最省”。
4. 测评没有做消融实验。提示词、工具 Schema、上下文整理、重试、编辑策略和缓存共同影响结果，不能把 Pi 的领先归因于单一设计。
5. 每个组合对每项任务只有一次有效成绩，样本仅 30 项。4 道题就让 Pi 与 Claude Code 拉开 13.4 个百分点，榜单值得参考，不足以宣布永久冠军。
6. 这是 SaaS 工具调用测试，不是完整软件开发评测。

## Harness 的解释框架

Harness 位于模型和真实环境之间，负责：

- 工具定义与参数格式
- 文件读取、编辑和终端执行策略
- 上下文保留、压缩和截断
- 错误恢复、重试和超时
- 子 Agent 与会话管理
- Provider 路由、缓存和用量统计

文章可用比喻：模型是司机，Harness 是车、导航和仪表盘。司机相同，执行系统不同，成功率、速度和油耗仍会变化。

## Pi 官方定位

来源：pi.dev；Mario Zechner《What I learned building an opinionated and minimal coding agent》。

- Pi 自称 minimal agent harness。
- 核心工具为 read/write/edit/bash，并提供会话、compaction、skills、extensions。
- 默认不把 sub-agent、plan mode、MCP 等全部固化在核心中。
- 极简可能减少固定提示开销并提高可定制性，但本测评没有证明这是 Pi 获胜的唯一原因。

## DeepSeek 官方补充

来源：DeepSeek API Change Log。

DeepSeek 自己的 V4 Flash Agent 基准也不是“裸模型”：官方注明使用 DeepSeek Harness minimal mode、max effort、top_p=0.95、temperature=1.0。写模型跑分时必须同时记录 Harness 与配置。

## 社区讨论素材

- Hacker News：缓存命中率取决于 Harness 和工作方式；子 Agent 会创建新上下文，可能降低缓存命中；长期主会话通常更省。
- Reddit 乐观派：把日常任务迁到 V4 Flash，复杂任务继续使用更强模型。
- Reddit 冷水派：OpenCode + DeepSeek 的体感可能比 Sonnet 慢。
- 基础设施派：速度还取决于 Provider；有人报告 DeepSeek 官方服务约 150–200 tok/s。
- 公开轨迹讨论显示，Pi 并非简单地“少读文件”；Claude Code 工具调用数可能更少却消耗更多 Token。可确认结果，不能编造单一因果。

## 推荐文章主线

不要照搬“Pi 最强、Claude 最快、DeepSeek 最省”的口号。更好的主线是：Agent 的选型单位已经从单一模型变成“模型 + Harness + Provider + 上下文策略”。

给独立开发者的落地方法：挑 5 个真实高频任务，每个组合跑 3 次，记录完成率、人工修正分钟数、中位耗时、总账单和缓存命中率；按任务分层路由，而不是押一个永远的冠军。

## 来源入口

- https://composio.dev/content/best-agent-harness-deepseek-v4-flash
- https://x.com/composio/status/2086814488162972027
- https://pi.dev
- https://mariozechner.at/posts/2025-11-30-pi-coding-agent
- https://api-docs.deepseek.com/updates
- https://news.ycombinator.com/item?id=49120299
- https://www.reddit.com/r/LocalLLaMA/comments/1v7d8px/harness_showdown_claude_code_vs_opencode_vs_pi
