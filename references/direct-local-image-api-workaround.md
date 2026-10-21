# 本地生图 API 直连兜底流程

适用场景：公众号发文配图/封面阶段，Hermes `image_generate` 调本地 `local-openai-image / gpt-image-2` 返回 502，但本地 OpenAI-compatible 服务本身可能仍可用。

核心经验：不要反复用同一个 `image_generate` 参数重试。先诊断本地 API，再改用直连 `/images/generations` 串行生成。

## 诊断

1. 读 `~/.hermes/config.yaml` 中 `image_gen.providers.local-openai-image` 或 `image_gen.local-openai-image` 的：
   - `base_url`
   - `api_key`
   - `model`
2. 用 Python requests 直连：

```python
import os, yaml, requests, json
cfg = yaml.safe_load(open(os.path.expanduser('~/.hermes/config.yaml')))
ig = cfg['image_gen']['providers']['local-openai-image'] if 'providers' in cfg.get('image_gen', {}) else cfg['image_gen']['local-openai-image']
base = ig['base_url'].rstrip('/')
key = ig['api_key']
model = ig.get('model', 'gpt-image-2')
r = requests.post(
    base + '/images/generations',
    headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
    json={'model': model, 'prompt': '测试：暖色手绘技术插画，中文标注', 'size': '1536x1024', 'n': 1},
    timeout=120,
)
print(r.status_code, r.text[:500])
```

如果这里返回 200，说明本地服务可用，是 Hermes image tool 路由层失败；可以继续用直连方式生成。

### `empty_response` 的进一步定位

如果 `image_generate` 不是 502，而是返回 `Local image API returned no image data` / `empty_response`，同时直连 `/images/generations` 得到 HTTP 200，常见原因不是上游故障，而是**插件调用的端点和解析的数据结构不匹配**：

- OpenAI Images 兼容端点通常返回 `data[0].b64_json` 或 `data[0].url`
- Responses 图像工具通常返回 `output[]` 中的 `image_generation_call.result`
- 本地代理只实现前一种，而 provider 仍调用 `/responses`、按后一种结构解析时，就会出现“请求成功但没有图片数据”

处理顺序：

1. 先备份 provider 文件，不要直接覆盖：
   ```bash
   stamp=$(date +%Y%m%d_%H%M%S)
   mkdir -p "$HOME/.hermes/backups/local-openai-image_$stamp"
   cp "$HOME/.hermes/plugins/image_gen/local-openai-image/__init__.py" \
      "$HOME/.hermes/backups/local-openai-image_$stamp/__init__.py"
   ```
2. 检查 provider 实际请求的是 `/responses` 还是 `/images/generations`，以及解析的是 `output[].result` 还是 `data[].b64_json`。
3. 对只支持 Images API 的本地代理，将请求改为 `/images/generations`，payload 至少包含 `model`、`prompt`、`size`、`response_format: b64_json`；结果读取 `data[0].b64_json`，并保留 `url` 作为兼容分支。
4. 运行 `python3 -m py_compile` 验证语法。
5. **已运行的 Hermes/Gateway 可能仍缓存旧模块**。改完文件后，新的 `image_generate` 调用仍报同样错误，不代表修复无效；需要重启加载 provider 的进程后再验证。若当前会话不适合重启，临时使用下文的串行直连脚本，或从 Hermes venv 启动一个新 Python 进程加载已修复 provider。
6. 修复后用一张最小测试图验证：返回成功、本地文件存在、文件可被图片解码，然后再批量生成。

### 凭据安全

- 不要打印整个 `image_gen` 配置或 provider 字典；浅层脱敏会漏掉嵌套的 `api_key`。
- 诊断脚本只输出 HTTP 状态码、响应顶层键、`data` 长度和图片项键名；不要输出 Authorization header、API key 或完整配置。
- 若要记录响应，先移除可能包含凭据或大段 base64 的字段。

## 串行生成脚本模板

要求：仍然必须先把每张图的完整 prompt 保存到 `prompts/NN-xxx.md`，再调用 API。不要跳过 prompt 文件记录。

```python
import os, yaml, requests, base64, pathlib, time
root = pathlib.Path('/path/to/article-dir')
cfg = yaml.safe_load(open(os.path.expanduser('~/.hermes/config.yaml')))
ig = cfg['image_gen']['providers']['local-openai-image'] if 'providers' in cfg.get('image_gen', {}) else cfg['image_gen']['local-openai-image']
base = ig['base_url'].rstrip('/')
key = ig['api_key']
model = ig.get('model', 'gpt-image-2')
headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}

tasks = [
    (root/'images/prompts/01-example.md', root/'images/01-example.png'),
    (root/'cover/prompts/01-cover.md', root/'cover/cover_raw.png'),
]

for idx, (prompt_file, out_file) in enumerate(tasks, 1):
    prompt = prompt_file.read_text()
    payload = {'model': model, 'prompt': prompt, 'size': '1536x1024', 'n': 1}
    for attempt in range(2):
        r = requests.post(base + '/images/generations', headers=headers, json=payload, timeout=240)
        if r.status_code == 200:
            data = r.json()['data'][0]
            raw = base64.b64decode(data['b64_json']) if 'b64_json' in data else requests.get(data['url'], timeout=120).content
            out_file.write_bytes(raw)
            print('saved', out_file, len(raw))
            break
        print('failed', r.status_code, r.text[:300])
        time.sleep(5)
    else:
        raise RuntimeError(f'failed to generate {out_file}')
```

## 发布前图片压缩建议

`gpt-image-2` 产出的 PNG 往往 2-3MB+，`publish.py` 大图上传容易慢或超时。正文图可以先转为 1280px 宽 JPG：

```python
from PIL import Image
from pathlib import Path
root = Path('/path/to/article-dir/images')
for png in sorted(root.glob('0*.png')):
    im = Image.open(png).convert('RGB')
    w, h = im.size
    nw = 1280
    nh = int(h * nw / w)
    im = im.resize((nw, nh), Image.LANCZOS)
    out = png.with_suffix('.jpg')
    im.save(out, quality=88, optimize=True, progressive=True)
```

然后在 `article.md` 中引用 JPG 的绝对路径。

## 封面裁切

封面仍按 16:9 生成，然后裁切公众号封面比例：

```bash
sips --cropToHeightWidth 653 1536 cover_raw.png --out cover.png
sips -g pixelWidth -g pixelHeight cover.png
```

确保封面 prompt 写明：核心内容在中央 60%，上下各留 20% 空白，防止裁切掉标题。