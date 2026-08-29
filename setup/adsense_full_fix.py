# -*- coding: utf-8 -*-
"""
구글 애드센스 승인 완전 최적화 스크립트
1. 사이트 제목 수정
2. 네비게이션 블록 메뉴 생성 (Twenty Twenty-Five 블록 테마)
3. 구글 인증 태그 Yoast SEO 설정
4. AI 콘텐츠 공개 페이지 생성
5. 필수 페이지 완성도 강화
"""
import requests, base64, os, json, time
from dotenv import load_dotenv
load_dotenv()

WP_URL = os.getenv("WP_URL")
api    = os.getenv("WP_API_URL")
user   = os.getenv("WP_USERNAME")
pw     = os.getenv("WP_PASSWORD")
tok    = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs   = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}
VERIFY = "ggNHqs8O0A4uBwxxNypiir6-GTSdXUORzvNh0t8NG_8"

print("="*60)
print("  구글 애드센스 승인 최적화 시작")
print("="*60)


# ── STEP 1: 사이트 제목 & 설명 수정 ─────────────────────
print("\n[STEP 1] 사이트 기본 정보 수정...")
r = requests.post(f"{api}/settings", json={
    "title":         "머니노트365",
    "description":   "매일 업데이트되는 글로벌 투자 보고서 | KOSPI·S&P500·비트코인 분석",
    "url":           "https://kingbrightsucces.com",
}, headers=hdrs, timeout=10)
print(f"  사이트 설정: {r.status_code}")
if r.status_code == 200:
    d = r.json()
    print(f"  ✅ 제목: {d.get('title','')} | 설명: {d.get('description','')[:40]}")


# ── STEP 2: 네비게이션 블록 메뉴 (wp_navigation post type) ──
print("\n[STEP 2] 네비게이션 메뉴 생성 (블록 테마)...")

nav_content = """<!-- wp:navigation-link {"label":"홈","url":"%s/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"일일 보고서","url":"%s/category/daily-report/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"모닝 뉴스","url":"%s/category/morning-news/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"국내 주식","url":"%s/category/kr-stock/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"미국 주식","url":"%s/category/us-stock/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"암호화폐","url":"%s/category/crypto/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"투자 전략","url":"%s/category/investment-strategy/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"공부방","url":"%s/category/invest-study/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"소개","url":"%s/about/","isTopLevelLink":true} /-->""" % tuple([WP_URL]*9)

r2 = requests.post(f"{api}/navigation", json={
    "title":   "머니노트365 메인 메뉴",
    "content": nav_content,
    "status":  "publish",
}, headers=hdrs, timeout=15)
print(f"  wp_navigation: {r2.status_code}")
if r2.status_code in (200, 201):
    nav_id = r2.json().get("id")
    print(f"  ✅ 네비게이션 블록 생성 완료 (ID: {nav_id})")
else:
    # 폴백: 기존 클래식 메뉴 아이템 재생성
    print(f"  ℹ️ 블록 네비게이션 실패 - 클래식 메뉴 항목 보완")
    menu_id = 73  # 기존에 생성된 메뉴 ID
    menu_items = [
        ("🏠 홈",          WP_URL),
        ("📋 일일 보고서", f"{WP_URL}/category/daily-report/"),
        ("🌅 모닝 뉴스",   f"{WP_URL}/category/morning-news/"),
        ("🇰🇷 국내 주식", f"{WP_URL}/category/kr-stock/"),
        ("🇺🇸 미국 주식", f"{WP_URL}/category/us-stock/"),
        ("🪙 암호화폐",   f"{WP_URL}/category/crypto/"),
        ("💡 투자 전략",   f"{WP_URL}/category/investment-strategy/"),
        ("📚 공부방",      f"{WP_URL}/category/invest-study/"),
        ("ℹ️ 소개",        f"{WP_URL}/about/"),
    ]
    for order, (label, url) in enumerate(menu_items, 1):
        ri = requests.post(f"{api}/menu-items", json={
            "title": label, "url": url, "type": "custom",
            "status": "publish", "menus": menu_id, "menu_order": order,
        }, headers=hdrs, timeout=10)
        status = "✅" if ri.status_code == 201 else f"❌{ri.status_code}"
        print(f"    {status} {label}")


