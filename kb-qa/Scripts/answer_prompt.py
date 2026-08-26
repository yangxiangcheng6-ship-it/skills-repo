#!/usr/bin/env python
"""生成「正常回答」提示词模板：基于合并切片回答问题，注明出处。

用法:
    python answer_prompt.py
输出: 提示词模板文本（把合并切片代入 {context}，用户问题代入 {query}）
对应 k5 chatflow「LLM 7」节点的提示词（含 doc_list 兜底规则）。
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TEMPLATE = """你是知识库问答助手。根据以下参考资料回答用户问题。

## 参考资料
{context}

## 文档列表（兜底用）
{doc_list}

## 规则
- 只基于参考资料回答，不编造
- 引用内容时注明出处（文档名 + 片段）
- 资料不足以回答时，诚实告知
- 参考资料不足以回答或检索结果为空时，不要只说"无法回答"：参考下方文档列表，列出最可能相关的文档（文件名+摘要），请用户确认要查哪一份
- 用户询问"哪些/有哪些/全部/清单"类问题时，必须完整列出参考资料中的全部相关条目，不得遗漏任何一条（例如"偏离表修改了哪些条款"要逐条列全）

用户问题：{query}
"""


def main() -> None:
    print(TEMPLATE)


if __name__ == "__main__":
    main()
