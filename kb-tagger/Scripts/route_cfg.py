#!/usr/bin/env python
"""KB 路由对照表：file_name + version -> dataset_id 与元数据字段 ID。

用法:
    python route_cfg.py <file_name> <version>
    version ∈ {标准, 偏离}; 扩展名 docx/xlsx; 未匹配默认 (标准, docx)
输出: JSON
"""
import json
import sys

CFG = {
    ("标准", "docx"): {
        "dataset_id": "67b0a079-38e2-4c60-83e6-933bba670695",
        "start_node_id": "1784856922229",
        "version_id": "f937afe4-afc6-4c80-aa6d-22d15209cd5a",
        "file_role_id": "c69557bf-e07d-4853-8dfe-fd9af0800f07",
        "doc_summary_id": "0005520c-35f2-4946-bac6-b2498fa86bf3",
    },
    ("标准", "xlsx"): {
        "dataset_id": "fa401e6b-144b-4962-b71e-9a5a69fa191e",
        "start_node_id": "1785293362919",
        "version_id": "bfebe1b2-5677-4c67-adb4-a926c44d72fc",
        "file_role_id": "df526ff1-915e-42ae-b5e8-b5e1cf18c7ab",
        "doc_summary_id": "1bbdae0e-d90d-4f88-8674-e4383bbb3770",
    },
    ("偏离", "docx"): {
        "dataset_id": "3e588f3f-9930-44b5-a060-740bdcf4db7c",
        "start_node_id": "1784856922229",
        "version_id": "5c475579-94fd-4c3f-b228-bad4e6fc2d9b",
        "file_role_id": "c19b814e-460c-4a3e-9690-66d603b24cf3",
        "doc_summary_id": "d24a8ff1-6af2-47cf-aca6-d2bf007434a1",
    },
    ("偏离", "xlsx"): {
        "dataset_id": "55ed6c00-acc2-441e-93f1-fd4f42ec1078",
        "start_node_id": "1785293362919",
        "version_id": "12aede26-32e2-4afa-a403-c1c3e40db227",
        "file_role_id": "b30a357b-5f83-4c56-b350-e2e0074c73f2",
        "doc_summary_id": "18720ea2-eb2d-492f-adbc-a8a956aa628b",
    },
}


def main() -> None:
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python route_cfg.py <file_name> <version>"}, ensure_ascii=False))
        return
    file_name = sys.argv[1]
    version = sys.argv[2]
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else "docx"
    key = (version, ext)
    cfg = CFG.get(key, CFG[("标准", "docx")])
    out = {
        "version": version,
        "ext": ext,
        "matched": key in CFG,
        **cfg,
    }
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
