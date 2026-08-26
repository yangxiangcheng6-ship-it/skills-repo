#!/usr/bin/env python
"""从 create-by-text 建文档接口的响应中提取 document_id。

用法:
    python extract_doc_id.py <响应JSON文件或JSON字符串>
输出: JSON {"document_id": "..."} 或 {"document_id": ""}
兼容三种响应形态：document.id / documents[0].id / data[0].id。
"""
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "用法: python extract_doc_id.py <响应JSON文件或JSON字符串>"}, ensure_ascii=False))
        return
    raw = sys.argv[1]
    r = None
    if raw.lstrip().startswith("{"):
        try:
            r = json.loads(raw)
        except Exception:
            r = None
    if r is None:
        try:
            with open(raw, encoding="utf-8") as f:
                r = json.load(f)
        except Exception as e:
            print(json.dumps({"error": f"解析响应失败: {e}"}, ensure_ascii=False))
            return
    doc_id = ""
    if "document" in r and isinstance(r["document"], dict):
        doc_id = r["document"].get("id", "")
    elif "documents" in r and isinstance(r["documents"], list) and r["documents"]:
        doc_id = r["documents"][0].get("id", "")
    elif "data" in r and isinstance(r["data"], list) and r["data"]:
        doc_id = r["data"][0].get("id", "")
    print(json.dumps({"document_id": doc_id}, ensure_ascii=False))


if __name__ == "__main__":
    main()
