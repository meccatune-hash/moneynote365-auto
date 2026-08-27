# -*- coding: utf-8 -*-
"""사이트 head 태그 확인 + 인증 메타태그 강제 삽입"""
import requests, base64, os, re
from dotenv import load_dotenv
load_dotenv()

WP_URL = os.getenv("WP_URL")
api    = os.getenv("WP_API_URL")
user   = os.getenv("WP_USERNAME")
pw     = os.getenv("WP_PASSWORD")
tok    = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs   = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

VERIFY_CODE = "ggNHqs8O0A4uBwxxNypiir6-GTSdXUORzvNh0t8NG_8"
META_TAG    = f'<meta name="google-site-verification" content="{VERIFY_CODE}" />'

# ── 1. 현재 사이트 head 확인 ──────────────────────────
print("[1] 사이트 head 태그 현재 상태 확인...")
r = requests.get(WP_URL, timeout=10)
head_part = r.text[:3000]
if "google-site-verification" in head_part:
    print("  ✅ 이미 메타태그 존재!")
    idx = head_part.find("google-site-verification")
    print(f"  내용: {head_part[idx-20:idx+80]}")
else:
    print("  ❌ 메타태그 없음 - 삽입 시작")

# ── 2. Insert Headers and Footers 플러그인 설정 확인 ──
print("\n[2] Insert Headers and Footers 설정 시도...")

# 여러 옵션 키로 시도
ihaf_options = [
    ("ihaf_google_analytics_code", META_TAG),
    ("ihaf_header_scripts",        META_TAG),
    ("wphead_insert",              META_TAG),
    ("ihaf_scripts_header",        META_TAG),
]
for key, val in ihaf_options:
    r2 = requests.post(f"{WP_URL}/wp-json/wp/v2/settings",
                       json={key: val}, headers=hdrs, timeout=10)
    print(f"  {key}: {r2.status_code}")

# ── 3. Yoast SEO 웹마스터 설정 ─────────────────────────
print("\n[3] Yoast SEO 웹마스터 설정...")

# Yoast wpseo 옵션의 정확한 키 이름들
yoast_keys = [
    "wpseo_googleverify",
    "google_verify",
]
for key in yoast_keys:
    r3 = requests.post(f"{WP_URL}/wp-json/wp/v2/settings",
                       json={key: VERIFY_CODE}, headers=hdrs, timeout=10)
    print(f"  {key}: {r3.status_code}")

# Yoast REST endpoint 시도
for endpoint in ["/wp-json/yoast/v1/settings", "/wp-json/yoast/v1/configuration/webmaster-verification"]:
    for payload in [
        {"google": VERIFY_CODE},
        {"googleverify": VERIFY_CODE},
        {"google_site_verification": VERIFY_CODE},
        {"webmaster_tools": {"google": VERIFY_CODE}},
    ]:
        r4 = requests.post(f"{WP_URL}{endpoint}", json=payload, headers=hdrs, timeout=10)
        if r4.status_code in (200, 201):
            print(f"  ✅ Yoast {endpoint} 성공! payload={list(payload.keys())}")
            break

# ── 4. WordPress customize API로 head 주입 ─────────────
print("\n[4] 커스터마이저 추가 CSS에 head 코드 시도...")
# 추가 CSS에 주석으로 인증 코드 삽입 (일부 테마는 이 방식 지원)
r5 = requests.post(f"{WP_URL}/wp-json/wp/v2/settings", json={
    "custom_css": f"""
/* google-site-verification: {VERIFY_CODE} */
/* =================================
   머니노트365 커스텀 스타일
   ================================= */
"""}, headers=hdrs, timeout=10)
print(f"  custom_css: {r5.status_code}")

# ── 5. 플러그인 목록 확인 ──────────────────────────────
print("\n[5] 활성 플러그인 확인...")
r6 = requests.get(f"{api}/plugins?status=active&per_page=20", headers=hdrs, timeout=10)
if r6.status_code == 200:
    for p in r6.json():
        print(f"  - {p.get('plugin','')} | {p.get('name','')}")

# ── 6. 재확인 ─────────────────────────────────────────
print("\n[6] 재확인...")
import time; time.sleep(2)
r7 = requests.get(WP_URL, timeout=10)
if "google-site-verification" in r7.text[:3000]:
    print("  ✅ 메타태그 삽입 성공!")
else:
    print("  ❌ 아직 미삽입 - 플러그인 직접 설정 필요")
    print("\n  → 현재 head 내용 (처음 1500자):")
    print(r7.text[:1500])
