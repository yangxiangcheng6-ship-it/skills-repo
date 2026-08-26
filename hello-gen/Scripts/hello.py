import sys
import json
from datetime import datetime


def main():
    # 重新配置标准输出，确保 UTF-8 编码支持，替换无法编码的字符
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    
    try:
        # 获取当前日期和时间
        now = datetime.now()
        # 格式化为指定字符串格式
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # 构建成功响应对象
        result = {
            "ok": True,
            "now": now_str
        }
        
        # 输出 JSON 字符串
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        # 捕获所有异常，返回结构化错误信息，禁止裸崩溃
        error_result = {
            "error": str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False))
        # 非零退出码表示执行失败
        sys.exit(1)


if __name__ == "__main__":
    main()