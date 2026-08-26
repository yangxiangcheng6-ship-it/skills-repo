#!/usr/bin/env python
"""更新 MinIO 索引 _index.json：追加文件名（带 .md 后缀）并排序。

用法:
    python update_index.py <索引JSON文件> <version> <file_name>
索引文件 = minio_client.py 读出的 _index.json 内容（{"标准": [...], "偏离": [...]}），不存在时可传空文件路径。
输出: JSON {"index_json": "..."}  —— 用 minio_client.py put_object("_index.json", ...) 写回。
排序保证 chatflow 匹配平局（同分文件名）时的确定性。
"""
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main() -> None:
    if len(sys.argv) < 4:
        print(json.dumps({"error": "用法: python update_index.py <索引JSON文件> <version> <file_name>"}, ensure_ascii=False))
        return
    path, version, file_name = sys.argv[1], sys.argv[2], sys.argv[3]

    data = {"标准": [], "偏离": []}
    try:
        with open(path, encoding="utf-8") as f:
            parsed = json.load(f)
        if isinstance(parsed, dict):
            for k in data:
                if isinstance(parsed.get(k), list):
                    data[k] = [str(f) for f in parsed[k] if f]
    except Exception:
        pass  # 索引不存在或损坏：从空清单开始重建

    key = version if version in data else "标准"
    obj = (file_name or "").strip() + ".md"
    if obj != ".md" and obj not in data[key]:
        data[key].append(obj)
        data[key] = sorted(data[key])  # 排序保证匹配平局的确定性

    print(json.dumps({"index_json": json.dumps(data, ensure_ascii=False)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
