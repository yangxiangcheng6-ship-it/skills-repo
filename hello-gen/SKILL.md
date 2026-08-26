---
name: hello-gen
description: 本技能用于端到端验证自动技能包生成系统。当用户需要测试脚本执行环境、标准库兼容性及结构化输出能力时触发。运行后将输出包含当前日期时间的 JSON 问候语。
---

# 执行流程

1. 运行脚本 `python Scripts/hello.py`
2. 脚本将输出一个 JSON 对象，格式如下：
   ```json
   {"ok": true, "now": "YYYY-MM-DD HH:MM:SS"}
   ```
3. 如果执行过程中发生异常，将返回结构化错误信息：
   ```json
   {\"error\": \"错误描述信息\"}\n   ```",
  "scripts": [
    {
      "path": "Scripts/hello.py",
      "content": "import sys\nimport json\nfrom datetime import datetime\n\n# 配置标准输出编码，确保中文及特殊字符正常显示\nsys.stdout.reconfigure(encoding=\"utf-8\", errors=\"replace\")\n\ndef main():\n    \"\"\"\n    主函数：生成包含当前时间的问候语 JSON 输出\n    \"\"\"\n    try:\n        # 获取当前日期时间并格式化\n        now_str = datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")\n        \n        # 构建成功响应结构\n        response = {\n            \"ok\": True,\n            \"now\": now_str\n        }\n        \n        # 输出 JSON 字符串\n        print(json.dumps(response, ensure_ascii=False))\n        \n    except Exception as e:\n        # 捕获所有异常并返回结构化错误信息，禁止裸崩溃\n        error_response = {\n            \"error\": str(e)\n        }\n        print(json.dumps(error_response, ensure_ascii=False))\n        # 非零退出码表示执行失败\n        sys.exit(1)\n\nif __name__ == \"__main__\":\n    main()"
    }
  ],
  "reference": []
}
```