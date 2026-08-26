#!/usr/bin/env python
"""构造 create-by-text 请求体：MinerU 清洗后的 markdown 文本 → Dify 建文档请求体。

用法:
    python create_by_text.py <文本文件路径> <文档名> [dataset_id]
输出: JSON {"request_body": "...json字符串"}；文本为空时输出 {"request_body": ""}（调用方直接跳过建文档）
检索配置（对照老库实测）：bge-m3(ollama) + hybrid 0.7/0.3 + qwen3-rerank + top_k 5 + 0.5，分段 \\n\\n/500/50。
"""
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def build_body(cleaned_text: str, filename: str) -> dict:
    return {
        "name": filename,
        "text": cleaned_text,
        "indexing_technique": "high_quality",
        "embedding_model": "bge-m3",
        "embedding_model_provider": "langgenius/ollama/ollama",
        "doc_language": "Chinese",
        "doc_form": "text_model",
        "process_rule": {
            "mode": "custom",
            "rules": {
                "pre_processing_rules": [
                    {"id": "remove_extra_spaces", "enabled": True},
                    {"id": "remove_urls_emails", "enabled": False},
                ],
                "segmentation": {
                    "separator": "\n\n",
                    "max_tokens": 500,
                    "chunk_overlap": 50,
                },
            },
        },
        "retrieval_model": {
            "search_method": "hybrid_search",
            "reranking_enable": True,
            "reranking_mode": "reranking_model",
            "reranking_model": {
                "reranking_provider_name": "langgenius/tongyi/tongyi",
                "reranking_model_name": "qwen3-rerank",
            },
            "top_k": 5,
            "score_threshold_enabled": True,
            "score_threshold": 0.5,
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


def main() -> None:
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python create_by_text.py <文本文件路径> <文档名> [dataset_id]"}, ensure_ascii=False))
        return
    path, filename = sys.argv[1], sys.argv[2]
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        print(json.dumps({"error": f"读取 {path} 失败: {e}"}, ensure_ascii=False))
        return
    if not text.strip():
        # 空文本守卫：返回空 body，调用方跳过建文档（否则 create-by-text 400 拖垮整次入库）
        print(json.dumps({"request_body": ""}, ensure_ascii=False))
        return
    body = build_body(text, filename)
    print(json.dumps({"request_body": json.dumps(body, ensure_ascii=False)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
