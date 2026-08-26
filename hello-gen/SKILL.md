---
name: hello-gen
description: 本技能用于在触发时生成包含当前日期时间的问候语，主要用于端到端验证自动技能包生成系统的功能完整性。
---

# 执行流程

1. 运行脚本 `python Scripts/hello.py`
2. 脚本将输出一个 JSON 对象，格式为 `{"ok": true, "now": "YYYY-MM-DD HH:MM:SS"}`。
3. 如果执行过程中发生错误，将返回结构化错误信息 `{"error": "错误描述"}`。