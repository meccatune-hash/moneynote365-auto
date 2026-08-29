# -*- coding: utf-8 -*-
"""
머니노트365 카테고리별 전문 보고서 메인
매일 09:00 KST 실행
"""
import sys, os, requests, base64
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from data.collectors.us_market      import collect_us_market
from data.collectors.kr_market      import collect_kr_market
from data.collectors.crypto         import collect_crypto
from report.category_generator      import (generate_category_post,
                                            WEEKLY_SCHEDULE, WEEKDAYS)
from report.generator               import format_market_data_for_prompt
from publisher.wp_publisher         import publish_post, sanitize_for_waf

KST = timezone(timedelta(hours=9))


def _api():
    return os.getenv("WP_API_URL")


def _hdrs():
    tok = base64.b64encode(
        f"{os.getenv('WP_USERNAME')}:{os.getenv('WP_PASSWORD')}".encode()
    ).decode()
    return {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}


def get_cat_id(slug: str) -> int | None:
    r = requests.get(f"{_api()}/categories?slug={slug}", headers=_hdrs(), timeout=10)
    items = r.json()
    return items[0]["id"] if items else None


def get_tag_ids_for(slugs: list) -> list:
    ids = []
    for slug in slugs:
        r = requests.get(f"{_api()}/tags?slug={slug}", headers=_hdrs(), timeout=10)
        items = r.json()
        if items:
            ids.append(items[0]["id"])
    return ids


def main():
    now     = datetime.now(KST)
    weekday = now.weekday()       # 0=월 ... 6=일
    wd      = WEEKDAYS[weekday]

    print("=" * 60)
    print(f"  머니노트365 카테고리 전문 보고서 파이프라인")
    print(f"  {now.strftime('%Y-%m-%d %H:%M KST')} ({wd}요일)")
    print("=" * 60)

    # ── 시장 데이터 수집 ─────────────────────────────────
    print("\n[Step 1] 시장 데이터 수집...")
    us_data     = collect_us_market()
    kr_data     = collect_kr_market()
    crypto_data = collect_crypto()
    market_str  = format_market_data_for_prompt(us_data, kr_data, crypto_data)
    print("  ✅ 수집 완료")

    # ── 오늘 카테고리 결정 ────────────────────────────────
    today_cats = WEEKLY_SCHEDULE.get(weekday, ["investment-strategy"])
    print(f"\n[Step 2] 오늘({wd}) 발행 카테고리: {today_cats}")

    # ── 카테고리별 보고서 생성 & 발행 ──────────────────────
    results = []
    for i, cat_slug in enumerate(today_cats):
        print(f"\n[{i+1}/{len(today_cats)}] '{cat_slug}' 보고서 생성 & 발행")

        try:
            # 보고서 생성
            post_data = generate_category_post(cat_slug, market_str)

            # 카테고리 & 태그 ID
            cat_id  = get_cat_id(cat_slug)
            tag_slugs = ["투자분석", "머니노트365", cat_slug.replace("-", "")]
            tag_ids = get_tag_ids_for(tag_slugs)

            # WordPress 발행
            content_clean = sanitize_for_waf(post_data["content"])
            post_id, post_url = publish_post(
                title=post_data["title"],
                content=content_clean,
                category_ids=[cat_id] if cat_id else [],
                tag_ids=tag_ids,
                excerpt=post_data["excerpt"],
                status="publish",
            )

            if post_url:
                print(f"  ✅ 발행 완료: {post_url}")
                results.append({"cat": cat_slug, "url": post_url, "ok": True})
            else:
                print(f"  ❌ 발행 실패")
                results.append({"cat": cat_slug, "ok": False})

        except Exception as e:
            print(f"  ❌ 오류: {e}")
            results.append({"cat": cat_slug, "ok": False, "error": str(e)})

    # ── 결과 요약 ─────────────────────────────────────────
    elapsed = (datetime.now(KST) - now).seconds
    ok_count = sum(1 for r in results if r.get("ok"))
    print(f"\n{'=' * 60}")
    print(f"  ✅ 완료: {ok_count}/{len(results)}개 발행 ({elapsed}초)")
    for r in results:
        status = "✅" if r.get("ok") else "❌"
        print(f"  {status} {r['cat']}: {r.get('url', r.get('error','실패'))}")
    print("=" * 60)


if __name__ == "__main__":
    main()
