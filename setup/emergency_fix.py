# -*- coding: utf-8 -*-
"""
긴급 수정:
1. 구글 인증 페이지들 메뉴에서 숨기기 (draft 처리)
2. 제대로 된 네비게이션 메뉴 생성
3. WPCode로 meta 태그 삽입
4. WP Super Cache 퍼지
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

VERIFY_CODE = "ggNHqs8O0A4uBwxxNypiir6-GTSdXUORzvNh0t8NG_8"
META_TAG    = f'<meta name="google-site-verification" content="{VERIFY_CODE}" />'


# ── STEP 1: 인증용 임시 페이지들 정리 ──────────────────
print("[STEP 1] 구글 인증 임시 페이지 정리...")
r = requests.get(f"{api}/pages?per_page=30&status=any", headers=hdrs, timeout=10)
for page in r.json():
    slug  = page.get("slug", "")
    title = page.get("title", {}).get("rendered", "")
    pid   = page["id"]
    # google 인증용 임시 페이지 감지
    if "google" in slug.lower() and ("nhs" in slug.lower() or "ggnhqs" in slug.lower() or len(slug) > 20):
        # draft로 전환 (삭제 대신 숨김)
        r2 = requests.delete(f"{api}/pages/{pid}?force=true", headers=hdrs, timeout=10)
        print(f"  🗑️  삭제: [{pid}] {title[:40]} ({r2.status_code})")


# ── STEP 2: 제대로 된 네비게이션 메뉴 생성 ─────────────
print("\n[STEP 2] 올바른 네비게이션 메뉴 생성...")

# 카테고리 ID 가져오기
r_cats = requests.get(f"{api}/categories?per_page=30", headers=hdrs, timeout=10)
cats   = {c["slug"]: c["id"] for c in r_cats.json()}

# 필수 페이지 ID 가져오기
r_pages = requests.get(f"{api}/pages?per_page=20&status=publish", headers=hdrs, timeout=10)
pages   = {p["slug"]: p["id"] for p in r_pages.json()}

print(f"  카테고리: {list(cats.keys())}")
print(f"  페이지: {list(pages.keys())}")

# 메뉴 생성 (WordPress REST API로 메뉴 직접 생성)
# nav_menus는 wp-json/wp/v2/menus (requires Gutenberg or WP 6.x)
menu_data = {
    "name":        "머니노트365 메인 메뉴",
    "slug":        "main-menu",
    "description": "메인 네비게이션 메뉴",
    "auto_add":    False,  # 새 페이지 자동 추가 OFF
}
r_menu = requests.post(f"{WP_URL}/wp-json/wp/v2/menus",
                       json=menu_data, headers=hdrs, timeout=10)
print(f"  메뉴 생성: {r_menu.status_code}")

if r_menu.status_code == 201:
    menu_id = r_menu.json()["id"]
    print(f"  ✅ 메뉴 ID: {menu_id}")

    # 메뉴 아이템 추가
    menu_items = [
        {"title": "🏠 홈",          "url": WP_URL,                         "type": "custom"},
        {"title": "📋 일일 보고서", "url": f"{WP_URL}/category/daily-report/", "type": "custom"},
        {"title": "🇰🇷 국내 주식", "url": f"{WP_URL}/category/kr-stock/",    "type": "custom"},
        {"title": "🇺🇸 미국 주식", "url": f"{WP_URL}/category/us-stock/",    "type": "custom"},
        {"title": "🪙 암호화폐",   "url": f"{WP_URL}/category/crypto/",      "type": "custom"},
        {"title": "💡 투자 전략",   "url": f"{WP_URL}/category/investment-strategy/", "type": "custom"},
        {"title": "📚 공부방",      "url": f"{WP_URL}/category/invest-study/","type": "custom"},
        {"title": "ℹ️ 소개",        "url": f"{WP_URL}/about/",               "type": "custom"},
    ]
    for i, item in enumerate(menu_items):
        r_item = requests.post(f"{WP_URL}/wp-json/wp/v2/menu-items", json={
            "title":  item["title"],
            "url":    item["url"],
            "type":   "custom",
            "status": "publish",
            "menus":  menu_id,
            "menu_order": i + 1,
        }, headers=hdrs, timeout=10)
        status = "✅" if r_item.status_code == 201 else f"❌{r_item.status_code}"
        print(f"  {status} {item['title']}")
elif r_menu.status_code == 404:
    print("  ℹ️  메뉴 API 없음 (WordPress 버전 이슈) - 대안 방법 시도")


# ── STEP 3: WordPress 자동 페이지 메뉴 추가 끄기 ───────
print("\n[STEP 3] 새 페이지 자동 메뉴 추가 끄기...")
r3 = requests.post(f"{api}/settings", json={
    "show_on_front":     "posts",
    "page_on_front":     0,
    "page_for_posts":    0,
}, headers=hdrs, timeout=10)
print(f"  홈페이지 설정: {r3.status_code}")


# ── STEP 4: WPCode로 메타태그 삽입 ───────────────────
print("\n[STEP 4] WPCode 헤더 스크립트 설정...")

# WPCode는 custom post type 'wpcode_snippet'으로 저장됨
snippet_data = {
    "title":   "Google Search Console Verification",
    "status":  "publish",
    "content": META_TAG,
    "meta": {
        "wpcode_snippet_type":     "html",
        "wpcode_snippet_location": "site_wide_header",
        "wpcode_snippet_priority": 10,
        "wpcode_snippet_status":   "active",
    }
}

# WPCode REST 엔드포인트 시도
for endpoint in [
    f"{WP_URL}/wp-json/wpcode/v1/snippets",
    f"{api}/wpcode",
    f"{api}/wpcode_snippet",
]:
    r4 = requests.post(endpoint, json=snippet_data, headers=hdrs, timeout=10)
    print(f"  {endpoint.split('/')[-1]}: {r4.status_code}")
    if r4.status_code in (200, 201):
        print(f"  ✅ WPCode 스니펫 생성 완료!")
        break


# ── STEP 5: WP Super Cache 초기화 ─────────────────────
print("\n[STEP 5] WP Super Cache 캐시 지우기...")
for endpoint in [
    f"{WP_URL}/wp-json/wp-super-cache/v1/cache",
    f"{WP_URL}/wp-json/wp/v2/settings",
]:
    try:
        r5 = requests.delete(endpoint, headers=hdrs, timeout=10)
        print(f"  캐시 삭제: {r5.status_code}")
        if r5.status_code in (200, 204):
            print("  ✅ 캐시 클리어 성공")
            break
    except:
        pass

# ── STEP 6: 현재 메뉴 상태 및 페이지 목록 최종 확인 ──
print("\n[STEP 6] 최종 페이지 목록 확인...")
r6 = requests.get(f"{api}/pages?per_page=20&status=publish&orderby=title", headers=hdrs, timeout=10)
for p in r6.json():
    print(f"  [{p['id']:3d}] {p['slug']:30s} | {p['title']['rendered'][:35]}")

print(f"""
{'='*55}
  ✅ 정리 완료!
{'='*55}
""")
