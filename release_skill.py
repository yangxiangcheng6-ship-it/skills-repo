#!/usr/bin/env python
"""技能包自动发布脚本：把 skills-repo 下所有技能包打包，发布到 Dify（management 工作流）。

用法:
    python release_skill.py            # 发布全部技能包
    python release_skill.py kb-tagger  # 只发布指定技能包

挂在 git hook（.git/hooks/post-commit）后，git commit 即自动发布。
"""
import base64
import hashlib
import hmac
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Windows 上 urllib 会自动读系统代理（注册表）——梯子开着时 localhost 请求
# 会被发给代理导致 502。本地 Dify 必须直连，显式禁用代理。
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))

REPO = Path(__file__).resolve().parent
USER_ID = "e3aed6db-4a91-41a0-8f1d-22fd702aa729"
CONSOLE_URL = "http://localhost/console/api"
APP_ID = "92796212-d221-4d77-99e1-9d68d0a0e6c8"
SECRET_KEY_FILE = Path(r"F:\新建文件夹\dify-main\docker\volumes\app\storage\.dify_secret_key")


def read_secret_key() -> str:
    sk = SECRET_KEY_FILE.read_text(encoding="utf-8").strip()
    if not sk:
        raise RuntimeError(f"{SECRET_KEY_FILE} 为空")
    return sk


def jwt_hs256(payload: dict, secret: str) -> str:
    def b64(b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

    header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = b64(json.dumps(payload, separators=(",", ":")).encode())
    sig = b64(hmac.new(secret.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest())
    return f"{header}.{body}.{sig}"


def tokens() -> tuple[str, str]:
    sk = read_secret_key()
    now = int(time.time())
    return (jwt_hs256({"user_id": USER_ID, "exp": now + 7200}, sk),
            jwt_hs256({"exp": now + 7200, "sub": USER_ID}, sk))


def call(url: str, method: str, access: str, csrf: str, body: dict | None = None,
         multipart: bytes | None = None, content_type: str | None = None) -> tuple[int, str]:
    headers = {"Authorization": f"Bearer {access}", "X-CSRF-Token": csrf, "Cookie": f"csrf_token={csrf}"}
    if multipart is not None:
        headers["Content-Type"] = content_type or "application/octet-stream"
        data = multipart
    elif body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    else:
        data = None
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def run_workflow(access: str, csrf: str, cmd: str, fid: str | None = None) -> str:
    startf = None
    if fid:
        startf = {"type": "custom", "transfer_method": "local_file",
                  "upload_file_id": fid, "name": "skill.zip"}
    body = {"inputs": {"command": cmd, "files": startf}, "files": [], "response_mode": "blocking"}
    status, text = call(f"{CONSOLE_URL}/apps/{APP_ID}/workflows/draft/run", "POST", access, csrf, body)
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("data: "):
            try:
                evt = json.loads(line[6:])
            except json.JSONDecodeError:
                continue
            if evt.get("event") == "workflow_finished":
                d = evt.get("data", {})
                if d.get("error"):
                    return f"ERROR: {d['error']}"
                return (d.get("outputs") or {}).get("result", "")
    return f"ERROR: 无输出 (status={status})"


def upload_zip(access: str, csrf: str, name: str, data: bytes) -> str | None:
    boundary = "----ReleaseSkillBoundary"
    parts = [
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\n'
        f"Content-Type: application/zip\r\n\r\n".encode() + data + b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    status, text = call(f"{CONSOLE_URL}/files/upload", "POST", access, csrf,
                        multipart=b"".join(parts),
                        content_type=f"multipart/form-data; boundary={boundary}")
    if status != 201:
        print(f"    [上传失败] {status}: {text[:300]}")
        return None
    return json.loads(text).get("id")


def make_zip(skill_dir: Path) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(skill_dir.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(skill_dir.parent))
    return buf.getvalue()


def publish(access: str, csrf: str, skill_dir: Path) -> None:
    name = skill_dir.name
    print(f"  [{name}] 打包...")
    zip_data = make_zip(skill_dir)
    print(f"  [{name}] 上传 ({len(zip_data)} 字节)...")
    fid = upload_zip(access, csrf, f"{name}.zip", zip_data)
    if not fid:
        return
    result = run_workflow(access, csrf, "新增技能", fid)
    print(f"  [{name}] 新增技能 → {result.strip()[:200]}")
    if "已存在" in result or "无法获取" in result:
        listing = run_workflow(access, csrf, "查看技能")
        m = re.search(r"(\d+)\.\s*" + re.escape(name), listing)
        if m:
            print(f"  [{name}] 已存在，先删除技能{m.group(1)}...")
            print(f"  [{name}] 删除 → {run_workflow(access, csrf, '删除技能' + m.group(1)).strip()[:200]}")
            result = run_workflow(access, csrf, "新增技能", fid)
            print(f"  [{name}] 重新新增 → {result.strip()[:200]}")
        else:
            print(f"  [{name}] 查看技能输出: {listing.strip()[:300]}")


def main() -> None:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    skills = [d for d in REPO.iterdir()
              if d.is_dir() and (d / "SKILL.md").exists() and d.name != ".git"]
    if only:
        skills = [d for d in skills if d.name == only]
    if not skills:
        print("（没有含 SKILL.md 的技能包子目录，跳过）")
        sys.exit(0)
    access, csrf = tokens()
    for d in skills:
        publish(access, csrf, d)


if __name__ == "__main__":
    main()
