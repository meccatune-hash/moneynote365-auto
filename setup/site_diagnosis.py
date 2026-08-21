# -*- coding: utf-8 -*-
"""현재 WordPress 사이트 상태 전체 진단"""
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()

api = os.getenv("WP_API_URL")
tok = base64.b64encode(f"{os.getenv('WP_USERNAME')}:{os.getenv('WP_PASSWORD')}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}"}

# 1. 사이트 기본 정보
r = requests.get(f"{os.getenv('WP_URL')}/wp-json", timeout=10)
info = r.json()
print("=== 사이트 정보 ===")
print(f"이름: {info.get('name')}")
print(f"설명: {info.get('description')}")
print(f"URL: {info.get('url')}")

# 2. 테마 정보
r2 = requests.get(f"{api}/themes?status=active", headers=hdrs, timeout=10)
if r2.status_code == 200 and r2.json():
    theme = r2.json()[0]
    print(f"\n=== 활성 테마 ===")
    print(f"테마명: {theme.get('name',{}).get('rendered','')}")
    print(f"버전: {theme.get('version','')}")

# 3. 메뉴 확인
r3 = requests.get(f"{api}/menus", headers=hdrs, timeout=10)
print(f"\n=== 메뉴 ({r3.status_code}) ===")
if r3.status_code == 200:
    for m in r3.json(): print(f"  - {m.get('name')} (ID:{m.get('id')})")

# 4. 카테고리 목록
r4 = requests.get(f"{api}/categories?per_page=30", headers=hdrs, timeout=10)
print(f"\n=== 카테고리 ({len(r4.json())}개) ===")
for c in sorted(r4.json(), key=lambda x: x.get("count",0), reverse=True):
    print(f"  [{c['count']:2d}개] {c['name']} (slug:{c['slug']})")

# 5. 필수 페이지 확인
r5 = requests.get(f"{api}/pages?per_page=20&status=any", headers=hdrs, timeout=10)
print(f"\n=== 페이지 목록 ===")
for p in r5.json():
    print(f"  [{p['status']}] {p['title']['rendered']} -> /{p['slug']}/")

# 6. 플러그인 확인
r6 = requests.get(f"{api}/plugins?status=active", headers=hdrs, timeout=10)
print(f"\n=== 활성 플러그인 ({r6.status_code}) ===")
if r6.status_code == 200:
    for p in r6.json(): print(f"  - {p.get('name')} v{p.get('version')}")
