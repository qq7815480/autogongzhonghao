# First Validated Article Workflow (2026-05-04)

## Article: DeepSeek V4"转芯"：一张发往国产芯片的投名状

Topic: DeepSeek V4 native adaptation for domestic AI chips (Huawei Ascend 950PR), triggering semiconductor market rally.

## Pipeline Execution Log

### 阶段一: brief.md
- Created with topic, keywords, detailed fact list (12 items with specific numbers/names)
- User provided the topic reference article via Sina news aggregator
- Account: main (老孙/豌豆四喜)

### 阶段二: Search Strategy
- **Authority layer**: 3 parallel `web_search` queries (English AI news, Chinese AI news, specific company news)
- **Deep reads**: `mcp_jina_crawl4ai_jina_read` on CSDN article + Sina news aggregator page
- **Specific queries**: "DeepSeek V4 华为昇腾 国产芯片", "Anthropic Claude code leaked", "OpenAI 1220亿美元融资"
- **Real-person layer**: Zhihu discussions, Reddit r/DeepSeek, HackerNews, German public media (DW), engineering blog posts

### 阶段 2.5: Material Classification
- This topic was a news/commentary piece — no original screenshots or product UI to preserve
- All visual content would be AI-generated (hand-drawn illustrations)
- No video content to embed
- **Key learning**: For pure news/commentary articles without reference screenshots, 阶段2.5 is essentially a pass-through

### 阶段三: Writing
- Structure: 6 sections (开篇 + 4 body + 写在最后)
- Total: ~2950 words
- Inline color marks: 8 types used (bold, yellow highlight, blue highlight, pink highlight, green highlight, red emphasis, blue term emphasis, orange emphasis)
- Tables: 1 (芯片参数对比)
- Quotes: 知乎工程师原话, 田渊栋原话, 德国之声报道原话

### 阶段 3.5: Humanization Pass
- Fixed "在美国出口管制的背景下" → "美国卡着芯片出口" (ai_score flagged as AI套话)
- Fixed "闭环" count: 2→1 (replaced one with "链条...打通")
- All other 9 checklist items passed on first draft

### AI Score Result
```
总分: 21.5 / 100 🟢 PASS
[burstiness   ] 36.3  (CV=0.636, good)
[phrases      ] 15.0  (1 AI套话 hit)
[vocab        ] 25.4  (1.7/千字 AI词密度)
[structural   ]  0.0  (perfect)
[punctuation  ] 10.0  (40 人味标点, expected 14.7)
```

## Pitfalls Discovered

1. **"在...的背景下" is caught by ai_score.py** even when used in specific context. Always rephrase: "美国卡着芯片出口" instead of "在美国出口管制的背景下".

2. **"闭环" and "生态" are in the AI vocab blacklist**. Max 2 occurrences each. Use "链条" or "体系" as alternatives.

3. **For news/commentary articles without reference visuals**, 阶段2.5 (素材分类) and 阶段四 (配图生成) can be streamlined. The article may not need 6-10 illustrations if it's analysis-heavy with tables and data.

4. **Search strategy matters**: Running 3 parallel web_search queries (English, Chinese, company-specific) + deep-reading 2-3 key articles gives enough material for a 3000-word piece. Don't over-search.

5. **真人层 quotes add significant value**: 知乎工程师的直白评论、田渊栋的原话、德国之声的客观评价 —— 这些 make the article feel researched rather than generated.

6. **⛔ Chinese encoding bug (CRITICAL)**: `requests.post(json=data)` defaults to `ensure_ascii=True`, converting all Chinese to `\uXXXX` escapes. WeChat API renders these as garbled text. MUST use `api.add_draft()` which internally uses `json.dumps(ensure_ascii=False).encode('utf-8')`.

7. **⛔ Duplicate draft cleanup (CRITICAL)**: When cleaning up test/duplicate drafts, NEVER use keyword matching (e.g., "delete if title contains 'DeepSeek'"). This accidentally deleted the correct draft. ALWAYS use exact `media_id` for deletion. For debugging, use `test` titles with minimal content and delete immediately after.

8. **WeChat draft API byte limits**: Title ≤36 bytes UTF-8 (~12 Chinese chars), digest ≤41 bytes. Much lower than the 64-byte limit in official docs. Error codes: 45003 (title), 45004 (digest).
