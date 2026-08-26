#!/usr/bin/env python
"""合并多个检索结果文件：去重、按文档分组标注、每块截 6000 字。

用法:
    python merge_chunks.py <检索结果文件1> [<检索结果文件2> ...]
每个文件是 retrieve.py 的输出（{"results": [...]}）。输出合并后的文本。
"""
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "用法: python merge_chunks.py <检索结果文件1> [...]"}, ensure_ascii=False))
        return
    seen = set()
    parts = []
    for path in sys.argv[1:]:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(json.dumps({"error": f"读取 {path} 失败: {e}"}, ensure_ascii=False))
            return
        if "results" not in data:
            print(json.dumps({"error": f"{path} 不是有效检索结果（缺 results 字段）: {data.get('error', '')}"}, ensure_ascii=False))
            return
        for r in data["results"]:
            content = (r.get("content") or "").strip()
            if not content or content in seen:
                continue
            seen.add(content)
            db = (r.get("dataset_name") or "").strip()
            doc = (r.get("document_name") or "").strip()
            label = f"{db} | {doc}".strip(" |")
            parts.append(f"【{label}】\n{content[:6000]}")
    merged = "\n\n".join(parts)
    print(json.dumps({"merged": merged, "chunk_count": len(parts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
