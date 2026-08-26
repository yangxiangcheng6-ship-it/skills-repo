---
name: hello-gen
description: 本技能用于端到端验证自动技能包生成系统。当用户需要测试系统能否正确生成并运行包含标准库依赖、UTF-8 编码处理及结构化 JSON 输出的 Python 脚本时触发。主要用途是输出问候语和当前日期时间。
---

# 执行流程

1. 运行脚本 `python Scripts/hello.py`。
2. 脚本将初始化标准输出编码为 UTF-8，以确保证中文或特殊字符正确显示。
3. 脚本获取当前系统时间，格式化为 "YYYY-MM-DD HH:MM:SS"。
4. 脚本输出一个 JSON 对象到标准输出：
   - 成功时：`{"ok": true, "now": "YYYY-MM-DD HH:MM:SS"}`
   - 失败时：`{"error": "错误描述信息"}`
5. 用户或下游系统可解析该 JSON 以验证技能执行状态和时间戳。