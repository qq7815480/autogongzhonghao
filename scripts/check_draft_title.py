#!/usr/bin/env python3
"""检查微信公众号草稿箱里是否已有完全同名草稿。只读，不删除、不创建。"""

from __future__ import annotations

import argparse
import json

import requests

from config import set_account
from wechat_token import get_access_token

API_BASE = "https://api.weixin.qq.com/cgi-bin"


def find_exact_title(account: str, title: str, page_size: int = 20) -> list[str]:
    set_account(account)
    token = get_access_token()
    url = f"{API_BASE}/draft/batchget?access_token={token}"
    offset = 0
    matches: list[str] = []

    while True:
        payload = {"offset": offset, "count": page_size, "no_content": 1}
        response = requests.post(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        # 微信接口常省略 charset；requests 可能按 Latin-1 解码，导致中文标题乱码、精确查重失效。
        data = json.loads(response.content.decode("utf-8"))
        if data.get("errcode"):
            raise RuntimeError(
                f"draft/batchget failed [{data.get('errcode')}]: {data.get('errmsg')}"
            )

        items = data.get("item", [])
        for item in items:
            for article in item.get("content", {}).get("news_item", []):
                if article.get("title") == title:
                    matches.append(item.get("media_id", ""))

        offset += len(items)
        if not items or offset >= data.get("total_count", 0):
            break

    return [media_id for media_id in matches if media_id]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="按完整标题检查微信公众号草稿箱，避免重复创建草稿"
    )
    parser.add_argument("--account", default="main")
    parser.add_argument("--title", required=True)
    args = parser.parse_args()

    matches = find_exact_title(args.account, args.title)
    print(
        json.dumps(
            {"title": args.title, "count": len(matches), "media_ids": matches},
            ensure_ascii=False,
        )
    )
    return 2 if matches else 0


if __name__ == "__main__":
    raise SystemExit(main())
