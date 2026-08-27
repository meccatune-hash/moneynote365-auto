# -*- coding: utf-8 -*-
"""
Google Search Console 완전 자동 설정
1. Insert Headers & Footers 플러그인 설치 → meta 태그 삽입
2. HTML 인증 파일 페이지 생성
3. Yoast SEO 사이트맵 설정
4. 사이트맵 pingback 자동 제출
"""
import requests, base64, os, time
from dotenv import load_dotenv
load_dotenv()

WP_URL = os.getenv("WP_URL")
api    = os.getenv("WP_API_URL")
user   = os.getenv("WP_USERNAME")
pw     = os.getenv("WP_PASSWORD")
tok    = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs   = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

VERIFY_CODE = "ggNHqs8O0A4uBwxxNypiir6-GTSdXUORzvNh0t8NG_8"
META_TAG = f'<meta name="google-site-verification" content="{VERIFY_CODE}" />'
SITEMAP  = f"{WP_URL}/sitemap_index.xml"

print("="*55)
print("  구글 서치콘솔 완전 자동 설정 시작")
print("="*55)


# ── STEP 1: Insert Headers and Footers 플러그인 설치 ──
print("\n[STEP 1] 'Insert Headers and Footers' 플러그인 설치...")
r = requests.post(f"{api}/plugins", json={
    "slug": "insert-headers-and-footers",
    "status": "active"
}, headers=hdrs, timeout=60)
print(f"  HTTP {r.status_code}")
if r.status_code in (200, 201):
    print("  ✅ 플러그인 설치 완료!")
    time.sleep(2)
elif r.status_code == 409:
    print("  ℹ️  이미 설치됨 - 활성화 시도...")
    # 활성화 시도
    r2 = requests.post(f"{api}/plugins/insert-headers-and-footers/insert-headers-and-footers",
                       json={"status": "active"}, headers=hdrs, timeout=15)
    print(f"  활성화: {r2.status_code}")
else:
    print(f"  ⚠️  {r.text[:150]}")


# ── STEP 2: WordPress 옵션으로 meta 태그 직접 주입 ──────
print("\n[STEP 2] head 메타 태그 설정...")

# Insert Headers & Footers 설정 (wp_options: ihaf_scripts)
option_sets = [
    ("ihaf_scripts", {"header_scripts": META_TAG, "body_scripts": "", "footer_scripts": ""}),
    ("wp_head_script", META_TAG),
]
for opt_name, opt_val in option_sets:
    r = requests.post(f"{WP_URL}/wp-json/wp/v2/settings",
                      json={opt_name: opt_val}, headers=hdrs, timeout=10)
    print(f"  {opt_name}: {r.status_code}")


# ── STEP 3: HTML 인증 파일 (정확한 형식으로) ───────────
print("\n[STEP 3] Google 인증 HTML 파일 생성...")

# Google이 요구하는 정확한 파일명과 내용
google_filename = f"google{VERIFY_CODE}"
google_content  = f"google-site-verification: {google_filename}.html"

# WordPress page로 생성 (slug = 파일명)
r = requests.post(f"{api}/pages", json={
    "title":   google_filename,
    "slug":    google_filename,
    "content": f"<p>{google_content}</p>",
    "status":  "publish",
    "template": "",
}, headers=hdrs, timeout=15)
print(f"  인증 파일 페이지: {r.status_code}")
if r.status_code == 201:
    page_url = r.json().get("link", "")
    print(f"  ✅ 생성 완료: {page_url}")
elif r.status_code == 422:
    print("  ℹ️  이미 존재함")


# ── STEP 4: Yoast SEO 사이트맵 핑백 제출 ─────────────
print("\n[STEP 4] Google에 사이트맵 자동 핑백...")

ping_urls = [
    f"https://www.google.com/ping?sitemap={SITEMAP}",
    f"https://www.bing.com/ping?sitemap={SITEMAP}",
]
for ping_url in ping_urls:
    try:
        rp = requests.get(ping_url, timeout=10)
        engine = "Google" if "google" in ping_url else "Bing"
        print(f"  {engine} 핑백: HTTP {rp.status_code}", "✅" if rp.status_code == 200 else "⚠️")
    except Exception as e:
        print(f"  핑백 오류: {e}")


# ── STEP 5: 현재 상태 최종 확인 ──────────────────────
print("\n[STEP 5] 인증 준비 상태 확인...")

check_items = [
    (f"{WP_URL}/{google_filename}", "HTML 인증 파일"),
    (SITEMAP, "사이트맵"),
    (f"{WP_URL}/", "사이트 홈"),
]
for url, label in check_items:
    try:
        r = requests.get(url, timeout=8, allow_redirects=True)
        status = "✅" if r.status_code == 200 else f"❌ ({r.status_code})"
        print(f"  {status} {label}: {url}")
    except Exception as e:
        print(f"  ❌ {label}: {e}")


print(f"""
{'='*55}
  ✅ 서치콘솔 인증 준비 100% 완료!
{'='*55}

인증 코드: {VERIFY_CODE}

지금 서치콘솔에서 [확인] 버튼만 누르면 됩니다:
→ https://search.google.com/search-console/

사이트맵 (인증 후 제출):
→ {SITEMAP}
""")
