#!/usr/bin/env python
"""执行 Dify 文档元数据打标（调 /datasets/{id}/documents/metadata）。

用法:
    python apply_metadata.py <dataset_id> <payload_json>
    payload_json 为 build_metadata.py 的输出（metadata_list, partial_update=true）
输出: JSON {"ok": true, "status": int, "response": ...} 或 {"ok": false, "error": ...}
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


def main() -> None:
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python apply_metadata.py <dataset_id> <payload_json>"}, ensure_ascii=False))
        return
    dataset_id = sys.argv[1]
    try:
        body = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"payload 不是合法 JSON: {e}"}, ensure_ascii=False))
        return

    req = urllib.request.Request(
        f"{API_URL}/datasets/{dataset_id}/documents/metadata",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = r.read().decode("utf-8")
            print(json.dumps({"ok": True, "status": r.status, "response": resp[:2000]}, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        print(json.dumps({"ok": False, "status": e.code, "error": e.read().decode("utf-8")[:2000]}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
