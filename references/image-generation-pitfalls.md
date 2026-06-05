# 配图生成坑点记录

## 生图 API 并发超时 (2026-06-03)

`image_generate` 工具（local-openai-image / GPT Image 2）在并发生成多张图片时容易全部超时。

**现象**: 同时发起 3 张图片生成请求，全部返回 "Local image API generation failed: timed out"。逐张重试时每张都能成功。

**根因**: local-openai-image provider 不支持高并发，多请求同时打上去会导致所有请求排队超时。

**解决方案**:
- 逐张串行生成，不要并发
- 每张生成后复制到工作目录（自然间隔就够了）
- 如果连续超时，等 1-2 分钟让 API 冷却再重试
- prompt 尽量精简，过长的 prompt 也会增加生成时间

## 图片文件大小

GPT Image 2 输出的 PNG 通常 2.5-3.7MB，5 张正文图 + 1 张封面 = ~18MB。`publish.py` 一次性上传容易超时，必须用分步手动流程（见 manual-publish-workflow-v2.md）。

## cover.jpg 实际是 PNG

`sips --cropToHeightWidth` 输出的文件即使扩展名为 .jpg，实际格式仍是 PNG（`file` 命令可见）。微信 API 能正常处理，不影响发布。
