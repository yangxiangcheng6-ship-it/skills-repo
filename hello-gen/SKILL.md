---
name: hello-gen
description: 本技能用于在触发时运行 Python 脚本，输出包含当前日期时间的问候语 JSON 数据，主要用于端到端验证自动技能包生成系统的功能完整性。
---

# hello-gen 技能说明

## 执行流程

1. 运行命令 `python Scripts/hello.py`
2. 脚本将初始化标准输出编码为 UTF-8，以确保中文字符正常显示。
3. 脚本获取当前系统时间，并构造一个 JSON 对象。
4. 标准输出将打印该 JSON 字符串。

## 输出格式

成功时输出：
```json
{"ok": true, "now": "YYYY-MM-DD HH:MM:SS"}
```

异常时输出：
```json
{"error": "错误描述信息"}
```