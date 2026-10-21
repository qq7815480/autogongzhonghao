# GPT-5.6 发布/有限预览素材库（更新至 2026-07-10）

适用场景：用户要求围绕 GPT-5.6、Sol/Terra/Luna、前沿模型分层发布、安全访问控制、Codex/Agent 能力、网友热议、使用测评写公众号文章。

## 最新状态：已从有限预览进入公开发布

### OpenAI 正式发布页（2026-07-09）
- 标题：GPT-5.6: Frontier intelligence that scales with your ambition。
- GPT-5.6 已从 limited preview 进入 general availability。
- 三模型家族：Sol（旗舰）、Terra（日常平衡）、Luna（最高性价比/最低成本）。
- 重点卖点：每个 token 完成更多有用工作；更强 performance per dollar；更强 coding agent、knowledge work、cybersecurity、science、design judgment、computer use。
- Ultra：最高能力设置，默认协调 4 个 agent 并行，适合复杂任务；API 可通过 Responses API 的 multi-agent beta 做类似体验。
- Agents’ Last Exam：GPT-5.6 Sol 53.6，比 Claude Fable 5 adaptive reasoning 高 13.1 分；medium reasoning 也高 11.4 分，约四分之一估算成本。
- Artificial Analysis Coding Agent Index：Sol max reasoning 得分 80，比 Fable 5 高 2.8 分；输出 token 少一半以上，用时不到一半，成本约低三分之一。
- BrowseComp：Sol 92.2%；OSWorld 2.0：Sol 62.6%，且比 Opus 4.8 少 85% output tokens。
- 官方/伙伴引用可作素材：Cursor、Qodo、Notion、Cognition、Rogo、Ramp、Shopify、Cisco、Clio 等均强调“更能坚持长任务 / token 更省 / 工具使用更稳”。

## 已交叉验证的公开信息

### OpenAI Help Center / Preview materials
- GPT-5.6 是三模型家族：Sol、Terra、Luna。
- Sol：旗舰、最强；Terra：较低成本强模型；Luna：最快、最省成本。
- 预览期通过 OpenAI API 和 Codex 提供给少数 trusted partners / organizations。
- 预览期不在 ChatGPT 中提供；公开发布后逐步扩展到 ChatGPT、Codex 和 API。
- 没有面向个人的公开申请或 waitlist。
- 价格：
  - gpt-5.6-sol：$5 / 1M input tokens，$30 / 1M output tokens
  - gpt-5.6-terra：$2.50 / 1M input tokens，$15 / 1M output tokens
  - gpt-5.6-luna：$1 / 1M input tokens，$6 / 1M output tokens
- Prompt caching：支持显式 cache breakpoints，最低 30 分钟缓存寿命；cache write 1.25x 未缓存输入价，cache read 仍享 90% cached-input discount。

### OpenAI Deployment Safety Hub / System Card（2026-06-26）
- 官方称在发布前与美国政府预览发布计划和模型能力；按政府要求先从少数 trusted partners 做 limited preview。
- Preparedness Framework 下，Sol/Terra/Luna 在 Cybersecurity 与 Biological and Chemical risk 上均按 High capability 对待；AI Self-Improvement 未达 High。
- 官方强调部署了更强 safeguards，包括模型训练、安全评估、activation classifiers、实时监控/拦截、trusted access 等。
- GPT-5.6 Sol/Terra 可找漏洞和 exploit pieces，但系统卡称其不能自主对 hardened targets 完成端到端攻击。
- 官方称投入超过 700,000 A100e GPU hours 自动寻找 universal jailbreaks，并在部署期持续红队测试。

## 媒体层信息

### CNBC（2026-07-08 / 2026-07-09）
- OpenAI 将公开发布 GPT-5.6 Sol、Terra、Luna，结束此前因美国政府要求造成的 limited preview。
- 同期发布 GPT-Live-1 / GPT-Live-1 mini，主打同时听和说。
- Sam Altman 称新模型在 agentic coding tasks 上 token efficiency 提升 54%，并称 “as good or better” than competing models。
- 背景：Anthropic Claude Fable 5 / Mythos 5 与美国政府 export control 冲突后恢复访问。

### VentureBeat
- GPT-5.6 初期约提供给 20 个组织。
- Sol 面向复杂 coding/security research；Terra 面向高容量业务任务；Luna 面向低成本日常工作。
- 报道把分阶段发布与美国 AI 安全评估流程、Anthropic 事件放在一起解释。
- 强调所有三个模型都按 cyber 和 bio/chemical High capability 处理，企业可能面临治理义务。

