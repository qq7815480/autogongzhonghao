# Deterministic PIL fallback for WeChat article assets

Use this when an article needs to be finished and the normal image-generation route is slow, unavailable, rate-limited, or when the required visual is a structured explanatory card rather than a photorealistic illustration.

## When it fits

- News/commentary articles where正文配图 can be warm editorial cards, comparison cards, flow diagrams, quote cards, or checklist cards.
- Need reliable Chinese text rendering and exact labels.
- Need a cover quickly with safe crop behavior for WeChat.
- Need to avoid hallucinated screenshot-like “evidence”. For real evidence screenshots, keep original screenshots; for community discussion, label the image as an归纳/摘录 card unless real screenshot files were captured.

## Recommended asset set

For a 4k-7k字 AI/news commentary article:

- 1 official/source screenshot if available, named `screenshot-*` or `original-*`.
- 4-6 deterministic cards for pure concept sections.
- 1 cover raw image at 1536×1024, then center-crop to 1536×653 for WeChat 2.35:1.

## Implementation notes

Use Python + Pillow. On the user’s Mac, Chinese-capable fonts that worked:

- `/System/Library/Fonts/STHeiti Medium.ttc`
- `/System/Library/Fonts/STHeiti Light.ttc`
- `/System/Library/Fonts/Supplemental/Songti.ttc`

Visual defaults that match the existing公众号 style:

- Background: warm paper texture, e.g. RGB `(248,241,226)` with slight per-pixel noise.
- Primary text: dark brown `(64,39,30)`.
- Accent fills: cream, tan, muted brown/orange.
- Card size: 1200×760 for正文配图.
- Cover raw: 1536×1024. Put title and main visual in the central 60%; leave top/bottom around 20% as expendable background.
- Cover crop: center crop to 1536×653, or use `sips --cropToHeightWidth 653 1536 cover_raw.png --out cover.jpg` if the raw image has a safe center.

## Required verification

After generating deterministic assets:

1. Use vision inspection on at least the cover and one representative正文图.
2. Verify all markdown image paths are absolute.
3. Verify local files exist.
4. Run AI-score check before publishing.
5. Publish with `--input article.md`, not `--html`, and confirm output says正文图片上传成功 and `N/N` images uploaded.

## Pitfalls

- Do not call these cards “real screenshots” unless they are actual captured screenshots. Use wording like “讨论归纳图 / 用户评价卡片 / 示意图”.
- Do not replace original evidence screenshots with generated cards. Keep `original-*` and `screenshot-*` assets.
- Do not put cover text near the top or bottom; WeChat crop will cut it.
- Use absolute paths in `article.md`; relative `images/...` paths are resolved from the scripts directory by `publish.py` and will be skipped.
