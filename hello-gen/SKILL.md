---
name: hello-gen
description: 本技能用于在需要验证系统端到端连通性时触发。运行后输出包含当前日期时间的JSON问候语，适用于自动化测试或环境检查场景。
---

# hello-gen 技能说明

## 执行流程

1. 运行脚本 `python Scripts/hello.py`
2. 脚本将输出一个 JSON 对象，格式如下：
   ```json
   {"ok": true, "now": "YYYY-MM-DD HH:MM:SS"}
   ```
3. 如果执行过程中发生错误，将返回包含错误信息的 JSON 对象：
   ```json
   {"error": "错误描述信息"}
   ```

## 注意事项

- 该脚本仅依赖 Python 标准库，无需安装任何第三方包。
- 输出内容已配置为 UTF-8 编码，确保中文环境下的兼容性。