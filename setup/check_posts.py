# -*- coding: utf-8 -*-
"""현재 포스트 전체 상태 확인"""
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()

api  = os.getenv("WP_API_URL")
user = os.getenv("WP_USERNAME")
pw   = os.getenv("WP_PASSWORD")
tok  = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}"}

r = requests.get(f"{api}/posts?per_page=20&status=any&orderby=date&order=desc", headers=hdrs, timeout=10)
posts = r.json()
print(f"총 {len(posts)}개 포스트:\n" + "-"*70)
for p in posts:
    chars = len(p.get("content", {}).get("rendered", ""))
    print(f"ID:{p['id']:3d} | {p['date'][:10]} | {p['status']:8s} | {chars:6,}자 | {p['title']['rendered'][:50]}")
