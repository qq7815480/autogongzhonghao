# baoyu 正文图/封面风格恢复流程

适用场景：公众号文章已经写好，但正文 AI 信息图或封面被做成了默认信息卡、PIL 卡片、科技蓝 PPT 风，用户要求恢复为 baoyu-article-illustrator / baoyu-cover-image 的暖色手绘杂志风。

## 关键教训

如果用户明确要求“baoyu 那个 skill / 之前 baoyu 的风格 / 不要默认风格”，不能用确定性 PIL 信息卡或默认卡片风兜底后直接发布。PIL 卡片只能在用户明确接受兜底，或生图完全不可用且为了不中断发布时临时使用。只要用户指出风格不对，必须重做并重新创建新版草稿，旧草稿提醒用户不要用。

## 正确补救步骤

1. 保留原版截图：`original-*`、`screenshot-*` 不动，不用 AI 图替代。
2. 只替换 AI 生成的信息图和封面：把正文中非原图的信息图路径替换为 `baoyu-*` 文件。
3. 每张图先写 prompt 文件到 `prompts/`，内容必须包含：
   - 文章中的真实信息点；
   - 中文标题和中文标注；
   - 暖色文艺杂志风、手绘线条、米白纸张背景、柔和土色调、轻微颗粒；
   - 明确禁止：默认PPT卡片、科技蓝、冰冷扁平UI、英文。
4. 正文图用 baoyu-article-illustrator 风格：warm / hand-drawn / editorial magazine。
5. 封面用 baoyu-cover-image 风格：scene + earth + hand-drawn + subtle，并写安全区要求：核心内容集中中央 60%，上下各留 20% 空白，再裁切成 2.35:1。
6. 替换 `article.md` 后检查：
   - 所有图片路径都是绝对路径；
   - `grep -n '!\[' article.md` 能看到原图 + baoyu 图；
   - 没有残留默认卡片图路径。
7. 重新跑 `ai_score.py`。
8. 用 `publish.py --input article.md --cover baoyu-cover.jpg` 创建新版草稿。
9. 告诉用户新版 media_id，并明确旧草稿不要用。

## 本地 image_generate 502 时的恢复模式

有时 Hermes 的 `image_generate` 封装返回 502，但同一台机器的本地 OpenAI-compatible 图片 API 仍可直连成功。不要立刻退回 PIL 默认卡片。先按下面方式诊断：

1. 查看 `~/.hermes/config.yaml`：
   - `image_gen.local-openai-image.base_url`
   - `image_gen.local-openai-image.api_key`
   - `image_gen.local-openai-image.model`
2. 直接请求 `${base_url}/images/generations`，payload 形如：
   - `model: gpt-image-2`
   - `prompt: <baoyu prompt>`
   - `size: 1536x1024`
3. 如果返回 `b64_json`，解码写入 `images/baoyu-*.png`。
4. 对封面图：先生成 1536×1024 原图，再用 PIL 或 `sips --cropToHeightWidth 653 1536` 居中裁切为 `baoyu-cover.jpg`。

注意：如果直连也失败，才报告生图链路故障；不要发布默认卡片风的“新版”。

## 话术

如果用户指出“为什么没按 baoyu 风格”：

- 先承认是流程执行错，不要辩解；
- 说明会保留原版截图，只重做 AI 信息图和封面；
- 重新发新版草稿，明确旧草稿不要用。