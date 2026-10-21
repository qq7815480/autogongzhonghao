#!/usr/bin/env python3
"""Verify a WeChat draft by exact media_id with UTF-8-safe decoding.

Checks title, author, digest, cover, body image count, CDN replacement, and absence
of local filesystem paths. Exits non-zero on any mismatch.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import set_account  # noqa: E402
from wechat_token import get_access_token  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", default="main")
    parser.add_argument("--media-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--digest", required=True)
    parser.add_argument("--image-count", required=True, type=int)
    args = parser.parse_args()

    set_account(args.account)
    token = get_access_token()
    response = requests.post(
        f"https://api.weixin.qq.com/cgi-bin/draft/get?access_token={token}",
        data=json.dumps({"media_id": args.media_id}, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=30,
    )
    response.raise_for_status()
    data = json.loads(response.content.decode("utf-8"))
    if data.get("errcode"):
        raise SystemExit(f"VERIFY_FAIL {json.dumps(data, ensure_ascii=False)}")

    items = data.get("news_item") or []
    if not items:
        raise SystemExit("VERIFY_FAIL draft/get returned no news_item")
    article = items[0]
    content = article.get("content", "")
    actual = {
        "title": article.get("title"),
        "author": article.get("author"),
        "digest": article.get("digest"),
        "image_count": content.count("<img"),
        "cdn_image_count": content.count("mmbiz.qpic.cn"),
        "content_length": len(content),
        "thumb_media_id": article.get("thumb_media_id"),
        "local_path_count": content.count("/Users/") + content.count("file://"),
    }
    expected = {
        "title": args.title,
        "author": args.author,
        "digest": args.digest,
        "image_count": args.image_count,
    }

    errors = []
    for key, value in expected.items():
        if actual[key] != value:
            errors.append(f"{key}: expected={value!r}, actual={actual[key]!r}")
    if actual["cdn_image_count"] < args.image_count:
        errors.append(
            f"cdn_image_count: expected>={args.image_count}, actual={actual['cdn_image_count']}"
        )
    if not actual["thumb_media_id"]:
        errors.append("thumb_media_id is empty")
    if actual["local_path_count"]:
        errors.append(f"local_path_count: expected=0, actual={actual['local_path_count']}")

    result = {"media_id": args.media_id, **actual}
    if errors:
        print(json.dumps({"status": "failed", "errors": errors, **result}, ensure_ascii=False))
        return 1
    print(json.dumps({"status": "verified", **result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
