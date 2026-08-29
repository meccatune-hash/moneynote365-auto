# -*- coding: utf-8 -*-
"""빈 카테고리에 초기 콘텐츠 생성 & 발행"""
import sys, os, requests, base64
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.collectors.us_market      import collect_us_market
from data.collectors.kr_market      import collect_kr_market
from data.collectors.crypto         import collect_crypto
from report.generator               import format_market_data_for_prompt
from report.category_generator      import generate_category_post
from publisher.wp_publisher         import publish_post, sanitize_for_waf

api  = os.getenv("WP_API_URL")
user = os.getenv("WP_USERNAME")
pw   = os.getenv("WP_PASSWORD")
tok  = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}


def get_cat_id(slug):
    r = requests.get(f"{api}/categories?slug={slug}", headers=hdrs, timeout=10)
    items = r.json()
    return items[0]["id"] if items else None


print("="*55)
print("  빈 카테고리 초기 콘텐츠 생성")
print("="*55)

print("\n[1] 시장 데이터 수집...")
us   = collect_us_market()
kr   = collect_kr_market()
coin = collect_crypto()
mstr = format_market_data_for_prompt(us, kr, coin)
print("  ✅ 완료")

# 글 0개인 카테고리 목록
empty_cats = [
    "global-stock",
    "bonds-rates",
    "futures-options",
    "short-selling",
    "economic-indicators",
    "investment-strategy",
    "invest-study",
    "us-stock",
]

print(f"\n[2] {len(empty_cats)}개 카테고리 보고서 생성 & 발행...")
results = []
for i, cat in enumerate(empty_cats):
    print(f"\n  [{i+1}/{len(empty_cats)}] {cat}")
    try:
        data  = generate_category_post(cat, mstr)
        cid   = get_cat_id(cat)
        clean = sanitize_for_waf(data["content"])
        pid, url = publish_post(
            title       = data["title"],
            content     = clean,
            category_ids= [cid] if cid else [],
            excerpt     = data["excerpt"],
            status      = "publish",
        )
        if url:
            print(f"  ✅ {url[:80]}")
            results.append((cat, True, url))
        else:
            results.append((cat, False, "발행 실패"))
    except Exception as e:
        print(f"  ❌ {e}")
        results.append((cat, False, str(e)[:60]))

print(f"\n{'='*55}")
ok = sum(1 for _, s, _ in results if s)
print(f"  완료: {ok}/{len(results)}개")
for cat, ok, info in results:
    print(f"  {'✅' if ok else '❌'} {cat}: {info[:60]}")
print("="*55)
