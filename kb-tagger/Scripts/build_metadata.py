#!/usr/bin/env python
"""构造 Dify 元数据打标 payload。

用法:
    python build_metadata.py <document_id> <version> <file_role> <doc_summary> <version_id> <file_role_id> <doc_summary_id>
输出: 标准 metadata_list JSON（partial_update=true）
"""
import json
import sys


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 7:
        print(json.dumps({"error": "用法: python build_metadata.py <document_id> <version> <file_role> <doc_summary> <version_id> <file_role_id> <doc_summary_id>"}, ensure_ascii=False))
        return
    document_id, version, file_role, doc_summary = args[0], args[1], args[2], args[3]
    version_id, file_role_id, doc_summary_id = args[4], args[5], args[6]

    body = {
        "operation_data": [
            {
                "document_id": document_id,
                "metadata_list": [
                    {"id": version_id, "name": "version", "value": version},
                    {"id": file_role_id, "name": "file_role", "value": file_role},
                    {"id": doc_summary_id, "name": "doc_summary", "value": doc_summary},
                ],
                "partial_update": True,
            }
        ]
    }
    print(json.dumps(body, ensure_ascii=False))


if __name__ == "__main__":
    main()
