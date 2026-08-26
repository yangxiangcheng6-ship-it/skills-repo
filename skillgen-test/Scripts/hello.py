#!/usr/bin/env python
"""hello"""
import json
import socket
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
def main():
    print(json.dumps({'ok': True}, ensure_ascii=False))
if __name__ == '__main__':
    main()
