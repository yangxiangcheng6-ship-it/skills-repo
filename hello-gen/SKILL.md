---
name: hello-gen
description: 本技能用于端到端验证自动技能包生成系统。当用户需要测试脚本执行环境、标准库兼容性或获取当前服务器时间时触发。
---

# hello-gen 技能说明

## 执行流程

1. **运行脚本**：执行 `python Scripts/hello.py`
2. **预期输出**：脚本将返回一个 JSON 对象，包含状态标志和当前日期时间。
   - 成功格式：`{"ok": true, "now": "YYYY-MM-DD HH:MM:SS"}`
   - 失败格式：`{\"error\": \"错误描述信息\"}`\n\n## 注意事项\n- 该脚本仅依赖 Python 标准库，无需安装任何第三方包。\n- 输出已强制配置为 UTF-8 编码，确保中文环境下的兼容性。",
  "scripts": [
    {
      "path": "Scripts/hello.py",
      "content": "import sys\nimport json\nfrom datetime import datetime\n\n# 关键配置：确保标准输出使用 UTF-8 编码，避免在某些终端环境下出现乱码\nsys.stdout.reconfigure(encoding=\"utf-8\", errors=\"replace\")\n\ndef main():\n    \"\"\"\n    主函数：生成问候语和当前时间，并以 JSON 格式输出。\n    异常情况下返回结构化错误信息，禁止裸崩溃。\n    \"\"\"\n    try:\n        # 获取当前日期时间，格式化为 YYYY-MM-DD HH:MM:SS\n        now_str = datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")\n        \n        # 构建成功响应对象\n        result = {\n            \"ok\": True,\n            \"now\": now_str\n        }\n        \n        # 输出 JSON 字符串，ensure_ascii=False 允许直接输出非 ASCII 字符（虽然此处主要是数字和符号）\n        print(json.dumps(result, ensure_ascii=False))\n        \n    except Exception as e:\n        # 捕获所有异常并返回结构化错误信息\n        error_result = {\n            \"error\": f\"执行失败: {str(e)}\"\n        }\n        print(json.dumps(error_result, ensure_ascii=False))\n        # 可选：设置退出码为 1 表示错误\n        sys.exit(1)\n\nif __name__ == \"__main__\":\n    main()"
    }
  ],
  "reference": []
}
```