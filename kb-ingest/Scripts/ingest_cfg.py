#!/usr/bin/env python
"""入库路由配置：version -> 老库（管道入库）+ MinerU 库（create-by-text 入库）的 dataset_id 与字段 ID。

用法:
    python ingest_cfg.py <version>   # version ∈ {标准, 偏离}
输出: JSON（含 dataset_id / start_node_id / 各字段 ID / mineru_* 字段 ID）
"""
import json
import sys

CFG = {
    "标准": {
        # --- 老库（管道入库）---
        "dataset_id": "67b0a079-38e2-4c60-83e6-933bba670695",
        "start_node_id": "1784856922229",
        "version_id": "f937afe4-afc6-4c80-aa6d-22d15209cd5a",
        "file_role_id": "c69557bf-e07d-4853-8dfe-fd9af0800f07",
        "doc_summary_id": "0005520c-35f2-4946-bac6-b2498fa86bf3",
        "doc_type_id": "c6d05c1e-f4bf-42c1-8e8d-fad5528bfdf9",
        # --- MinerU 库（create-by-text 入库）---
        "mineru_dataset_id": "eafbbd6f-463f-4376-af2d-795a86fb8de6",
        "mineru_version_id": "4326d10e-56a8-4633-b8fc-7ff3d47d5deb",
        "mineru_file_role_id": "1a4a6392-f924-4773-97e4-3babf0d661b3",
        "mineru_doc_summary_id": "0cfce0c0-e4b4-41e6-ab91-c47a165f7b65",
        "mineru_doc_type_id": "91d4c63a-b4b9-4e47-8396-92982aae9821",
    },
    "偏离": {
        # --- 老库（管道入库）---
        "dataset_id": "3e588f3f-9930-44b5-a060-740bdcf4db7c",
        "start_node_id": "1784856922229",
        "version_id": "5c475579-94fd-4c3f-b228-bad4e6fc2d9b",
        "file_role_id": "c19b814e-460c-4a3e-9690-66d603b24cf3",
        "doc_summary_id": "d24a8ff1-6af2-47cf-aca6-d2bf007434a1",
        "doc_type_id": "cc1c88f9-f8a8-4ec7-b7c2-e2448d9f272f",
        # --- MinerU 库（create-by-text 入库）---
        "mineru_dataset_id": "ec6da867-2ae5-4d6e-b4b8-f92aeaf1395c",
        "mineru_version_id": "0f73f782-b95a-451f-a047-8adaad295ffd",
        "mineru_file_role_id": "c90f80f2-218b-424f-b323-00491905ff93",
        "mineru_doc_summary_id": "25e87c7d-513a-4d08-a9ae-efac8c31b245",
        "mineru_doc_type_id": "d9c4b285-46a6-4bad-83b3-ed5e22111a71",
    },
}


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "用法: python ingest_cfg.py <version>（标准/偏离）"}, ensure_ascii=False))
        return
    version = sys.argv[1]
    cfg = CFG.get(version)
    if cfg is None:
        print(json.dumps({"error": f"未知版本：{version}（可选 标准/偏离）"}, ensure_ascii=False))
        return
    print(json.dumps({"version": version, **cfg}, ensure_ascii=False))


if __name__ == "__main__":
    main()