### Engadget / The Information / 中文媒体转述
- GPT-5.6 limited preview 给 trusted partners。
- 访问限制与美国政府预览/协调有关。
- 转述 Altman 内部备忘录称预览期间政府会“逐个客户批准访问权限”；Altman 也称这不是 OpenAI 偏好的长期模式，会寻找更可持续方案。

## 测评层素材

### CodeRabbit（2026-07-09）
- 如果还在用 GPT-5.5 或更早 OpenAI 模型做 coding agent，可先测试 Sol。
- Sol 更能“跟到底”：处理 messy repo tasks、长 checklist、review issue 发现更多。
- Terra 适合 scoped work，但要测 cost per solved task；便宜 token 不一定等于便宜完成任务。
- Fable 5 在架构判断和规划品味上仍可并行；Sonnet 5 在部分 review comment quality 上仍有优势。
- 推荐路由：Sol 做长实现/高成本漏 bug 的 review；Terra 做 scoped repeatable work；Luna 做 first-pass lane。

### 社交/视频测评（需降级处理）
- AICodeKing/YouTube 摘要：KingBench 3 中 Sol 78.57%、Terra 62.9%、Luna 44.3%；Sol/Terra 在 hard math task 完美；三者在 long-horizon agentic fine-tuning task 完美。
- 同一测评称 GPT-5.6 在 frontend/visual tasks 上仍落后 Fable 5 和 Opus 4.8；结论是“不是 paradigm shift，但比 GPT-5.5 是强且价格漂亮的升级”。
- 这类第三方/个人 benchmark 必须标为“社区测评/个人测试”，不要写成官方事实。

## 社区与网友热议层

### Reddit / r/codex release megathread
- 用户关注点很实际：Codex coding performance、debugging quality、speed/rate limits、larger repo handling、UI/workflow changes、bugs/regressions。
- 有用户称 Sol 先在 Codex 部分可见，不在 ChatGPT 主聊天里；Pro 计划可见。
- 有用户提到 context window 353k tokens（社区体验，待官方确认，不能写死）。
- Ultra 模式被反馈为更谨慎地开 subagents；某个 hard prompt 跑 10-20 分钟后触发 bio/cyber additional safety checks，但仍继续。
- 有用户吐槽 24 小时滚动开放不是“马上可用”。

### Reddit / r/singularity、r/OpenAI
- 一派追 Sol：旗舰能力、Ultra、Codex、benchmark。
- 另一派认为 Luna 反而更关键：$1 input / $6 output，如果接近 GPT-5.4/5.5 水平，将显著改变批量任务成本。
- 有人认为 Terra 不重要，普通用户只关心“最强模型”；这可用来呈现社区分歧。

## 社区与传闻层：必须降级处理

- 早期中文/英文社区出现过 Codex 后台日志、gpt-5.6、iris-alpha、kindle、kepler、150 万 token 上下文、前端 UI 生成、coding benchmark 等说法。
- 这些传闻有些被官方发布方向部分印证：GPT-5.6 确实来了，确实与 API/Codex、软件工程、Agent、网络安全相关。
- 但不能把所有泄露细节写成事实。
- 150 万上下文：OpenAI Help Center / 发布页未明确确认，文章里不要写死。
- 353k context window：可作为社区体验提及，必须标注“有用户反馈/待官方确认”。
- GPT-5.6 91.9% Terminal-Bench 2.1：可见于社交转述/解读视频；写作时标为“社交转述/特定模式下说法”，不要写成第三方榜单已公开更新。

## 推荐文章主线

不要写成“OpenAI 又王炸/吊打/封神”。更稳、更有判断力的主线是：

> GPT-5.6 的重点不只是更强，而是前沿模型开始进入“三层定价 + 多 Agent + 安全访问 + 政府评估 + 企业路由”的新阶段。它正在从互联网产品变成受控基础设施。

可用标题方向：
- 最强模型上锁了
- GPT-5.6来了，但别只盯Sol
- GPT-5.6真正的大新闻，不是跑分
- 最强AI开始分层发布
- GPT-5.6来了，普通人该先看Luna

## 写作注意

- 把信息分为三层：官方事实、媒体转述、社区传闻。
- 跑分、泄露代号、context window、第三方个人 benchmark 要谨慎，避免“已证实”口吻。
- 重点解释 Sol/Terra/Luna 分层、价格、Codex/Agent 工作流、安全访问控制、政府评估流程。
- 对老孙/独立开发者读者，落点放在：以后不是永远用最强模型，而是做模型路由，把简单任务交给便宜模型，关键步骤才上旗舰模型。
- 推荐落点句：Luna 做粗活，Terra 做正活，Sol 做难活和把关。
- 结尾可问三个现实问题：谁能用？用哪一档？怎么把任务拆给不同模型？
