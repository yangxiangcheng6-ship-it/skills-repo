---
name: hello-gen
description: 本技能用于在用户请求生成问候语或验证系统功能时触发。运行脚本输出包含当前日期时间的JSON格式问候信息，用于端到端验证自动技能包生成系统。
---

# 执行流程

1. 运行 `python Scripts/hello.py`
2. 脚本将输出标准 JSON 格式数据：`{"ok": true, "now": "YYYY-MM-DD HH:MM:SS"}`
3. 若执行过程中出现异常，将返回结构化错误信息：`{\"error\": \"错误描述\"}`",
  "scripts": {
    "Scripts/hello.py": "import sys\nimport json\nfrom datetime import datetime\n\ndef main():\n    # 配置标准输出为 UTF-8 编码，防止中文乱码\n    sys.stdout.reconfigure(encoding=\"utf-8\", errors=\"replace\")\n    \n    try:\n        # 获取当前日期时间并格式化为指定字符串\n        now_str = datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")\n        \n        # 构建成功响应对象\n        result = {\n            \"ok\": True,\n            \"now\": now_str\n        }\n        \n        # 输出 JSON 格式结果\n        print(json.dumps(result, ensure_ascii=False))\n        \n    except Exception as e:\n        # 异常处理：返回结构化错误信息，禁止裸崩溃\n        error_result = {\n            \"error\": str(e)\n        }\n        print(json.dumps(error_result, ensure_ascii=False))\n        sys.exit(1)\n\nif __name__ == \"__main__\":\n    main()"
  },
  "reference": {}
}
```