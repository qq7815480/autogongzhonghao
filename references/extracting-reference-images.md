# 从参考文章提取原图

当用户给微信公众号文章链接作为参考时，原文中的截图（软件界面、操作步骤、产品功能展示）**必须保留原图**，不能用 AI 生成的抽象图替代。

## 提取流程

### 1. 获取图片 URL

在浏览器中打开参考文章，用 JavaScript 提取所有微信 CDN 图片：

```javascript
// 在 browser_console 中执行
const images = document.querySelectorAll('img');
const imageUrls = [];
images.forEach((img, index) => {
  const src = img.getAttribute('data-src') || img.src;
  if (src && src.includes('mmbiz.qpic.cn')) {
    imageUrls.push({
      index: index + 1,
      url: src,
      alt: img.alt || ''
    });
  }
});
JSON.stringify(imageUrls, null, 2);
```

### 2. 下载图片（带防盗链绕过）

微信 CDN 有防盗链，必须带 Referer 头：

```bash
cd ~/.hermes/skills/wechat-publisher/sunwork/<date-slug>/images

curl -s -o screenshot-xxx.png \
  -H "Referer: https://mp.weixin.qq.com/" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "<image_url>"
```

**命名规范**：用 `screenshot-` 前缀命名原图（如 `screenshot-computer-use.png`），方便阶段四识别哪些段落已有原图。

### 3. 在 article.md 中使用绝对路径

**⛔ 铁律：必须用绝对路径**

```markdown
![描述](/Users/sun/.hermes/skills/wechat-publisher/sunwork/<date-slug>/images/screenshot-xxx.png)
```

不要用相对路径 `images/screenshot-xxx.png`，publish.py 在 scripts/ 目录下运行时会解析失败，图片全部跳过。

### 4. 验证下载成功

```bash
ls -la images/screenshot-*.png | wc -l
# 检查文件大小，0 字节表示下载失败
```

## 常见坑

- **web_extract 无法提取微信文章**：返回 "Blocked: URL targets a private or internal network address"，必须用 browser_navigate + browser_console
- **部分图片格式无效**：微信文章中可能有 webp 格式图片，上传到微信 CDN 时报 40137 invalid image format，这些图片会上传失败但不影响其他图片
- **封面图和作者头像跳过**：提取时过滤掉 `cover_image` 和 `作者头像` 类型的图片
