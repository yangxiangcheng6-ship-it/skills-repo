#!/usr/bin/env python
"""生成「澄清/报错」提示词模板：匹配不到文档 / 检索无结果 / 服务报错时使用。

用法:
    python clarify_prompt.py
输出: 提示词模板文本（把 doc_list 代入 {doc_list}，用户问题代入 {query}）
对应 k5 chatflow「LLM 5」节点的澄清兜底提示词。
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TEMPLATE = """系统无法确定用户的问题对应哪份文档，或本次没有检索到相关内容。

请向用户说明情况，并提问澄清需要补充什么信息（比如：标准版还是偏离版？具体指哪份文档？），从下方文档列表中挑出可能相关的文档，列成选项让用户选。

- 如果只是本次没搜到相关内容，请用户换个问法或补充更多细节，并列出可选文档
- 如果知识库服务报错：如实说明错误信息，请用户稍后重试，不要编造内容

## 文档列表
{doc_list}

用户问题：{query}
"""


def main() -> None:
    print(TEMPLATE)


if __name__ == "__main__":
    main()
