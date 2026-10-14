# -*- coding: utf-8 -*-
"""
연예·엔터테인먼트 뉴스 자동 발행 메인 실행 파일
- 하루 2회 (아침 07:30 / 저녁 18:30 KST) 실행
- python main_entertainment.py [--edition morning|evening]
"""
import sys
import os
import argparse
import requests
import base64
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from data.collectors.entertainment_collector import collect_entertainment_news
from report.entertainment_generator import (
    generate_entertainment_report,
    generate_entertainment_title,
    generate_entertainment_excerpt,
    get_current_edition
)
from publisher.wp_publisher import publish_post

KST = timezone(timedelta(hours=9))


def _get_header():
    api = os.getenv("WP_API_URL")
    tok = base64.b64encode(
        f"{os.getenv('WP_USERNAME')}:{os.getenv('WP_PASSWORD')}".encode()
    ).decode()
    return api, {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}


def get_id_by_slug(endpoint, slug):
    api, hdrs = _get_header()
    try:
        r = requests.get(f"{api}/{endpoint}?slug={slug}", headers=hdrs, timeout=10)
        items = r.json()
        return items[0]["id"] if items else None
    except Exception as e:
        print(f"  [WARN] {endpoint}/{slug} 조회 오류: {e}")
        return None


def get_tag_ids(slugs):
    api, hdrs = _get_header()
    ids = []
    for slug in slugs:
        try:
            r = requests.get(f"{api}/tags?slug={slug}", headers=hdrs, timeout=10)
            items = r.json()
            if items:
                ids.append(items[0]["id"])
        except Exception:
            pass
    return ids


def run_entertainment_pipeline(edition: str = None):
    start = datetime.now(KST)
    if not edition:
        edition = get_current_edition()

    edition_kr = "아침 모닝" if edition == "morning" else "저녁 이브닝"

    print("=" * 60)
    print(f"  🎬 머니노트365 연예·엔터테인먼트 뉴스 발행 파이프라인 ({edition_kr})")
    print(f"  시작: {start.strftime('%Y-%m-%d %H:%M KST')}")
    print("=" * 60)

    # Step 1: 기사 수집
    print("\n[Step 1] 연예계 실시간 뉴스 & 핫이슈 수집")
    news_data = collect_entertainment_news()
    total = news_data.get("total_count", 0)
    print(f"  -> 수집된 뉴스 총 {total}건")

    # Step 2: AI 리포트 생성
    print(f"\n[Step 2] AI {edition_kr} 연예 브리핑 생성 (핫이슈 TOP 기사 집중 분석)")
    content = generate_entertainment_report(news_data, edition=edition)
    title   = generate_entertainment_title(edition=edition)
    excerpt = generate_entertainment_excerpt(edition=edition)

    # Step 3: WordPress 발행
    print("\n[Step 3] WordPress 발행")
    cat_id = get_id_by_slug("categories", "entertainment")
    if not cat_id:
        from publisher.wp_publisher import get_or_create_category
        cat_id = get_or_create_category("연예·엔터테인먼트", "entertainment",
                                        "매일 아침·저녁 최신 연예계 핫이슈, 방송/드라마, K-POP, 영화 소식 종합 브리핑")

    tag_ids = get_tag_ids([
        "연예뉴스", "엔터테인먼트", "연예계핫이슈", "KPOP", "드라마",
        "영화", "예능", "방송뉴스", "연예브리핑", "아이돌"
    ])

    post_id, post_url = publish_post(
        title=title,
        content=content,
        category_ids=[cat_id] if cat_id else [],
        tag_ids=tag_ids,
        excerpt=excerpt,
        status="publish",
    )

    elapsed = (datetime.now(KST) - start).seconds
    print("\n" + "=" * 60)
    if post_url:
        print(f"  ✅ 연예 뉴스 ({edition_kr}) 발행 성공! ({elapsed}초 소요)")
        print(f"  제목: {title}")
        print(f"  URL:  {post_url}")
    else:
        print("  ❌ 발행 실패")
    print("=" * 60)
    return post_id, post_url


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entertainment news publisher")
    parser.add_argument("--edition", choices=["morning", "evening"], default=None,
                        help="morning or evening edition (auto-detected if omitted)")
    args = parser.parse_args()
    run_entertainment_pipeline(edition=args.edition)
