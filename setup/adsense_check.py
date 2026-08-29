# -*- coding: utf-8 -*-
"""애드센스 승인 체크리스트 전체 진단"""
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()

WP_URL = os.getenv("WP_URL")
api    = os.getenv("WP_API_URL")
user   = os.getenv("WP_USERNAME")
pw     = os.getenv("WP_PASSWORD")
tok    = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs   = {"Authorization": f"Basic {tok}"}

print("="*60)
print("  구글 애드센스 승인 체크리스트 진단")
print("="*60)

# 1. 사이트 기본 정보
r = requests.get(f"{api}/settings", headers=hdrs, timeout=10)
s = r.json()
print(f"\n[사이트 정보]")
print(f"  제목: {s.get('title','')}")
print(f"  설명: {s.get('description','')}")
print(f"  URL:  {s.get('url','')}")

# 2. 필수 페이지 확인
print(f"\n[필수 페이지]")
must_pages = ["privacy-policy-2", "contact", "about", "disclaimer"]
r2 = requests.get(f"{api}/pages?per_page=30&status=publish", headers=hdrs, timeout=10)
existing = {p["slug"]: p for p in r2.json()}
for slug in must_pages:
    status = "✅" if slug in existing else "❌ 없음"
    title  = existing.get(slug, {}).get("title", {}).get("rendered", "")
    print(f"  {status} {slug}: {title[:40]}")

# 3. 카테고리 & 글 수
print(f"\n[카테고리별 글 수]")
r3 = requests.get(f"{api}/categories?per_page=30", headers=hdrs, timeout=10)
cats = r3.json()
for c in sorted(cats, key=lambda x: x.get("count",0), reverse=True):
    if c["slug"] == "uncategorized": continue
    bar = "█" * min(c.get("count",0), 20)
    print(f"  {c.get('count',0):3d}개 {bar} {c['name']}")

# 4. 전체 포스트 수
r4 = requests.get(f"{api}/posts?per_page=1&status=publish", headers=hdrs, timeout=10)
total = r4.headers.get("X-WP-Total", "?")
print(f"\n[전체 발행 글 수]: {total}개")

# 5. 사이트 head 확인
print(f"\n[Head 태그 확인]")
rh = requests.get(WP_URL, timeout=10)
head = rh.text[:4000]
checks = {
    "viewport 메타태그":     "viewport",
    "charset UTF-8":        "UTF-8",
    "canonical URL":        "canonical",
    "OG 메타태그":           "og:title",
    "robots 허용":           "index, follow",
    "Yoast SEO":            "Yoast SEO",
    "구조화 데이터(schema)": "schema.org",
    "구글 인증 메타태그":    "google-site-verification",
}
for label, keyword in checks.items():
    status = "✅" if keyword.lower() in head.lower() else "❌ 없음"
    print(f"  {status} {label}")

# 6. 메뉴 확인
print(f"\n[네비게이션 메뉴]")
r5 = requests.get(f"{WP_URL}/wp-json/wp/v2/menus", headers=hdrs, timeout=10)
if r5.status_code == 200:
    menus = r5.json()
    print(f"  메뉴 수: {len(menus)}")
    for m in menus:
        print(f"  - {m.get('name','')}: {m.get('count',0)}개 항목")
else:
    print(f"  ❌ 메뉴 API 응답 없음 ({r5.status_code})")

print(f"\n{'='*60}")
print("  진단 완료!")
print(f"{'='*60}")
