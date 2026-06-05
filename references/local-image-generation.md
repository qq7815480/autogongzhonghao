# 本地 API 生图约定

适用场景：wechat-publisher 流程中的封面图、正文配图、商品图或其它公众号素材生图。

## 固定原则

- 默认走本地 OpenAI-compatible 生图 API，不走外部生图服务。
- 默认 Hermes 路由：`local-openai-image / gpt-image-2（image2）`。
- 从当前 Hermes 配置读取 `image_gen.local-openai-image`，不要硬编码 token。
- 生成后保存为本地文件，回复用户时发本地文件/附件，不发远程链接。
- 图片中如有文字、标注、标题，必须明确要求中文。

## 推荐调用方式

1. 读取 `~/.hermes/config.yaml` 中 `image_gen.local-openai-image` 的 base_url、model、api_key/token 配置。
2. 调用本地 `/v1/images/generations`。
3. 保存返回图片到当前工作目录或 `sunwork/<date-slug>/images/`。
4. 对公众号正文图片，插入 article.md 前必须使用绝对路径。
5. 对封面图，生成 16:9 后按微信 2.35:1 规则裁切，并验证安全区。

## 注意

历史上 Codex OAuth / openai-codex 方案可以作为旧方案排障参考，但不再作为默认路径。不要因为旧文档提到 `image_generate` 或 `openai-codex` 就绕过本地 API。