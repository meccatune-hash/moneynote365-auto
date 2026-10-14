# -*- coding: utf-8 -*-
"""
머니노트365 모닝 뉴스 메인 실행 파일
매일 07:00 KST (UTC 22:00 전날) 자동 실행
"""
import sys, os, requests, base64
from datetime import datetime, timezone, timedelta
sys.path.insert(0, str(Path(__file__).parent))
try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

from data.collectors.news_collector import collect_news
from report.news_generator          import (generate_morning_news,
                                            generate_news_title,
                                            generate_news_excerpt)
from publisher.wp_publisher         import publish_post

KST = timezone(timedelta(hours=9))


def _get_header():
    api = os.getenv("WP_API_URL")
    tok = base64.b64encode(
        f"{os.getenv('WP_USERNAME')}:{os.getenv('WP_PASSWORD')}".encode()
    ).decode()
    return api, {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}


def get_id_by_slug(endpoint, slug):
    api, hdrs = _get_header()
    r = requests.get(f"{api}/{endpoint}?slug={slug}", headers=hdrs, timeout=10)
    items = r.json()
    return items[0]["id"] if items else None


def get_tag_ids(slugs):
    api, hdrs = _get_header()
    ids = []
    for slug in slugs:
        r = requests.get(f"{api}/tags?slug={slug}", headers=hdrs, timeout=10)
        items = r.json()
        if items:
            ids.append(items[0]["id"])
    return ids


def main():
    start = datetime.now(KST)
    print("=" * 55)
    print("  머니노트365 모닝 뉴스 브리핑 파이프라인")
    print(f"  시작: {start.strftime('%Y-%m-%d %H:%M KST')}")
    print("=" * 55)

    # Step 1: 뉴스 수집
    print("\n[Step 1] 글로벌 뉴스 수집 (CNN·BBC·Reuters·CNBC)")
    news_data = collect_news()
    total = news_data.get("total_count", 0)
    if total == 0:
        print("  ⚠️  뉴스 수집 실패 - API 없이 일반 브리핑으로 대체")

    # Step 2: AI 뉴스 브리핑 생성
    print("\n[Step 2] AI 모닝 뉴스 브리핑 생성")
    content = generate_morning_news(news_data)
    title   = generate_news_title(news_data=news_data)
    excerpt = generate_news_excerpt()

    # Step 2.5: 관련 사진 2~3장 자동 수집·업로드 및 본문/썸네일 배치
    from publisher.image_manager import enrich_post_with_images
    featured_media_id, content = enrich_post_with_images(
        content=content,
        category_type="morning-news",
        title=title,
        news_items=news_data.get("all_items", news_data.get("news", [])),
        max_images=3
    )

    # Step 3: WordPress 발행
    print("\n[Step 3] WordPress 발행")
    cat_id  = get_id_by_slug("categories", "morning-news")

    # 'morning-news' 카테고리가 없으면 daily-report로
    if not cat_id:
        cat_id = get_id_by_slug("categories", "daily-report")

    tag_ids = get_tag_ids(["글로벌뉴스", "미국증시", "cnn", "bbc", "reuters",
                           "모닝브리핑", "경제뉴스", "투자뉴스"])

    post_id, post_url = publish_post(
        title=title,
        content=content,
        category_ids=[cat_id] if cat_id else [],
        tag_ids=tag_ids,
        featured_media_id=featured_media_id,
        excerpt=excerpt,
        status="publish",
    )

    elapsed = (datetime.now(KST) - start).seconds
    print(f"\n{'=' * 55}")
    if post_url:
        print(f"  ✅ 모닝 뉴스 발행 성공! ({elapsed}초 소요)")
        print(f"  제목: {title}")
        print(f"  URL:  {post_url}")
    else:
        print(f"  ❌ 발행 실패")
    print("=" * 55)


if __name__ == "__main__":
    main()
