# Agent 模型路由技术趋势素材库

适用：撰写 Agent 产品、多模型架构、AI Gateway、模型路由、成本与可靠性主题文章。

## 核心判断

Agent 的一次用户任务通常会展开为规划、工具选择、执行、结果消化、修正与验证等多次模型调用。模型的成本、延迟、限流和能力缺口会在多步流程里累积。因此，产品问题正从“固定选哪一个模型”转为“每一步该由哪个模型执行，失败后如何接管”。

模型路由不等于轮询多个模型。生产路由至少应处理：

1. 硬能力过滤：视觉、上下文长度、工具调用、严格结构化输出、地域与数据政策。
2. 任务分层：抽取、普通执行、复杂规划、错误恢复、高风险验证。
3. 经济约束：单次成本、会话预算、团队预算、缓存价格。
4. 性能约束：首 token 延迟、总延迟、吞吐与排队。
5. 可靠性：限流、超时、上下文超限、供应商故障、能力不匹配。
6. 状态连续性：长会话和工具循环尽量保持模型/供应商粘性，避免上下文漂移与 prompt cache 失效。
7. 可观测与评测：记录实际模型、选择原因、费用、延迟、缓存、工具结果和最终任务成功率。

## 一手资料卡

### RouteLLM（ICLR 2025）

- 论文：RouteLLM: Learning to Route LLMs with Preference Data，arXiv:2406.18665，发表于 ICLR 2025。
- LMSYS 官方博客报告：矩阵分解路由器在 MT-Bench 上以约 26% 的 GPT-4 调用达到约 95% 的 GPT-4 表现；按论文当时价格假设，相比随机路由基线约省 48%。
- 关键边界：同一路由器在分布外的 MMLU 上一度接近随机；补充该领域验证数据后才改善。
- 写作要求：这些数字只适用于特定模型、价格、数据集和质量阈值，不能写成所有 Agent 都能固定节省 48% 或 85%。
- 来源：
  - https://proceedings.iclr.cc/paper_files/paper/2025/hash/5503a7c69d48a2f86fc00b3dc09de686-Abstract-Conference.html
  - https://arxiv.org/abs/2406.18665
  - https://www.lmsys.org/blog/2024-07-01-routellm

### OpenRouter Auto Router

- 支持模型与 provider endpoint 选择、价格上限和 session stickiness。
- 会话粘性用于保持行为一致并提高 prompt cache 命中。
- 没有端点满足价格上限时应失败，而不是突破预算。
- 来源：https://openrouter.ai/docs/model-routing

### LiteLLM

- Router 支持负载均衡、重试、cooldown、跨 provider fallback、预算和 tag 路由。
- Auto Routing 可由小模型做结构化分类；分类超时、空响应或 schema 不合格时，可退回启发式规则或默认模型。
- 来源：
  - https://docs.litellm.ai/docs/routing-load-balancing
  - https://docs.litellm.ai/docs/proxy/auto_routing

### Cloudflare AI Gateway

- Dynamic Routing 可用可视化或 JSON 配置条件、配额、模型、fallback、A/B 分流和路由版本。
- Spend Limits 可在主模型预算耗尽后转向便宜模型。
- 响应元数据可暴露实际 model 与 provider，方便追踪决策。
- 来源：https://developers.cloudflare.com/ai-gateway/features/dynamic-routing

### Vercel AI Gateway

- Model fallbacks 按顺序尝试后备模型。
- 触发原因不只包括 provider 故障，也包括上下文超限、输入类型不支持和能力不匹配。
- 来源：https://vercel.com/changelog/model-fallbacks-now-available-in-vercel-ai-gateway

### LangChain

- 官方将 Agent 概括为 Model + Harness；prompt、tools、middleware 都属于模型外的 harness。
- 预置 middleware 包括 model retry 和 model fallback，说明模型选择正从业务代码抽离到控制层。
- 来源：
  - https://docs.langchain.com/oss/python/langchain/overview
  - https://docs.langchain.com/oss/python/langchain/middleware/built-in

## 社区争论（只能写成观点或个案）

支持者常见理由：

- 轻模型做浏览、抽取和普通执行，强模型保留给规划、恢复和验证。
- 路由策略与具体模型映射分离，新模型替换只改配置。
- 预算、限流和供应商故障可由统一控制层接管。

反对者常见理由：

- router 若要判断复杂任务，自己可能也得很强，增加首轮延迟和成本。
- 多轮交互会发生意图漂移，简单 embedding/意图分类容易误判。
- 通用 benchmark 不一定符合客服口吻、法务标准、工具成功率等业务质量定义。
- 长会话频繁切模型会损失 prompt cache，并破坏模型行为连续性。
- 模型支持聊天不代表能稳定调用同一套工具；工具 schema 和结构化输出兼容必须单独验证。

代表性争论：https://news.ycombinator.com/item?id=49126630

## 推荐文章结构

1. 用一次 Agent 任务展开成多次调用的具体冲突切入。
2. 解释单模型为何放大成本与失败，而不是泛谈“模型百花齐放”。
3. 澄清路由不是轮询：先硬过滤，再任务分层，再 fallback。
4. 用 RouteLLM 说明节省潜力，同时突出 OOD 失效边界。
5. 讲缓存粘性、工具兼容和 router 自身成本，避免营销化。
6. 给中小团队渐进路线：统一接口 → 能力清单 → 静态分层 → 失败路径 → 真实流量回放 → 有限动态路由。
7. 结论落在评测：优化目标应是整次任务成功率、总延迟和总成本，而非单次 token 单价。

## 事实边界

- 厂商自报生产数据必须注明“厂商自报”，不能当行业总体统计。
- 社区帖子中的故障案例只作为风险提示，不能写成普遍事实。
- “模型路由系统”不等于必须训练路由模型；多数团队应先做统一接口、确定性规则、fallback 和观测。
- 产品代码可用逻辑模型名解耦供应商，但不同模型的提示行为、工具协议和长上下文表现仍不完全可替换。
