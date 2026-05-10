# 微信公众号文章发布完整工作流

本文档记录了从选题到发布草稿箱的完整流程，供 Agent 和开发者参考。

## 流程概览

```
阶段一: 理解需求与收集素材
    ↓
阶段二: 全网信息搜索与整理
    ↓
阶段 2.5: 素材分类与多媒体处理
    ↓
阶段三: 撰写骨架稿
    ↓ ⛔ 暂停，等用户审阅
阶段 3.5: 人味化改写 (反 AI 检测核心)
    ↓
阶段四: 生成配图 (baoyu-article-illustrator)
    ↓
阶段 4.5: 生成封面图 (baoyu-cover-image)
    ↓
阶段五: AI 味自检 gate + 格式转换与发布
    ↓
阶段六: 告知用户
```

## 前置条件

### 1. 配置文件

复制模板并填入真实凭证：

```bash
cp wechat-publisher.yaml.example wechat-publisher.yaml
```

配置结构：

```yaml
default: main

accounts:
  main:
    name: "你的公众号名称"
    app_id: "wx1234567890abcdef"        # 从微信公众平台获取
    app_secret: "your_app_secret_here"  # 从微信公众平台获取
    author: "作者名"
    theme: "warm-editorial"             # 排版主题
    image_style: "hand-drawn-blue"      # 配图风格
    voice: |
      写作风格描述...

image_generation:
  generator: "baoyu-image-gen"

integrations:
  wechatsync_mcp_token: ""
```

### 2. IP 白名单

在微信公众平台后台添加当前机器的公网 IP：

```bash
curl ifconfig.me  # 获取公网 IP
```

### 3. 验证连接

```bash
cd scripts
python3 -c "from wechat_api import get_access_token; print('连接成功:', get_access_token()[:10]+'...')"
```

## 阶段一: 理解需求与收集素材

**目标**: 搞清楚用户要什么，采集真人味原料。

### 执行步骤

1. **分析用户输入**
   - 有参考文章: 读完，提取核心观点、独特素材、数据、案例
   - 只给话题: 确认目标账号，询问用户是否有个人亲历细节

2. **识别目标账号**: 根据话题自动选账号，加载对应 voice

3. **产出**: `sunwork/<date-slug>/brief.md`

### ⛔ 参考文章处理规则

参考文章是"原料"不是"模板"：
- **提取素材**: 核心数据、独特案例、关键观点
- **丢掉结构**: 不看原文小节划分，自己重新组织
- **用自己的话讲**: 不是"换个说法"而是"重新讲述"
- **加入"我"**: 必须有自己的判断、经历、踩坑
- **必须问用户**: 有什么亲历细节？踩过什么坑？

### 文章细节规范

- **时间**: 用"最近"、"今天"等模糊时间，不用具体时间点
- **案例**: 换成大众常见的通用场景，不用小众项目
- **术语**: 替换成更接地气的通用内容

## 阶段二: 全网信息搜索与整理

**目标**: 既要权威数据，也要真人语料。

### 权威层
- 最新资讯 + 数据 (优先 6 个月内)
- 相关案例 / 故事
- 专家观点 / 官方报告 / Release Notes

### 真人层 (反 AI 检测原料)
- Reddit / HackerNews / V2EX / 即刻 / 少数派的帖子原话
- X (Twitter) 上当事人 / 员工的发言原文
- 小红书 / 知乎的一线用户吐槽
- 产品具体的 commit message / issue 讨论

### 产出
`sunwork/<date-slug>/research.md`，每个素材标来源。

## 阶段 2.5: 素材分类与多媒体处理

**核心原则: 有原图的优先用原始素材，不用 AI 生成的抽象图替代。**

### 分类规则

| 素材类型 | 处理方式 |
|---|---|
| 软件截图 / 产品界面 | 保留原图，下载后直接上传微信 CDN |
| 视频内容 | 嵌入视频播放代码或截图+引导 |
| 数据图表 / 对比图 | 保留原图 |
| 纯文字观点 / 概念 | 生成手绘配图 |

### 原图命名规范

下载的原图必须用 `original-` 或 `screenshot-` 前缀命名：
- `original-seed-benchmark.png`
- `screenshot-wechat-settings.jpg`

## 阶段三: 撰写骨架稿

**目标**: 按结构写出初稿。允许这一稿有 AI 味，下一阶段专门负责"人味化"。

### 文章结构模板

