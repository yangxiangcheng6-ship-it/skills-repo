#!/usr/bin/env python
"""拉取标准/偏离两库文档清单 → doc_list 格式（[KB名] doc_type值 | 摘要 | 文件名）。

用法:
    python list_docs.py
输出: JSON {"doc_list": "多行文本"}
环境变量可覆盖: DIFY_API_URL  DIFY_API_KEY
"""
import json
import os
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 本地 Dify 直连，禁用系统代理（梯子开着时 localhost 会被发给代理 → 502）
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))


def _first_reachable(urls: list[str], timeout: float = 1.0) -> str:
    """容器内执行（skill_agent 插件）优先用容器名地址，失败回退 localhost"""
    import socket
    import urllib.parse
    for url in urls:
        parsed = urllib.parse.urlparse(url)
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            socket.create_connection((parsed.hostname, port), timeout=timeout).close()
            return url
        except OSError:
            continue
    return urls[-1]


API_URL = os.environ.get("DIFY_API_URL", _first_reachable(["http://api:5001/v1", "http://127.0.0.1/v1"]))
API_KEY = os.environ.get("DIFY_API_KEY", "dataset-Kz491fr3x8jSWR8QEC8BYG3Z")

KBS = [
    ("标准docx", "67b0a079-38e2-4c60-83e6-933bba670695"),
    ("偏离docx", "3e588f3f-9930-44b5-a060-740bdcf4db7c"),
]


def fetch_docs(kb_name: str, dataset_id: str) -> dict:
    req = urllib.request.Request(
        f"{API_URL}/datasets/{dataset_id}/documents?limit=50",
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> None:
    lines = []
    for kb_name, ds_id in KBS:
        try:
            data = fetch_docs(kb_name, ds_id)
        except urllib.error.HTTPError as e:
            print(json.dumps({"error": f"拉取 {kb_name} 文档清单失败: HTTP {e.code}"}, ensure_ascii=False))
            return
        except Exception as e:
            print(json.dumps({"error": f"拉取 {kb_name} 文档清单失败: {e}"}, ensure_ascii=False))
            return
        for doc in data.get("data", []):
            meta = {m["name"]: m["value"] for m in doc.get("doc_metadata", []) if m.get("id") != "built-in"}
            lines.append(f"[{kb_name}] {meta.get('doc_type', '')} | {meta.get('doc_summary', '')} | {doc.get('name', '')}")
    print(json.dumps({"doc_list": "\n".join(lines)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
