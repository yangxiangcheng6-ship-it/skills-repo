#!/usr/bin/env python
"""构造 MinerU 库打标 payload：document_id + version/file_role/doc_summary/doc_type 四字段。

用法:
    python build_metadata.py <llm输出JSON文件> <document_id> <version> <mineru_version_id> <mineru_file_role_id> <mineru_doc_summary_id> <mineru_doc_type_id>
llm输出 = 智能打标 LLM 的结果（{"file_role": "...", "doc_summary": "...", "doc_type": "..."}，可带 ```json 围栏）。
document_id 为空时输出合法空 payload（{"operation_data": []}），打标接口空操作返回，不报错。
输出: JSON {"metadata_body": "...json字符串"}
"""
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 7:
        print(json.dumps({"error": "用法: python build_metadata.py <llm输出文件> <document_id> <version> <ver_id> <role_id> <sum_id> <type_id>"}, ensure_ascii=False))
        return
    llm_path, document_id, version = args[0], args[1], args[2]
    v_id, r_id, s_id, t_id = args[3], args[4], args[5], args[6]

    try:
        with open(llm_path, encoding="utf-8") as f:
            text = f.read().strip()
    except Exception as e:
        print(json.dumps({"error": f"读取 {llm_path} 失败: {e}"}, ensure_ascii=False))
        return

    parsed = {}
    try:
        for sep in ["```json", "```"]:
            if sep in text:
                text = text.split(sep)[1].split("```")[0].strip()
        parsed = json.loads(text)
    except Exception:
        parsed = {}

    if not document_id:
        # 跳过了 MinerU 链（如 xlsx）：发合法空 payload，打标接口直接空操作返回
        print(json.dumps({"metadata_body": json.dumps({"operation_data": []}, ensure_ascii=False)}, ensure_ascii=False))
        return

    body = {
        "operation_data": [{
            "document_id": document_id,
            "metadata_list": [
                {"id": v_id, "name": "version", "value": version},
                {"id": r_id, "name": "file_role", "value": parsed.get("file_role", "通用条款")},
                {"id": s_id, "name": "doc_summary", "value": parsed.get("doc_summary", "")},
                {"id": t_id, "name": "doc_type", "value": parsed.get("doc_type", "")},
            ],
            "partial_update": True,
        }]
    }
    print(json.dumps({"metadata_body": json.dumps(body, ensure_ascii=False)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
