# 技能包需求

## 技能名
hello-gen

## 功能
一个演示技能：运行脚本输出问候语和当前日期时间。用于端到端验证自动技能包生成系统。

## 具体要求
- SKILL.md：frontmatter 必须含 name（hello-gen）和 description（中文描述：本技能的触发条件和用途）
- 正文按"执行流程"组织：第 1 步运行 `python Scripts/hello.py`，说明输出格式
- 脚本 Scripts/hello.py：
  - 只用 Python 标准库（json/os/sys/datetime），禁止第三方库
  - main 函数开头必须 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`
  - 输出 JSON：{"ok": true, "now": "YYYY-MM-DD HH:MM:SS"}
  - 异常时返回结构化 {"error": ...}，禁止裸崩溃
  - 关键注释用中文
- 不需要 Reference 文件，不涉及外部服务调用
- 路径只允许 Scripts/ 前缀，禁止 ../ 和绝对路径
