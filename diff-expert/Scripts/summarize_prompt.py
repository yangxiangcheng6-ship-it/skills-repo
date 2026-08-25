#!/usr/bin/env python
"""差异提炼 prompt 模板：把 diff_docs.py 的差异块交给 LLM 提炼成结构化差异表。

用法:
    python summarize_prompt.py < diff_blocks.json

输出 LLM 系统提示词（可直接粘贴给模型使用），或:
    python summarize_prompt.py --file diff_blocks.json --compact
    # compact 模式把差异块内容也拼进 prompt（差异块小的时候用）

模板要求 LLM 输出:
    JSON 数组，每项 {条款, 变化类型, 标准版内容, 偏离版内容, 实质影响}
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TEMPLATE = """你是文档差异对比专家。下面是同一份协议（或附件）「标准版」与「偏离版」的差异块数据，
请把它们提炼成结构化的差异表。

## 硬规则

1. 只输出 JSON 数组，不要任何其他文字、解释或 markdown 代码块标记。
2. 每一项格式: {{"条款": "...", "变化类型": "修改|删除|新增", "标准版内容": "...", "偏离版内容": "...", "实质影响": "..."}}
   - 修改: 标准版与偏离版同一位置内容不同
   - 删除: 标准版有、偏离版没有
   - 新增: 标准版没有、偏离版有
3. 「条款」写差异所在的具体条款号或章节名（如 "第 7.2 条"、"价格表 B 行"），找不到就写 "无明确条款号"。
4. 忽略纯格式/噪声差异，不要报：
   - 版本戳、水印（如 VOLVO）、页脚、脚注编号、空白/换行差异
   - 仅有日期或标题编号变化的整段内容（如整段只是版本号不同）
   - 文档清洗元信息头（如 "- 原始字符数：…"、"- 步骤字符数：…"、"- 去除重复分块" 等清洗统计行）
   - 双语版本里同一段英文相同、仅中文翻译措辞差异且含义一致的（若中文含义实质不同则报）
5. 合并相邻的同类差异为一条，不要碎片化重复。
6. 「实质影响」用一句话说清楚这个差异意味着什么（谁吃亏、义务变重还是变轻、范围扩大缩小）。
7. 最多报 20 条；差异少于 3 条时，如实输出少的条数，不要凑数。

## 差异数据

{data_json}

现在输出 JSON 数组。
"""


def build(data: dict, compact: bool = False) -> str:
    if compact:
        payload = json.dumps(data, ensure_ascii=False, indent=1)
    else:
        payload = json.dumps({
            "stats": data.get("stats"),
            "blocks_count": len(data.get("blocks", [])),
            "提示": "差异块数量多时，分批次把每个块的 standard_lines/deviation_lines 内容传入后再提炼。",
        }, ensure_ascii=False, indent=1)
    return TEMPLATE.format(data_json=payload)


def main() -> None:
    path = None
    compact = False
    for a in sys.argv[1:]:
        if a == "--compact":
            compact = True
        elif a == "--file":
            path = sys.argv[sys.argv.index(a) + 1]
        elif not a.startswith("-"):
            path = a

    if path:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    if compact:
        # 差异块少（≤10 块）时全量拼接
        print(build(data, compact=True))
    else:
        print(build(data, compact=False))
        if not compact:
            print("\n# 注: 块数 <= 10 时建议加 --compact 全量拼接；否则分批喂给 LLM。",
                  file=sys.stderr)


if __name__ == "__main__":
    main()
