#!/usr/bin/env python
"""Dify 知识库检索：query + 可选 version/doc_type metadata 过滤，hybrid + rerank。

用法:
    python retrieve.py "<query>" [--version 标准|偏离] [--doc_type 主协议] [--top_k 8]
输出: JSON {"results": [{"content": str, "document_name": str, "score": float, "dataset_name": str}]}
环境变量可覆盖: DIFY_API_URL  DIFY_API_KEY
"""
import argparse
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

API_URL = os.environ.get("DIFY_API_URL", "http://127.0.0.1/v1")
API_KEY = os.environ.get("DIFY_API_KEY", "dataset-Kz491fr3x8jSWR8QEC8BYG3Z")

# KB 配置（2026-08-17 起表格并入 docx 库；字段 ID 与智能入库 (22) 路由表一致）
DATASETS = {
    "标准": "67b0a079-38e2-4c60-83e6-933bba670695",
    "偏离": "3e588f3f-9930-44b5-a060-740bdcf4db7c",
}
METADATA_IDS = {
    "标准": {"version": "f937afe4-afc6-4c80-aa6d-22d15209cd5a", "doc_type": "c6d05c1e-f4bf-42c1-8e8d-fad5528bfdf9"},
    "偏离": {"version": "5c475579-94fd-4c3f-b228-bad4e6fc2d9b", "doc_type": "cc1c88f9-f8a8-4ec7-b7c2-e2448d9f272f"},
}


def retrieve(query: str, version: str | None = None, doc_type: str | None = None, top_k: int = 8) -> dict:
    if version and version not in DATASETS:
        return {"error": f"未知版本：{version}（可选 标准/偏离）"}
    targets = [(v, ds) for v, ds in DATASETS.items() if not version or v == version]
    if doc_type and not version:
        return {"error": "--doc_type 需要配合 --version 使用（先锁定版本再按文档类型过滤）"}

    body = {
        "query": query,
        "retrieval_model": {
            "search_method": "hybrid_search",
            "score_threshold_enabled": False,
            "reranking_enable": True,
            "reranking_mode": "reranking_model",
            "reranking_model": {
                "reranking_provider_name": "langgenius/tongyi/tongyi",
                "reranking_model_name": "qwen3-rerank",
            },
            "top_k": top_k,
            "weights": {
                "vector_setting": {
                    "vector_weight": 0.7,
                    "embedding_model_name": "bge-m3",
                    "embedding_provider_name": "langgenius/ollama/ollama",
                },
                "keyword_setting": {"keyword_weight": 0.3},
            },
        },
    }
    if version:
        body["metadata_filtering_mode"] = "manual"
        conds = [{
            "metadata_id": METADATA_IDS[version]["version"],
            "name": "version",
            "comparison_operator": "is",
            "value": version,
        }]
        if doc_type:
            conds.append({
                "metadata_id": METADATA_IDS[version]["doc_type"],
                "name": "doc_type",
                "comparison_operator": "is",
                "value": doc_type,
            })
        body["metadata_filtering_conditions"] = {"conditions": conds, "logical_operator": "and"}

    all_results = []
    for v, ds_id in targets:
        url = f"{API_URL}/datasets/{ds_id}/retrieve"
        req = urllib.request.Request(
            url,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"error": f"检索 {v} 库失败: HTTP {e.code} {e.read().decode()[:200]}"}
        except Exception as e:
            return {"error": f"检索 {v} 库失败: {e}"}
        for rec in data.get("records", []):
            # 响应结构：records[] 每项 = {"segment": {...}, "score": ...}（segment 是单数对象）
            seg = rec.get("segment") or {}
            content = seg.get("content", "")
            if not content:
                continue
            all_results.append({
                "content": content,
                "document_name": (seg.get("document") or {}).get("name", "") or seg.get("document_name", ""),
                "dataset_name": v,
                "score": rec.get("score"),
            })
    return {"results": all_results}


def main() -> None:
    ap = argparse.ArgumentParser(description="Dify 知识库检索（hybrid + rerank）")
    ap.add_argument("query", help="检索词（5~15 字，纯内容关键词）")
    ap.add_argument("--version", choices=["标准", "偏离"], help="只检索该版本库（metadata 过滤）")
    ap.add_argument("--doc_type", help="文档类型过滤（需配合 --version）")
    ap.add_argument("--top_k", type=int, default=8)
    args = ap.parse_args()
    print(json.dumps(retrieve(args.query, args.version, args.doc_type, args.top_k), ensure_ascii=False))


if __name__ == "__main__":
    main()
