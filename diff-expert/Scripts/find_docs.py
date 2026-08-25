#!/usr/bin/env python
"""定位文档：按 topic 在索引里匹配标准版 / 偏离版文档。

用法:
    python find_docs.py "<topic>"

topic 例: "Appendix A" / "主协议" / "数据处理协议" / "行为准则" / "报价单"
输出 JSON:
    {"topic": ..., "matched": true,
     "standard": {"version": "标准", "filename": "..."},
     "deviation": {"version": "偏离", "filename": "..."},
     "alternatives": [...], "hint": "..."}
"""
import json
import sys
from difflib import SequenceMatcher

from minio_client import list_index

# 成对映射：topic → (标准版文件名, 偏离版文件名)。
# 用于文件名不相似但语义同源的一对文档（如 主协议 Master ↔ Framework），模糊匹配分不出来。
PAIR_ALIASES = {
    "主协议": ("Master Agreement of 汽车合同中台项目 for IT Purchasing.docx.md",
               "Framework Agreement of TECH Platfrom Project.docx.md"),
    "框架协议": ("Master Agreement of 汽车合同中台项目 for IT Purchasing.docx.md",
                 "Framework Agreement of TECH Platfrom Project.docx.md"),
    "tech平台框架协议": ("Master Agreement of 汽车合同中台项目 for IT Purchasing.docx.md",
                        "Framework Agreement of TECH Platfrom Project.docx.md"),
}

# 已知的主题别名映射（英文全名 → 用户常用叫法），补充模糊匹配
ALIASES = {
    "appendix a": "Appendix A",
    "总条款": "Appendix A",
    "it采购总条款": "Appendix A",
    "master agreement": "Master Agreement",
    "主协议": "Master Agreement",
    "框架协议": "Framework Agreement",
    "tcc": "Framework Agreement",
    "tech平台": "Framework Agreement",
    "dpa": "Appendix C",
    "数据处理协议": "Appendix C",
    "委托处理": "Appendix C",
    "数据修改协议": "Appendix C",
    "quotation": "Appendix D",
    "报价": "Appendix D",
    "报价单": "Appendix E",
    "price list": "Appendix E",
    "价格表": "Appendix E",
    "code of conduct": "Appendix F",
    "行为准则": "Appendix F",
    "conduct": "Appendix F",
    "deviation form": "Appendix A1",
    "偏离表": "Appendix A1",
    "信息安全": "Appendix B",
    "it security": "Appendix B",
}


def normalize(s: str) -> str:
    return " ".join(s.lower().split())


def score(topic: str, filename: str) -> float:
    """文件名匹配分：0~1。包含关系给高分，模糊匹配兜底"""
    t, f = normalize(topic), normalize(filename)
    if t and t in f:
        return 1.0
    if f and f in t:
        return 0.9
    return SequenceMatcher(None, t, f).ratio()


def match(topic: str, files: list[str]) -> list[tuple[float, str]]:
    scored = [(score(topic, f), f) for f in files]
    scored.sort(key=lambda x: -x[0])
    return scored


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "用法: python find_docs.py \"<topic>\""}, ensure_ascii=False))
        sys.exit(1)
    topic = sys.argv[1]

    idx = list_index()
    if idx is None:
        print(json.dumps({"error": "无法读取 MinIO 索引"}, ensure_ascii=False))
        sys.exit(1)

    # 1) 成对映射优先（文件名不相似的已知配对）
    pair = PAIR_ALIASES.get(normalize(topic))
    if pair:
        std_name, dev_name = pair
        result = {
            "topic": topic,
            "mapped_topic": "PAIR_ALIASES",
            "matched": True,
            "standard": {"version": "标准", "filename": std_name, "score": 1.0},
            "deviation": {"version": "偏离", "filename": dev_name, "score": 1.0},
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 2) 别名映射 → 模糊匹配
    mapped = ALIASES.get(normalize(topic), topic)

    std_scores = match(mapped, idx.get("标准", []))
    dev_scores = match(mapped, idx.get("偏离", []))

    best_std = std_scores[0] if std_scores else (0.0, None)
    best_dev = dev_scores[0] if dev_scores else (0.0, None)

    result = {
        "topic": topic,
        "mapped_topic": mapped,
        "matched": best_std[0] >= 0.6 and best_dev[0] >= 0.6,
        "standard": {"version": "标准", "filename": best_std[1], "score": round(best_std[0], 2)},
        "deviation": {"version": "偏离", "filename": best_dev[1], "score": round(best_dev[0], 2)},
        "alternatives": {
            "标准": [f for s, f in std_scores[:3]],
            "偏离": [f for s, f in dev_scores[:3]],
        },
    }
    if not result["matched"]:
        result["hint"] = (f"topic「{topic}」在标准/偏离两侧都匹配到文件才算定位成功；"
                          f"当前标准侧「{best_std[1]}」{best_std[0]:.2f} 分、"
                          f"偏离侧「{best_dev[1]}」{best_dev[0]:.2f} 分，"
                          f"低于 0.6 阈值，需要换说法或从 alternatives 里挑一个。")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