```markdown
# 标题 (抓眼球，15-25 字)

> 摘要引言 (1-2 句话)

## 开篇
(用具体场景/数字/人物/对话切入，禁止"随着 XX 的飞速发展")

## 小节一: xxx

## 小节二: xxx

## 小节三: xxx

## 写在最后
```

### 文章规模

- 小节数量: 3-6 个
- 配图数量: 6-10 张
- 总字数: 2500-5000 字
- ⛔ 参考文章长度约束: 改写后 ±10% 以内

### 排版增强标记

| 标记 | 效果 | 用途 |
|---|---|---|
| `**文本**` | 主加粗 | 最重要结论，一段最多 1 次 |
| `==文本==` | 黄色背景高亮 | 关键数据 / 核心论点 |
| `++文本++` | 蓝色背景高亮 | 概念定义 / 工具名 |
| `%%文本%%` | 粉色背景高亮 | 警示 / 陷阱 |
| `&&文本&&` | 绿色背景高亮 | 正面结果 / 推荐做法 |
| `!!文本!!` | 红色强调 | 警告 / 反对 |
| `@@文本@@` | 蓝色强调 | 术语 / 产品名 |
| `^^文本^^` | 橙色强调 | 温暖点缀 |

**密度**: 每 500 字 3-5 处行内标记，至少混用 4 种类型。

### ⛔ 阶段三完成后必须暂停

把文章全文发给用户审阅，等用户确认后再进入阶段四。

## 阶段 3.5: 人味化改写 (反 AI 检测核心)

**快捷路径**: 如果阶段三已主动应用全部 9 条规则且 ai_score < 35，可跳过。

### 反 AI 检测强制清单

**① Burstiness (句长抖动)**
- 相邻三句字数差出现至少一次 >15 字
- 每 3-4 个长句插入一个 5-12 字短句
- 禁止连续 4 句都是 25-40 字标准长句

**② 禁用词清单** (命中 >1 次必须替换)
```
首先/其次/最后   不仅...而且   一方面...另一方面
值得一提的是     不可否认       毋庸置疑
综上所述         总而言之       由此可见
众所周知         不难发现       显而易见
在...的背景下    随着...的发展  站在...的角度
```

**③ AI 高频词黑名单** (命中 >2 次必须替换)
```
赋能/打造/聚焦/深度融合/生态/闭环/链路/抓手/
价值链/护城河/方法论/底层逻辑/生态位/结构化思维/
提升效率/助力/全链路/一站式/端到端/量变到质变/
引领/颠覆/革命性/前所未有/核心竞争力/范式/
降本增效/数字化转型/产业升级/破局/出圈/沉淀/
深耕/蓝图/新篇章
```

**④ 开头破冰规则**
禁止从宏观背景切入。改为: 具体场景/数字/话/人物

**⑤ 人称和立场**
- 全文 ≥3 次第一人称"我"的主观表达
- 允许不确定表达: "我可能说错了"、"存疑"

**⑥ 事实密度**
每 500 字 ≥1 个具体数字或专有名词

**⑦ 标点多样性**
- 破折号 `——` ≥1 次
- 问号 ≥2 次
- 括号插入 `(...)` ≥1 次
- 省略号 `...` ≤3 次

**⑧ 结构的"不完美"**
允许: "扯远了，回到主题"、反悔句、自嘲、小节长度不对称

**⑨ 按账号 voice 做语气过滤**

## 阶段四: 生成配图

使用 `baoyu-article-illustrator` skill 生成正文配图。

### 前置步骤 (必须先执行)

```bash
# 扫描 article.md 中已有的图片引用
grep -oP '!\[.*?\]\((.*?)\)' article.md
```

- `images/original-*` 或 `images/screenshot-*` → 原图，跳过
- 只为没有原图的纯文字段落生成 AI 配图

### 配置

- style: hand-drawn (暖色纸+手绘线条)
- palette: warm (暖色调)
- language: zh (中文文字标注)

### ⛔ 铁律

有原图的段落绝对不能再用 AI 生成替代图。

## 阶段 4.5: 生成封面图

使用 `baoyu-cover-image` skill，每次发文必须单独生成封面图。

### 封面图安全区规则

GPT Image 2 只支持 16:9，微信封面需要 2.35:1。裁切时会切掉上下约 30%。

**在 prompt 中必须加入**：
```
【安全区要求】
- 核心内容（标题文字、主要视觉元素）集中在画面中央 60% 区域
- 上下各留 20% 空白/背景区域（会被裁切掉）
- 标题文字居中放置，不要靠近上下边缘
```

### 裁切命令

```bash
sips --cropToHeightWidth 653 1536 cover_raw.png --out cover.png
```

