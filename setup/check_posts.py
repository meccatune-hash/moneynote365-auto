# -*- coding: utf-8 -*-
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()

api = os.getenv("WP_API_URL")
tok = base64.b64encode(f"{os.getenv('WP_USERNAME')}:{os.getenv('WP_PASSWORD')}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}"}

# 최근 10개 포스트 확인 (draft 포함)
r = requests.get(f"{api}/posts?per_page=10&status=any&orderby=date&order=desc", headers=hdrs, timeout=10)
posts = r.json()
print(f"최근 포스트 {len(posts)}개:")
print("-"*70)
for p in posts:
    print(f"ID:{p['id']:3d} | {p['date'][:10]} | {p['status']:8s} | {p['title']['rendered'][:45]}")
