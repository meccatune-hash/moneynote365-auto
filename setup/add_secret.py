# -*- coding: utf-8 -*-
"""GitHub Secret WP_API_URL 추가 + 오늘 빠진 글 수동 발행"""
import requests, os, base64
from dotenv import load_dotenv
load_dotenv()

OWNER = "meccatune-hash"
REPO  = "moneynote365-auto"
TOKEN = os.getenv("GITHUB_TOKEN")
WP_URL= os.getenv("WP_URL")
g_hdrs = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}

print("[1] GitHub Secret WP_API_URL 추가...")

# Public key 가져오기
r = requests.get(
    f"https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/public-key",
    headers=g_hdrs, timeout=10
)
pk = r.json()
print(f"  Public key ID: {pk.get('key_id','')}")

# Secret 암호화 (PyNaCl 없이 GitHub API 직접 사용)
from base64 import b64encode
try:
    from nacl import encoding, public
    def encrypt(pk_b64, secret_value):
        pk_bytes = b64encode(
            public.PublicKey(pk_b64.encode(), encoding.Base64Encoder()).encode()
        )
        sealed = public.SealedBox(
            public.PublicKey(pk_b64.encode(), encoding.Base64Encoder())
        ).encrypt(secret_value.encode())
        return b64encode(sealed).decode()
    
    api_url = f"{WP_URL}/wp-json/wp/v2"
    encrypted = encrypt(pk["key"], api_url)
    r2 = requests.put(
        f"https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/WP_API_URL",
        json={"encrypted_value": encrypted, "key_id": pk["key_id"]},
        headers=g_hdrs, timeout=10
    )
    print(f"  WP_API_URL Secret: {r2.status_code}")
except ImportError:
    print("  nacl 없음 - 대안 방법으로 WP_API_URL 설정")
    # main.py에서 WP_URL로부터 직접 구성하도록 수정 필요
    pass

print("\n완료!")
