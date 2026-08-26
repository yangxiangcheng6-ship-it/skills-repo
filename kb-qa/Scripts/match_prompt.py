#!/usr/bin/env python
"""生成「文档匹配」提示词模板：从 doc_list 匹配用户问题 → 结构化 results[]。

用法:
    python match_prompt.py
输出: 提示词模板文本（把 doc_list 和用户问题代入 {doc_list} / {query} 后交给 LLM）
对应 k5 chatflow「LLM 4」节点的提示词与结构化输出 schema。
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TEMPLATE = """文档列表格式：[KB名] doc_type值 | 摘要 | 文件名

任务：从文档列表中找到与用户查询最相关的文档（可能多个），为每个相关文档确定 doc_type/version 并重写检索词，放入 results 数组。

规则：
- 候选 doc_type 只是提示：列表中有对应行就用它，没有或与用户查询明显冲突时，按用户查询意图选最相关的行
- version 一律以匹配行所在 KB 名为准（"标准"开头→"标准"，"偏离"开头→"偏离"），忽略候选 version，不要因为候选 version 与 KB 名不一致就输出空
- query：结合用户查询和对话历史，为每个相关文档重写一个 5~15 字的纯检索词（涉及多个文档/主题时每个一组）（去掉"标准/偏离/哪个版本"等筛选词，保留内容关键词）
- 只有列表里确实没有任何相关文档时，才输出 {"results": []}
- doc_type 只输出文档列表里出现的值，不要把整行抄下来
- 对比类问题（"一样吗""对比""和…比"）：query 只保留双方共同的核心词（如"付款期限"），禁止拼入"标准/偏离/版本"等筛选词
- query 禁止输出"通用条款""主协议""框架协议""数据保护""信息安全""合规制度""报价模板""价格清单"等文档类型词本身——它们是文档分类不是检索主题，用了会检索不到具体条款（反例：query="通用条款"是错的，query="付款期限"才对）
- 对比类问题：所有组必须输出相同的核心主题词（如两组都输出"付款期限"），禁止一组输出文档类型词而另一组输出主题词
- 询问"文件组成/附件清单/有哪些文件"类：doc_type 选被询问的文档本身（如问框架协议的组成 → doc_type=框架协议，不要选附件对应的文档类型）
- 询问具体条款时，query 优先用原文标题词（如"合同文件""服务费用和付款""验收测试"）

文档列表：
{doc_list}

用户查询：{query}

输出 JSON（严格按 schema）：
{{
  "results": [
    {{"doc_type": "文档列表里出现的值", "version": "标准|偏离", "query": "5~15字纯检索词"}}
  ]
}}
"""


def main() -> None:
    print(TEMPLATE)


if __name__ == "__main__":
    main()
