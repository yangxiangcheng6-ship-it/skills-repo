#!/usr/bin/env python
"""输出 file_role 7 分类法提示词模板（供 LLM 判断用）。

用法:
    python tag_prompt.py
输出: 提示词文本（含 {version} 占位符，使用时替换为实际版本）
"""
import sys

PROMPT = """你是一个法律/商务文档分类专家。下面是从一份文档中检索出的内容片段。请通读这些片段，判断文档的 file_role 和 doc_summary。

注意：已知这份文档的 version 是"{version}"，不需要再判断。

## 输出格式（纯JSON，不要markdown包裹）

{{
  "file_role": "角色分类",
  "doc_summary": "一句话概括"
}}

## file_role（7选1）
- "主协议"：框架合同、Master Agreement，统领全局
- "通用条款"：IT采购的标准法律条款、General Terms
- "数据保护附件"：DPA、数据处理协议、委托处理协议
- "信息安全附件"：IT安全最低要求、信息安全标准
- "合规附件"：行为准则、Code of Conduct
- "变更协议"：对标准条款的偏离/变更/修改申请表
- "商务附件"：报价单、价目表、价格清单

## doc_summary
读完内容后，用15字以内概括。例如：
- "IT采购通用条款与条件"
- "委托处理个人数据协议"
- "供应商信息安全最低要求"

只输出JSON，不要解释。
"""


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "{version}"
    print(PROMPT.format(version=version))


if __name__ == "__main__":
    main()
