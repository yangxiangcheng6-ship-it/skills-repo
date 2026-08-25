#!/usr/bin/env python
"""分块对比两份文档（标准 vs 偏离），输出差异块 JSON。

用法:
    python diff_docs.py "<标准版文件名>" "<偏离版文件名>" [--max-block 40]

从 MinIO 读文档内容，difflib 按行对比，忽略纯空白差异（行尾/连续空格/空行），
超长差异块自动截断并标记 truncated，供 LLM 提炼时注意。

输出 JSON:
    {"standard": {...}, "deviation": {...},
     "stats": {"diff_blocks": n, "diff_lines_std": x, "diff_lines_dev": y},
     "blocks": [{"type": "replace|delete|insert", "start_std": int, "start_dev": int,
                 "standard_lines": [...], "deviation_lines": [...], "truncated": false}]}
"""
import difflib
import json
import sys
from pathlib import Path

from minio_client import get_doc

BATCH = 800      # 分批对比的行数（SequenceMatcher 内存保护）
MAX_BLOCK = 40   # 单个差异块最多输出行数，超出截断


def normalize_lines(text: str) -> list[str]:
    """按行拆分 + 归一化空白（保留原始行内容用于展示）"""
    lines = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue  # 跳过空行，避免空行差异误报
        lines.append(stripped)
    return lines


def batch_diff(a: list[str], b: list[str]) -> list[dict]:
    """分批做 SequenceMatcher，合并边界处断开的差异块"""
    blocks = []
    for start in range(0, max(len(a), len(b)), BATCH):
        a_part = a[start:start + BATCH]
        b_part = b[start:start + BATCH]
        matcher = difflib.SequenceMatcher(None, a_part, b_part, autojunk=False)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            blocks.append({
                "type": tag,
                "start_std": start + i1,
                "start_dev": start + j1,
                "end_std": start + i2,
                "end_dev": start + j2,
                "standard_lines": a_part[i1:i2],
                "deviation_lines": b_part[j1:j2],
            })
    return blocks


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    max_block = MAX_BLOCK
    for i, a in enumerate(sys.argv[1:]):
        if a.startswith("--max-block") and i + 2 <= len(sys.argv):
            max_block = int(sys.argv[i + 2])

    if len(args) < 2:
        print(json.dumps({"error": "用法: python diff_docs.py \"<标准版文件名>\" \"<偏离版文件名>\""},
                         ensure_ascii=False))
        sys.exit(1)
    std_name, dev_name = args[0], args[1]

    std_text = get_doc("标准", std_name)
    dev_text = get_doc("偏离", dev_name)
    if std_text is None or dev_text is None:
        print(json.dumps({"error": "读取文档失败（检查文件名与 MinIO 索引一致）"}, ensure_ascii=False))
        sys.exit(1)

    a = normalize_lines(std_text)
    b = normalize_lines(dev_text)
    raw_blocks = batch_diff(a, b)

    # 合并相邻块 + 截断超长块
    blocks = []
    for blk in raw_blocks:
        if blocks and blk["start_std"] == blocks[-1]["end_std"] and \
                blk["start_dev"] == blocks[-1]["end_dev"]:
            # 相邻同型块合并
            blocks[-1]["standard_lines"].extend(blk["standard_lines"])
            blocks[-1]["deviation_lines"].extend(blk["deviation_lines"])
            blocks[-1]["end_std"] = blk["end_std"]
            blocks[-1]["end_dev"] = blk["end_dev"]
        else:
            blocks.append(blk)

    for blk in blocks:
        if len(blk["standard_lines"]) + len(blk["deviation_lines"]) > max_block:
            blk["truncated"] = True
            blk["standard_lines"] = blk["standard_lines"][:max_block // 2]
            blk["deviation_lines"] = blk["deviation_lines"][:max_block // 2]
        else:
            blk["truncated"] = False

    stats = {
        "std_lines": len(a),
        "dev_lines": len(b),
        "diff_blocks": len(blocks),
        "diff_lines_std": sum(len(x["standard_lines"]) for x in blocks),
        "diff_lines_dev": sum(len(x["deviation_lines"]) for x in blocks),
    }

    print(json.dumps({
        "standard": {"version": "标准", "filename": std_name},
        "deviation": {"version": "偏离", "filename": dev_name},
        "stats": stats,
        "blocks": blocks,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
