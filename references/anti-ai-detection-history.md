# 反 AI 检测演进记录

## 2026-06-20: 合并 humanizer-zh 模式

将 `humanizer-zh` skill 中适合中文公众号的模式选择性合并进 wechat-publisher 阶段 3.5。

### 合并来源
- `humanizer-zh`（GitHub: Feodasha/awesome-Humanizer-zh）— 24 条英文反 AI 模式
- 约 1/3 对中文公众号不适用（curly quotes、title case、em dash、表格分割线、bullet 变 em dash 等英文排版细节）
- 选择性提取了 6 条适配中文的模式

### 新增到 SKILL.md 阶段 3.5 的 6 条

| 编号 | 名称 | 来源 | 检查方法 |
|------|------|------|----------|
| ⑩ | 系动词回避 | humanizer-zh #7 | 搜"堪称/充当/扮演...的利器/桥梁" |
| ⑪ | 同义词循环 | humanizer-zh #9 | 一段 3+ 种称呼指代同一东西 |
| ⑫ | 营销化/夸张语气 | humanizer-zh #4 | 搜"震撼/神器/杀疯了"等广告词 |
| ⑬ | 虚假对比范围 | humanizer-zh #13 | "从小白到大佬"式假排比 |
| ⑭ | 无主语/被动滥用 | humanizer-zh #14 | "效率提升300%"无主语 |
| ⑮ | 预告+空洞结尾 | humanizer-zh #19+#20 | "接下来让我们"+"未来可期" |

### 流程升级
- 从"9条清单逐条过"升级为"三遍扫描"
- 第二遍新增"灵魂注入"（有观点/有节奏/有矛盾/有具体感受/有口头禅/允许不完美）
- 第三遍新增"终审"（自问"什么让这篇文章一看就是AI写的？"）

### ai_score.py 更新
- AI_PHRASES: 31 → 58 条（+27 条新正则）
- AI_VOCAB: 47 → 62 个（+15 个新词）
- 新增检测维度: 系动词模式、预告句、虚假排比、广告腔、空洞结尾

### 未合并的 humanizer-zh 模式（不适用中文公众号）
- curly quotes / smart quotes（英文排版）
- title case（英文大小写）
- em dash 过度使用（中文破折号用法不同）
- 表格 vs 项目符号切换（排版偏好，非 AI 信号）
- 省略号格式（中文用 `...`，非英文 `...`）
- 时间和缩写（英文如 Jan vs January，中文无此问题）
- 通用术语混用（英文如 utilize vs use，中文无直接对应）

### 注意事项
- ai_score.py 中的正则已用中文语料验证，"精准/智能化/深度学习/智能体/Agent"等技术术语已排除（太常见会误报）
- AI_VOCAB 中"新格局"只保留一次（之前列表有重复但 Python list 不去重，已修复）
