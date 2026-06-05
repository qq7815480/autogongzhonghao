# 多篇参考文章处理流程

当用户给多篇参考文章（或先存档多篇再创作）时的处理模式。

## 典型场景

用户发多个链接 → 存档到 Obsidian → 基于多篇素材创作新文章

## 处理步骤

1. **逐篇提取**: 用 `browser_navigate` 抓取每篇文章（微信文章只能用浏览器，web_extract/jina 会被 CAPTCHA 拦截）
2. **存档到 Obsidian**: 作为素材备份，路径 `~/sunwork/ObsidianVault/📒 其他随记/`
3. **提取核心素材**: 从每篇中提取——
   - 独特数据/数字
   - 具体案例/人物/公司
   - 独家观点/判断
   - 可直接引用的金句
4. **丢掉原文结构**: 不按任何一篇的结构走，重新组织文章骨架
5. **融合改写**: 用自己的话重新讲述，不能原文复制

## ⛔ 严禁

- 跟着任何一篇参考文章的结构走
- 原文复制句子（哪怕换几个词）
- 做"三篇文章的总结"
- 只做结构重组不做语言改写

## ✅ 判断标准

- 读者觉得"这是老孙写的" → 成功
- 读者觉得"这是三篇参考文章的整合" → 失败

## 微信文章抓取

微信公众号文章 (mp.weixin.qq.com) 有反爬机制，按优先级尝试：

1. `web_extract` → ❌ "Blocked: URL targets a private or internal network address"
2. `mcp_jina_crawl4ai_jina_read` / `crawl4ai_crawl` → ❌ "环境异常，完成验证后即可继续访问"
3. `browser_navigate` → ✅ 通常可行（需 Camofox 运行）
4. **`curl` + python3 HTML 解析** → ✅ 最可靠的备用方案（不依赖浏览器）

### curl 备用方案（当 browser_navigate 也失败时）

```bash
curl -sL -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36' \
  'https://mp.weixin.qq.com/s/XXXXX' 2>/dev/null | python3 -c "
import sys, re
html = sys.stdin.read()
# 提取标题
title_match = re.search(r'<h1[^>]*id=\"activity-name\"[^>]*>(.*?)</h1>', html, re.DOTALL)
if title_match:
    print('TITLE:', title_match.group(1).strip())
# 提取正文
content_match = re.search(r'<div[^>]*id=\"js_content\"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
if content_match:
    text = content_match.group(1)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'\s+', ' ', text).strip()
    print(text[:12000])
"
```

关键点：
- 必须带真实 User-Agent，否则微信返回验证码页面
- 正文在 `<div id="js_content">` 里，用正则提取
- `&nbsp;` / `&amp;` 等 HTML 实体需要手动替换
- 上限 12000 字符通常够用，超长文章可调大

## 多篇参考文章的融合策略

### 正面+负面素材融合（"硬币两面"模式）

当用户给的多篇参考文章中，有正面介绍（功能更新、增长数据）也有负面/批评内容（限制收紧、用户投诉）时，采用"先扬后抑"结构：

1. **正面素材在前**：功能亮点、数据增长、用户好评 —— 建立"这事确实重要"的认知
2. **负面素材在后**：限制、代价、隐患 —— 作为"现实检验"，让文章有深度
3. **个人判断收尾**：不是简单的"好坏参半"，而是给出明确的使用建议

这种结构比纯吹或纯喷都更有说服力。读者会觉得作者"既了解好处也知道坑在哪"。

### 判断融合是否成功的标准

- 两篇素材的内容是否**自然衔接**（不是两块独立内容拼在一起）
- 是否有**自己的判断和过渡句**连接两个角度
- 读者是否觉得"这是一个完整的故事"而不是"两篇摘要"
