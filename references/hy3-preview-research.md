# 腾讯混元 Hy3 preview 发布与开源素材库

用途：写腾讯混元 Hy3 / 国产开源大模型 / Agent 模型应用文章时，可作为素材底稿。注意：这是素材库，不是文章模板；写作时要重新组织结构，用老孙口吻讲，不要照搬官方发布稿。

## 核心事实

- 发布时间：2026-04-23 前后。
- 模型：腾讯混元 Hy3 preview，语言模型，不是混元 3D / 图像模型。
- 架构：MoE，快慢思考融合。
- 参数：总参数 295B，激活参数 21B，MTP 层参数 3.8B。
- 结构：80 层，192 个专家，top-8 激活；GQA，64 attention heads / 8 KV heads / head dim 128；隐藏层 4096；FFN 中间层 13312；词表 120832；BF16。
- 上下文：官方称最大 256K；OpenRouter 页面显示 262K。
- reasoning_effort：支持 no_think / low / high；复杂数学、代码、推理任务可用 high，日常对话默认 no_think。
- 部署：支持 vLLM、SGLang；README 建议 8 张 GPU，H20-3e 或更大显存卡型。普通开发者更现实的方式是 TokenHub / OpenRouter / 第三方平台。
- 开源平台：GitHub、Hugging Face、ModelScope、GitCode 等。
- 许可：腾讯混元社区许可协议；不要误写为 Apache 2.0。

## 腾讯官方口径

- Hy3 preview 是“混元重建后训练的第一个模型”，也是混元当时最智能的模型。
- 2026 年 2 月起，腾讯混元重建预训练与强化学习基础设施，目标转向真实场景实用性。
- 三个方向：能力体系化、真实评估、模型与推理设计协同以追求成本效率。
- 腾讯首席 AI 科学家姚顺雨表示，希望通过开源和发布获得社区反馈，帮助 Hy3 正式版提升。

## 官方披露的产品应用

- 已接入：腾讯云、元宝、ima、CodeBuddy、WorkBuddy、QQ、QQ 浏览器、腾讯文档、腾讯乐享等。
- 后续或报道中提到：微信公众号 AI 分身、AI 客服、和平精英 AI NPC、腾讯新闻、腾讯自选股、腾讯客服、微信读书、QQ 小Q 等。
- CodeBuddy / WorkBuddy：TTFT 降低 54%，端到端响应时间缩短 47%，成功率超过 99.99%。
- 真实用户环境：稳定支撑最长 495 步复杂 Agent 工作流，覆盖文档处理、数据分析、知识检索、MCP 工具链编排。
- 腾讯文档 AI PPT：相较 Hy2，生成成功率提升 20%；部分报道还提到评测得分提升 10%、生成耗时缩短 20%。

## 评测方向

官方重点不是单一榜单，而是三类能力：

1. 复杂推理：FrontierScience-Olympiad、IMOAnswerBench、清华求真书院数学博资考（26 春）、CHSBO 2025。
2. 上下文学习和指令遵循：腾讯提出 CL-bench / CL-bench-Life，强调杂乱长上下文中的规则遵循。
3. 代码与 Agent：SWE-Bench Verified、Terminal-Bench 2.0、BrowseComp、WideSearch、ClawEval、WildClawBench，以及内部 Hy-Backend、Hy-Vibe Bench、Hy-SWE Max。

写作注意：这些多为官方自述或官方图表，可引用但不要写成“全行业公认第一”。

## 价格与调用渠道

- 腾讯云 TokenHub：输入最低 1.2 元/百万 tokens；缓存输入 0.4 元/百万 tokens；输出 4 元/百万 tokens；个人版 Token 套餐最低 28 元/月。
- OpenRouter：模型 slug `tencent/hy3-preview`；页面显示 Released Apr 22, 2026；价格约 $0.063 / $0.21 per 1M tokens；支持 OpenAI-compatible API。
- Agent 场景成本重点在输入 tokens：多步工作流会不断重复塞入历史上下文、工具结果、文件片段，缓存和低输入价很关键。

## 热议与第三方观察

- Tencent Hy X 帖子摘要：发布两周后，Hy3 preview 在 OpenRouter 周榜处理 3.66T tokens，周增长 298%，总用量、工具调用、编码三个维度第一，全平台市场份额 15.4%；热门 app 包括 Hermes Agent、Claude Code、Kilo Code、OpenClaw、Cline。
- 21 财经：5 月 7 日 OpenRouter 周榜 Hy3 preview Token 调用量和市场占有率双双登顶；上线两周调用量超过 Hy2 的 10 倍；CodeBuddy / WorkBuddy 等智能体应用中 Token 调用量高涨 16.5 倍；真正考验在更大参数 Hy3 正式版。
- Max Woolf 博客观点：Hy3 在 OpenRouter 上热度高，但非科学测试看，质量更像与其他中国开源模型同档，不一定接近 Claude Opus 4.7 / GPT-5.5；受欢迎可能来自低价、免费期转化、缓存经济、某个大型应用的实际调用。
- Reddit / LocalLLaMA 讨论点：许可证偏限制；295B/299B 级别模型本地部署门槛高。

## 推荐文章角度

稳妥主线：Hy3 preview 的价值不是“腾讯一夜登顶 / 吊打全场”，而是腾讯用产品场景反哺模型的一次工程化答卷。重点讲“够用 + 便宜 + 长上下文 + Agent 工具调用 + 产品协同”。

可用判断：
- 不是每个维度都最强，但很可能适合输入密集、长上下文、多步工具调用的 Agent 场景。
- 它代表腾讯把模型竞争从“刷榜叙事”拉回“真实产品可用性和成本账”。
- 仍需保留：preview 非正式版、外部独立测评不够多、自部署门槛高、许可可能影响第三方云厂商托管。

## 可保留原图

官方 GitHub README 里有多张评测图，适合下载为 `original-*` 原图直接用，不要用 AI 抽象图替代：

- `https://raw.githubusercontent.com/Tencent-Hunyuan/Hy3-preview/main/assets/bench_stem.jpg`
- `https://raw.githubusercontent.com/Tencent-Hunyuan/Hy3-preview/main/assets/bench_context.jpg`
- `https://raw.githubusercontent.com/Tencent-Hunyuan/Hy3-preview/main/assets/bench_agent_overview_v3.jpg`
- `https://raw.githubusercontent.com/Tencent-Hunyuan/Hy3-preview/main/assets/bench_claw_agent.png`
- `https://raw.githubusercontent.com/Tencent-Hunyuan/Hy3-preview/main/assets/bench_claw_agent2.jpg`

发布前建议压缩到 1280px 宽以内，避免 publish.py 上传大图超时：

```bash
sips -s format jpeg -s formatOptions 78 -Z 1280 original-xx.jpg --out compressed-original-xx.jpg
```

文章中引用压缩图的绝对路径。
