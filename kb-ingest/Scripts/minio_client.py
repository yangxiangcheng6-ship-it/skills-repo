#!/usr/bin/env python
"""MinIO S3 客户端（AWS4-HMAC-SHA256 签名，纯标准库，无第三方依赖）。

用法:
    from minio_client import get_object, put_object, list_index, get_doc

环境变量可覆盖默认值:
    MINIO_ENDPOINT  MINIO_ACCESS_KEY  MINIO_SECRET_KEY  MINIO_BUCKET  MINIO_REGION
"""
import hashlib
import hmac
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 本地 Dify/MinIO 直连，禁用系统代理（梯子开着时 localhost 会被发给代理 → 502）
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))

ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000")
ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin123")
BUCKET = os.environ.get("MINIO_BUCKET", "dify-files")
REGION = os.environ.get("MINIO_REGION", "us-east-1")

INDEX_KEY = "_index.json"


def _hmac(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _sign_headers(method: str, encoded_path: str, query: str, body: bytes = b"") -> dict:
    now = datetime.now(timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(body).hexdigest()
    host = urllib.parse.urlparse(ENDPOINT).netloc

    headers = {"host": host, "x-amz-content-sha256": payload_hash, "x-amz-date": amz_date}
    canonical_headers = "".join(f"{k}:{v}\n" for k, v in headers.items())
    signed_headers = ";".join(headers.keys())

    canonical_request = "\n".join([method, encoded_path, query, canonical_headers, signed_headers, payload_hash])
    scope = f"{date_stamp}/{REGION}/s3/aws4_request"
    string_to_sign = "\n".join(["AWS4-HMAC-SHA256", amz_date, scope,
                                hashlib.sha256(canonical_request.encode()).hexdigest()])
    k_date = _hmac(("AWS4" + SECRET_KEY).encode(), date_stamp)
    k_region = _hmac(k_date, REGION)
    k_service = _hmac(k_region, "s3")
    k_signing = _hmac(k_service, "aws4_request")
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
    return {
        "Authorization": f"AWS4-HMAC-SHA256 Credential={ACCESS_KEY}/{scope}, "
                         f"SignedHeaders={signed_headers}, Signature={signature}",
        "x-amz-date": amz_date,
        "x-amz-content-sha256": payload_hash,
    }


def get_object(key: str) -> bytes | None:
    """S3 GET 对象内容（失败返回 None）"""
    encoded = urllib.parse.quote(key, safe="/")
    headers = _sign_headers("GET", f"/{BUCKET}/{encoded}", "")
    req = urllib.request.Request(f"{ENDPOINT}/{BUCKET}/{encoded}", method="GET", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        print(f"  [minio] GET {key} 失败: HTTP {e.code} {e.read().decode()[:150]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  [minio] GET {key} 失败: {e}", file=sys.stderr)
        return None


def put_object(key: str, content: str | bytes) -> bool:
    """S3 PUT 写入对象（文本或 bytes；成功返回 True）"""
    body = content.encode("utf-8") if isinstance(content, str) else content
    encoded = urllib.parse.quote(key, safe="/")
    headers = _sign_headers("PUT", f"/{BUCKET}/{encoded}", "", body)
    headers["Content-Type"] = "application/octet-stream"
    req = urllib.request.Request(f"{ENDPOINT}/{BUCKET}/{encoded}", data=body, method="PUT", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status in (200, 201, 204)
    except urllib.error.HTTPError as e:
        print(f"  [minio] PUT {key} 失败: HTTP {e.code} {e.read().decode()[:150]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  [minio] PUT {key} 失败: {e}", file=sys.stderr)
        return False


def list_index() -> dict | None:
    """读索引 _index.json → {'标准': [...], '偏离': [...]}"""
    data = get_object(INDEX_KEY)
    if not data:
        return None
    return json.loads(data.decode("utf-8"))


def get_doc(version: str, filename: str) -> str | None:
    """按版本+文件名读文档内容（返回字符串）"""
    key = f"{version}/{filename}"
    data = get_object(key)
    return data.decode("utf-8", "replace") if data else None


if __name__ == "__main__":
    import sys as _sys
    action = _sys.argv[1] if len(_sys.argv) > 1 else "list"
    if action == "list":
        idx = list_index()
        if idx is None:
            _sys.exit(1)
        print(f"索引 {INDEX_KEY}: 标准 {len(idx.get('标准', []))} 个 / 偏离 {len(idx.get('偏离', []))} 个")
        for v in ("标准", "偏离"):
            for f in idx.get(v, []):
                print(f"  {v}: {f}")
    elif action == "put" and len(_sys.argv) == 4:
        ok = put_object(_sys.argv[2], _sys.argv[3])
        print(f"put {'OK' if ok else 'FAILED'}: {_sys.argv[2]}")
        _sys.exit(0 if ok else 1)
    else:
        print("用法: python minio_client.py [list | put <key> <content>]")