### 验证

检查封面图，确保标题和主要元素完整可见。

## 阶段五: AI 味自检 + 格式转换与发布

### 手动预检

```bash
cd scripts
python3 ai_score.py /path/to/article.md --threshold 45
```

阈值约定:
- < 35: 🟢 PASS，可以发
- 35-45: 🟡 WARN，建议再改一轮
- ≥ 45: 🔴 FAIL，必须回到阶段 3.5 重写

### 一键发布

```bash
cd scripts
python3 publish.py \
  --account main \
  --input /path/to/article.md \
  --cover /path/to/cover.jpg \
  --title "文章标题" \
  --digest "120字以内摘要"
```

publish.py 自动: 读取账号配置 → 跑 AI 味 gate → 处理图片 → HTML 转换 → 封面上传 → 创建草稿

## 阶段六: 告知用户

- 告知草稿已保存到草稿箱
- 提醒用户登录 mp.weixin.qq.com 查看并手动确认发布
- 文章不会自动群发

## 文件结构

```
sunwork/<date-slug>/
├── brief.md          # 阶段一产出
├── research.md       # 阶段二产出
├── article.md        # 阶段三/3.5 产出
├── images/
│   ├── original-*.png    # 原图 (阶段 2.5)
│   ├── screenshot-*.jpg  # 截图 (阶段 2.5)
│   ├── 01.png            # AI 配图 (阶段四)
│   └── ...
└── cover.jpg         # 封面图 (阶段 4.5)
```

`<date-slug>` 格式: `20260504-topic-slug` (日期+短横线+语义化)

## 常用命令

```bash
SCRIPTS=scripts

# 列出已配置账号
python3 $SCRIPTS/wechat_api.py list-accounts

# 列出排版主题
python3 $SCRIPTS/html_converter.py --list-themes

# 只做格式转换
python3 $SCRIPTS/html_converter.py article.md --theme warm-editorial -o article.html

# 上传图片到微信 CDN
python3 $SCRIPTS/image_handler.py upload photo.jpg

# AI 味检测
python3 $SCRIPTS/ai_score.py article.md --threshold 45
```

## 常见坑

### 图片路径必须用绝对路径

article.md 中的图片引用必须使用绝对路径，不能用相对路径。publish.py 在 scripts/ 目录下运行时，相对路径会解析失败。

### 微信草稿 API 标题长度限制

实测约 36 字节 UTF-8（约 12 个中文字符），超长会报 45003。摘要限制约 41 字节，超长报 45004。

### publish.py 大文件超时

文章含多张大图（3MB+）时容易超时。解决方案：分步执行——先手动上传封面，再逐张上传正文图，然后转 HTML，最后创建草稿。

### 封面图比例裁切

GPT Image 2 只支持 16:9/9:16/1:1，无法直接生成 2.35:1。生成后必须用 sips 裁切。

### 微信 CDN 防盗链

`image_handler.py` 已增强，自动处理防盗链：
- 自动添加 `Referer: https://mp.weixin.qq.com/` 头
- 下载后用 magic bytes 验证是否为真图片
- 失败时自动用 curl 带完整浏览器 headers 重试

### 中文编码

创建草稿必须用 `api.add_draft()`，严禁 `requests.post(json=data)`（默认 ensure_ascii=True 会导致中文乱码）。

### 防止重复草稿

创建草稿前，先用 draft/batchget 检查是否已有同标题草稿。清理草稿时必须用精确的 media_id，严禁关键词模糊匹配删除。

## 排版主题

内置 16 套主题，位于 `assets/themes/*.json`。

| 类别 | 推荐主题 |
|---|---|
| AI / 产品 / 深度分析 | `refined-blue` · `warm-editorial` · `business-navy` |
| 技术 / 工程 | `minimal-mono` · `minimal-bw` · `cyber-neon` |
| 新闻 / 热点 | `news-bold` · `warm-editorial` |
| 人文 / 随笔 | `ink-wash` · `elegant-ink` |
| 生活 / 美食 | `warm-orange` · `mint-fresh` |
| 时尚 / 情感 | `girly-pink` · `sunset-coral` |

## 视觉风格体系

| 组件 | 工具 | 风格 |
|---|---|---|
| 封面图 | baoyu-cover-image | scene + earth + hand-drawn + subtle |
| 正文配图 | baoyu-article-illustrator | hand-drawn + warm |
| 排版主题 | warm-editorial | 栗色暖调 + 米白纸 + 宋体 |
| 生图后端 | GPT Image 2 | openai-codex (Codex OAuth) |