# ── STEP 3: AI 콘텐츠 공개 & 저작권 페이지 ─────────────
print("\n[STEP 3] AI 콘텐츠 공개 페이지 생성...")

ai_disclosure = """<h2>AI 생성 콘텐츠 공개 (AI Content Disclosure)</h2>
<p>머니노트365는 Google Gemini AI를 활용하여 금융 투자 보고서 및 뉴스 브리핑을 자동 생성합니다. 본 사이트의 콘텐츠 생성 방식에 대해 투명하게 공개합니다.</p>

<h2>데이터 수집 출처</h2>
<ul>
<li><strong>주식 시장 데이터:</strong> Yahoo Finance API (실시간 시세, 지수, 섹터 데이터)</li>
<li><strong>암호화폐 데이터:</strong> CoinGecko API (가격, 시가총액, 공포탐욕지수)</li>
<li><strong>글로벌 뉴스:</strong> CNN Business, BBC Business, CNBC, MarketWatch RSS 피드</li>
<li><strong>경제 지표:</strong> 공개 금융 데이터 API</li>
</ul>

<h2>AI 분석 과정</h2>
<p>수집된 실제 시장 데이터를 Google Gemini AI 모델에 입력하여 분석 보고서를 생성합니다. AI는 데이터를 기반으로 설명, 해설, 투자 인사이트를 작성합니다. 모든 수치는 실제 데이터에 기반하며, AI의 해석 및 분석이 포함됩니다.</p>

<h2>콘텐츠의 한계</h2>
<ul>
<li>AI가 생성한 내용은 오류를 포함할 수 있습니다</li>
<li>미래 시장 예측은 불확실하며 실제 결과와 다를 수 있습니다</li>
<li>본 콘텐츠는 교육 및 정보 제공 목적이며, 투자 권유가 아닙니다</li>
</ul>

<h2>업데이트 주기</h2>
<table>
<thead><tr><th>콘텐츠</th><th>발행 시간</th><th>출처</th></tr></thead>
<tbody>
<tr><td>모닝 뉴스 브리핑</td><td>매일 오전 7:00 KST</td><td>CNN, BBC, CNBC, MarketWatch</td></tr>
<tr><td>카테고리별 분석</td><td>매일 오전 9:00 KST</td><td>Yahoo Finance, CoinGecko</td></tr>
<tr><td>일일 투자 보고서</td><td>매일 오후 1:00 KST</td><td>Yahoo Finance, CoinGecko</td></tr>
</tbody>
</table>

<h2>문의</h2>
<p>콘텐츠 관련 문의 또는 오류 제보는 <a href="/contact/">문의하기</a> 페이지를 이용해 주세요.</p>"""

r3 = requests.post(f"{api}/pages", json={
    "title":   "AI 콘텐츠 공개 안내",
    "slug":    "ai-disclosure",
    "content": ai_disclosure,
    "status":  "publish",
}, headers=hdrs, timeout=15)
print(f"  AI 공개 페이지: {r3.status_code}")
if r3.status_code == 201:
    print(f"  ✅ 생성: {r3.json().get('link','')}")
elif r3.status_code == 422:
    print("  ℹ️  이미 존재")


# ── STEP 4: Yoast SEO 구글 인증 직접 설정 ─────────────
print("\n[STEP 4] 구글 인증 메타태그 설정...")
# Yoast SEO wpseo 옵션 업데이트 - WPCode 플러그인으로 확실하게 삽입
# WPCode 스니펫 생성 (custom post type)
snippet_content = f'<meta name="google-site-verification" content="{VERIFY}" />'

