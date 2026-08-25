#!/usr/bin/env python
"""校验打标结果：file_role 7 类内、doc_summary ≤15 字、version ∈ {标准,偏离}。

用法:
    python validate_tags.py --file_role <角色> --doc_summary <概括> --version <版本>
退出码: 0=通过, 1=失败; 输出校验报告 JSON
"""
import json
import sys

FILE_ROLES = ["主协议", "通用条款", "数据保护附件", "信息安全附件", "合规附件", "变更协议", "商务附件"]
VERSIONS = ["标准", "偏离"]


def main() -> None:
    args = sys.argv[1:]
    kv: dict[str, str] = {}
    i = 0
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            kv[args[i][2:]] = args[i + 1]
            i += 2
        else:
            i += 1

    checks: list[dict] = []
    ok = True

    file_role = kv.get("file_role", "")
    if file_role not in FILE_ROLES:
        ok = False
        checks.append({"field": "file_role", "ok": False, "detail": f"{file_role!r} 不在 7 类内: {FILE_ROLES}"})
    else:
        checks.append({"field": "file_role", "ok": True})

    doc_summary = kv.get("doc_summary", "")
    if len(doc_summary) > 15:
        ok = False
        checks.append({"field": "doc_summary", "ok": False, "detail": f"长度 {len(doc_summary)} 超过 15 字"})
    elif not doc_summary:
        ok = False
        checks.append({"field": "doc_summary", "ok": False, "detail": "为空"})
    else:
        checks.append({"field": "doc_summary", "ok": True, "detail": f"长度 {len(doc_summary)}"})

    version = kv.get("version", "")
    if version not in VERSIONS:
        ok = False
        checks.append({"field": "version", "ok": False, "detail": f"{version!r} 不在 {VERSIONS}"})
    else:
        checks.append({"field": "version", "ok": True})

    print(json.dumps({"ok": ok, "checks": checks}, ensure_ascii=False))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
