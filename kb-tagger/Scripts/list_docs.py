#!/usr/bin/env python
"""按文件名查知识库文档，获取 document_id（打标前置步骤）。

用法:
    python list_docs.py <version> <file_name>
    version ∈ {标准, 偏离}
输出: JSON {"matched": bool, "document_id": str, "document_name": str,
            "candidates": [{"document_id", "name"}]}
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

# 与 route_cfg.py 同源
DATASETS = {
    "标准": "67b0a079-38e2-4c60-83e6-933bba670695",
    "偏离": "3e588f3f-9930-44b5-a060-740bdcf4db7c",
}


def fetch_docs(dataset_id: str) -> list[dict]:
    req = urllib.request.Request(
        f"{API_URL}/datasets/{dataset_id}/documents?limit=100",
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data.get("data", []) or data.get("documents", [])


def normalize(name: str) -> str:
    return str(name or "").strip().lower().replace("\\", "/").rsplit("/", 1)[-1]


def main() -> None:
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python list_docs.py <version> <file_name>"}, ensure_ascii=False))
        return
    version, file_name = sys.argv[1], sys.argv[2]
    ds_id = DATASETS.get(version)
    if not ds_id:
        print(json.dumps({"error": f"未知版本：{version}（可选 标准/偏离）"}, ensure_ascii=False))
        return
    target = normalize(file_name)
    try:
        docs = fetch_docs(ds_id)
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": f"拉取文档清单失败: HTTP {e.code}"}, ensure_ascii=False))
        return
    except Exception as e:
        print(json.dumps({"error": f"拉取文档清单失败: {e}"}, ensure_ascii=False))
        return

    candidates = [{"document_id": d.get("id"), "name": d.get("name", "")} for d in docs]
    exact = [c for c in candidates if normalize(c["name"]) == target]
    partial = [c for c in candidates if target and target in normalize(c["name"])]
    if exact:
        hit = exact[0]
        print(json.dumps({"matched": True, "document_id": hit["document_id"], "document_name": hit["name"],
                          "candidates": candidates}, ensure_ascii=False))
        return
    if partial:
        hit = partial[0]
        print(json.dumps({"matched": True, "document_id": hit["document_id"], "document_name": hit["name"],
                          "matched_by": "partial", "candidates": candidates}, ensure_ascii=False))
        return
    print(json.dumps({"matched": False, "document_id": None, "document_name": None,
                      "candidates": candidates,
                      "hint": f"在{version}库未找到文件名包含「{file_name}」的文档，请确认文件名或文档是否已入库"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
