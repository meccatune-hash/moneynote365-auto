# -*- coding: utf-8 -*-
"""Firewall test + content chunked publisher"""
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()

api  = os.getenv("WP_API_URL")
user = os.getenv("WP_USERNAME")
pw   = os.getenv("WP_PASSWORD")
tok  = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

# 짧은 테스트
r = requests.post(f"{api}/posts", json={
    "title": "TEST-MN365-FIREWALL",
    "content": "<p>방화벽 테스트</p>",
    "status": "draft"
}, headers=hdrs, timeout=15)
print(f"짧은 포스트: {r.status_code}")
if r.status_code == 201:
    pid = r.json()["id"]
    print(f"[OK] 짧은 포스트 성공 - 긴 내용이 방화벽에 막힘")
    # 긴 내용으로 업데이트 테스트
    long_content = "<p>" + "테스트 내용 " * 500 + "</p>"
    r2 = requests.post(f"{api}/posts/{pid}", json={
        "content": long_content
    }, headers=hdrs, timeout=30)
    print(f"긴 내용 업데이트: {r2.status_code}")
    requests.delete(f"{api}/posts/{pid}?force=true", headers=hdrs, timeout=10)
    print("테스트 포스트 삭제 완료")
else:
    print(f"[FAIL] {r.text[:300]}")