# WPCode 방식 1: wpcode REST API
for ep in [f"{WP_URL}/wp-json/wpcode/v1/snippets",
           f"{api}/wpcode",
           f"{api}/wpcode_snippet"]:
    rs = requests.post(ep, json={
        "title": "Google Search Console Verification",
        "content": snippet_content,
        "status": "publish",
        "meta": {
            "wpcode_snippet_type": "html",
            "wpcode_snippet_location": "site_wide_header",
        }
    }, headers=hdrs, timeout=10)
    if rs.status_code in (200, 201):
        print(f"  ✅ WPCode 스니펫 생성 성공!")
        break

# Yoast SEO 설정 시도
yoast_payloads = [
    {"wpseo_googleverify": VERIFY},
    {"googleverify": VERIFY},
    {"google_site_verification": VERIFY},
]
for payload in yoast_payloads:
    ry = requests.post(f"{api}/settings", json=payload, headers=hdrs, timeout=10)
    if ry.status_code == 200 and list(payload.keys())[0] in ry.json():
        print(f"  ✅ Yoast 설정: {list(payload.keys())[0]}")
        break

print(f"  ℹ️  관리자 패널에서 직접 설정 권장:")
print(f"      → {WP_URL}/wp-admin/admin.php?page=wpseo_general")
print(f"      → Site connections 탭 → Google: {VERIFY}")


# ── STEP 5: 광고 정책 준수 안내 페이지 ─────────────────
print("\n[STEP 5] 저작권 & 광고 정책 안내 페이지...")

copyright_content = """<h2>저작권 안내 (Copyright Notice)</h2>
<p>머니노트365(moneynote365)의 모든 콘텐츠는 저작권법의 보호를 받습니다.</p>

<h2>콘텐츠 이용 조건</h2>
<ul>
<li>본 사이트의 콘텐츠는 개인 비상업적 용도로만 이용 가능합니다</li>
<li>상업적 이용, 무단 복제, 배포는 금지됩니다</li>
<li>출처 표기 후 일부 인용은 허용됩니다 (출처: 머니노트365)</li>
</ul>

<h2>외부 데이터 저작권</h2>
<p>본 사이트에서 사용하는 금융 데이터는 Yahoo Finance, CoinGecko 등의 서비스에서 제공됩니다. 해당 데이터의 저작권은 각 제공 기관에 있습니다.</p>

<h2>면책 조항 (Disclaimer)</h2>
<p>본 사이트의 모든 투자 정보는 교육 목적으로 제공되며, 특정 종목의 매수·매도를 권유하지 않습니다. 투자 결정은 본인의 판단과 책임하에 이루어져야 합니다.</p>

<h2>문의</h2>
<p>저작권 관련 문의: <a href="/contact/">문의하기</a></p>"""

r5 = requests.post(f"{api}/pages", json={
    "title":   "저작권 & 광고 정책",
    "slug":    "copyright",
    "content": copyright_content,
    "status":  "publish",
}, headers=hdrs, timeout=10)
print(f"  저작권 페이지: {r5.status_code}")
if r5.status_code in (200, 201):
    print(f"  ✅ 생성 완료")


# ── STEP 6: 최종 사이트 정보 확인 ───────────────────────
print("\n[STEP 6] 최종 확인...")
time.sleep(2)
rf = requests.get(f"{api}/settings", headers=hdrs, timeout=10)
sf = rf.json()
print(f"  사이트 제목: {sf.get('title','')}")
print(f"  사이트 설명: {sf.get('description','')}")

r_posts = requests.get(f"{api}/posts?per_page=1&status=publish", headers=hdrs, timeout=10)
print(f"  전체 글 수: {r_posts.headers.get('X-WP-Total','?')}개")

rh2 = requests.get(WP_URL, timeout=10)
title_in_html = "머니노트365" in rh2.text
print(f"  홈페이지 사이트명: {'✅ 머니노트365 확인' if title_in_html else '❌ 아직 변경 안됨'}")

print(f"""
{'='*60}
  ✅ 애드센스 최적화 완료!
{'='*60}
""")
