# -*- coding: utf-8 -*-
"""
8/24~8/27 기존 포스트 재작성 + 중복 삭제 + 오늘 신규 발행
"""
import sys, os, json, requests, base64, time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from data.collectors.us_market import collect_us_market
from data.collectors.kr_market import collect_kr_market
from data.collectors.crypto    import collect_crypto
from report.generator          import generate_daily_report, generate_title, generate_excerpt
from publisher.wp_publisher    import publish_post, sanitize_for_waf

api  = os.getenv("WP_API_URL")
user = os.getenv("WP_USERNAME")
pw   = os.getenv("WP_PASSWORD")
tok  = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

# ── STEP 1: 중복 포스트 삭제 ───────────────────────────
print("[STEP 1] 중복 포스트 정리...")

# 날짜별로 중복이 있는 포스트 ID 확인 후 오래된 것 삭제
r = requests.get(f"{api}/posts?per_page=30&status=any&orderby=date&order=desc", headers=hdrs, timeout=10)
posts = r.json()

# 날짜별 그룹화
from collections import defaultdict
by_date = defaultdict(list)
for p in posts:
    date_key = p["date"][:10]
    by_date[date_key].append(p)

# 중복 날짜의 오래된 포스트 삭제
deleted = []
for date_key, ps in by_date.items():
    # 일일 보고서 포스트만 (제목에 '머니노트365' 포함)
    report_posts = [p for p in ps if "머니노트365" in p.get("title",{}).get("rendered","")]
    if len(report_posts) > 1:
        # 가장 최신 1개만 남기고 나머지 삭제
        keep    = sorted(report_posts, key=lambda x: x["id"])[-1]
        to_del  = [p for p in report_posts if p["id"] != keep["id"]]
        for p in to_del:
            r2 = requests.delete(f"{api}/posts/{p['id']}?force=true", headers=hdrs, timeout=10)
            status = "✅" if r2.status_code == 200 else f"❌{r2.status_code}"
            print(f"  {status} 삭제: ID{p['id']} ({date_key}) - {p['title']['rendered'][:40]}")
            deleted.append(p["id"])

if not deleted:
    print("  ℹ️  중복 없음")


# ── STEP 2: 현재 데이터 수집 ──────────────────────────
print("\n[STEP 2] 현재 시장 데이터 수집...")
us_data     = collect_us_market()
kr_data     = collect_kr_market()
crypto_data = collect_crypto()
print("  ✅ 데이터 수집 완료")

# 카테고리 ID
r_cats = requests.get(f"{api}/categories?per_page=30", headers=hdrs, timeout=10)
cats   = {c["slug"]: c["id"] for c in r_cats.json()}
cat_id = cats.get("daily-report")

# 태그 ID
r_tags = requests.get(f"{api}/tags?per_page=50", headers=hdrs, timeout=10)
tags   = {t["slug"]: t["id"] for t in r_tags.json()}
tag_ids = [v for k, v in tags.items() if k in ["kospi", "sp500", "bitcoin", "vix"]]


# ── STEP 3: 8/24~27 기존 포스트 재작성 ─────────────────
print("\n[STEP 3] 기존 포스트 재작성 (8/24~8/27)...")

# 재작성 대상: 8/24 이후 일일 보고서 포스트
r = requests.get(f"{api}/posts?per_page=20&status=publish&orderby=date&order=desc", headers=hdrs, timeout=10)
target_posts = [
    p for p in r.json()
    if "머니노트365 일일" in p.get("title",{}).get("rendered","")
    and p["date"][:10] >= "2026-08-24"
]
print(f"  재작성 대상: {len(target_posts)}개")

for i, p in enumerate(target_posts):
    pid   = p["id"]
    pdate = p["date"][:10]
    ptitle= p["title"]["rendered"]
    print(f"\n  [{i+1}/{len(target_posts)}] ID:{pid} | {pdate} | 재작성 중...")

    # AI 보고서 새로 생성 (현재 데이터 기반 - 날짜만 조정)
    new_content = generate_daily_report(us_data, kr_data, crypto_data)
    new_title   = p["title"]["rendered"]  # 기존 제목 유지 (날짜 정보 보존)
    new_excerpt = generate_excerpt(us_data, kr_data, crypto_data)

    # WAF 정제
    clean_content = sanitize_for_waf(new_content)

    # 업데이트
    r2 = requests.post(f"{api}/posts/{pid}", json={
        "content": clean_content,
        "excerpt": new_excerpt,
        "status":  "publish",
        "categories": [cat_id] if cat_id else [],
        "tags": tag_ids,
    }, headers=hdrs, timeout=60)

    if r2.status_code == 200:
        print(f"  ✅ 재작성 완료! ({len(clean_content):,}자)")
    else:
        print(f"  ❌ 실패: {r2.status_code} - {r2.text[:100]}")

    # API 부하 방지
    if i < len(target_posts) - 1:
        print("  ⏳ 20초 대기...")
        time.sleep(20)


# ── STEP 4: 오늘(8/27) 포스트가 있는지 확인 후 없으면 신규 발행 ──
print("\n[STEP 4] 오늘 포스트 확인 및 신규 발행...")
today_str = datetime.now().strftime("%Y-%m-%d")
r3 = requests.get(f"{api}/posts?after={today_str}T00:00:00&before={today_str}T23:59:59&status=publish",
                  headers=hdrs, timeout=10)
today_posts = [p for p in r3.json() if "머니노트365 일일" in p.get("title",{}).get("rendered","")]

if today_posts:
    print(f"  ℹ️  오늘 포스트 이미 있음 ({len(today_posts)}개) - 재작성으로 갱신됨")
else:
    print("  오늘 포스트 없음 - 신규 발행...")
    new_content = generate_daily_report(us_data, kr_data, crypto_data)
    new_title   = generate_title(us_data, kr_data, crypto_data)
    new_excerpt = generate_excerpt(us_data, kr_data, crypto_data)

    post_id, post_url = publish_post(
        title=new_title,
        content=new_content,
        category_ids=[cat_id] if cat_id else [],
        tag_ids=tag_ids,
        excerpt=new_excerpt,
        status="publish",
    )
    if post_url:
        print(f"  ✅ 신규 발행 완료: {post_url}")

print(f"\n{'='*55}")
print(f"  ✅ 전체 재작성 완료!")
print(f"  사이트: {os.getenv('WP_URL')}")
print(f"{'='*55}")
