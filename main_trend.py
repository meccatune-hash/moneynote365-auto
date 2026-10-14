# -*- coding: utf-8 -*-
"""
실시간 급상승 트렌드 이슈 자동 포스팅 메인 스크립트 (main_trend.py)
- 대한민국 실시간 검색어 및 조회율 최상위 트렌드 수집
- 일일 5개(기본값) 고품질 심층 포스팅 자동 생성 및 발행
- WordPress REST API + WAF 보안 우회 + 카테고리/태그 자동 매핑
- 실행법: python main_trend.py [--count 5]
"""
import sys
import os
import re
import time
import argparse
import requests
import base64
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
try:
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

from data.collectors.trend_collector import collect_top_trends
from report.trend_generator import build_trend_post
from publisher.wp_publisher import (
    publish_post,
    get_or_create_category,
    get_or_create_tag,
    upload_image,
    get_auth_header
)

KST = timezone(timedelta(hours=9))
WP_API_URL = os.getenv("WP_API_URL")


def upload_trend_pictures(keyword: str, pictures: list, max_count: int = 3) -> list:
    """
    수집된 관련 사진 후보를 다운로드하여 워드프레스 미디어 라이브러리에 업로드
    반환: [{'id': media_id, 'url': media_url, 'source': source, 'caption': caption}, ...]
    """
    uploaded = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    for idx, pic in enumerate(pictures[:max_count], 1):
        url = pic.get("url")
        if not url:
            continue
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200 and len(resp.content) > 500:
                tmp_filename = f"temp_trend_{int(time.time()*1000)}_{idx}.jpg"
                with open(tmp_filename, "wb") as f:
                    f.write(resp.content)
                mid, murl = upload_image(tmp_filename, title=f"{keyword} 관련 현장 사진 {idx}")
                if os.path.exists(tmp_filename):
                    os.remove(tmp_filename)
                if mid and murl:
                    uploaded.append({
                        "id": mid,
                        "url": murl,
                        "source": pic.get("source", "언론사 보도자료"),
                        "caption": pic.get("caption", f"{keyword} 관련 보도 사진")
                    })
                    print(f"    📷 관련 사진 {idx} 업로드 완료 (ID: {mid}) - {pic.get('source')}")
        except Exception as e:
            print(f"    [WARN] 사진 {idx} 업로드 건너뜀: {e}")
    return uploaded


def flush_wp_cache():
    """WP Super Cache 캐시 플러시"""
    try:
        api = os.getenv("WP_API_URL")
        tok = base64.b64encode(f"{os.getenv('WP_USERNAME')}:{os.getenv('WP_PASSWORD')}".encode()).decode()
        hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}
        requests.post(f"{api}/plugins/wp-super-cache/wp-cache", headers=hdrs, json={"status": "inactive"}, timeout=10)
        requests.post(f"{api}/plugins/wp-super-cache/wp-cache", headers=hdrs, json={"status": "active"}, timeout=10)
        print("  [CACHE] WP Super Cache 새로고침 완료")
    except Exception as e:
        print(f"  [WARN] 캐시 새로고침 오류: {e}")


def run_trend_pipeline(count: int = 5):
    """실시간 트렌드 수집 및 상위 N개 포스팅 자동 발행 파이프라인"""
    start_time = datetime.now(KST)
    print("=" * 65)
    print(f"  🔥 머니노트365 실시간 트렌드 이슈 자동 포스팅 파이프라인")
    print(f"  목표: 상위 급상승 트렌드 {count}개 기사 생성 및 발행")
    print(f"  시작 시각: {start_time.strftime('%Y-%m-%d %H:%M:%S KST')}")
    print("=" * 65)

    # 1. 카테고리 확인/생성
    print("\n[Step 1] '트렌드 이슈' 카테고리 확인")
    cat_id = get_or_create_category(
        "트렌드 이슈",
        "trend-issues",
        "실시간 대한민국 최신 급상승 트렌드, 가장 조회율이 높고 화제가 되는 핫이슈 심층 분석"
    )
    if not cat_id:
        print("  [ERROR] 카테고리 ID를 가져올 수 없습니다. 기본값 196 사용")
        cat_id = 196

    # 2. 실시간 트렌드 수집
    print(f"\n[Step 2] 실시간 최고 조회율 트렌드 {count}개 수집 중...")
    trends = collect_top_trends(count=count)
    if not trends:
        print("  [ERROR] 트렌드 데이터를 수집하지 못했습니다.")
        return []

    published_posts = []

    # 3. 개별 트렌드 기사 생성 및 발행
    print(f"\n[Step 3] AI 심층 트렌드 기사 순차 생성 및 발행")
    for idx, item in enumerate(trends, 1):
        keyword = item.get("keyword", "")
        print(f"\n--- [{idx}/{len(trends)}] '{keyword}' 기사 작성 시작 ---")

        try:
            # 1) 관련 사진 최대 3장 워드프레스 미디어 라이브러리 업로드
            pictures = item.get("pictures", [])
            print(f"  [사진 업로드] '{keyword}' 관련 사진 {len(pictures)}건 중 최대 3건 처리")
            uploaded_images = upload_trend_pictures(keyword, pictures, max_count=3)

            # 2) 본문에 사진 2~3장 자동 배치된 기사 생성
            post_data = build_trend_post(item, uploaded_images=uploaded_images)

            # 태그 ID 조회 및 생성
            tag_ids = []
            for tag_name in post_data["tags"]:
                # 한글 태그 slug 생성 (소문자 영문/숫자, 또는 urlencode)
                clean_slug = tag_name.lower().replace(" ", "-")
                tid = get_or_create_tag(tag_name, clean_slug)
                if tid:
                    tag_ids.append(tid)

            # 포스트 발행 (대표 썸네일 featured_media 지정 포함)
            res = publish_post(
                title=post_data["title"],
                content=post_data["content"],
                category_ids=[cat_id],
                tag_ids=tag_ids,
                featured_media_id=post_data.get("featured_media_id"),
                excerpt=post_data["excerpt"],
                status="publish",
                seo_meta={
                    "yoast_title": post_data["title"],
                    "yoast_desc": post_data["excerpt"],
                    "focus_kw": keyword
                }
            )

            if res:
                if isinstance(res, tuple):
                    post_id, post_url = res
                else:
                    post_id = res
                    post_url = f"https://kingbrightsucces.com/?p={post_id}"
                print(f"  🎉 발행 성공! [ID: {post_id}] {post_data['title']}")
                print(f"  🔗 URL: {post_url}")
                published_posts.append({
                    "id": post_id,
                    "keyword": keyword,
                    "title": post_data["title"],
                    "url": post_url
                })
            else:
                print(f"  ❌ 발행 실패: {keyword}")

        except Exception as e:
            print(f"  ❌ {keyword} 기사 생성 중 예외 발생: {e}")

    # 4. 캐시 플러시
    print("\n[Step 4] 전체 사이트 캐시 플러시")
    flush_wp_cache()

    end_time = datetime.now(KST)
    elapsed = (end_time - start_time).total_seconds()
    print("\n" + "=" * 65)
    print(f"  ✨ 트렌드 파이프라인 완료! (총 {len(published_posts)}/{count}개 성공)")
    print(f"  소요 시간: {elapsed:.1f}초")
    for p in published_posts:
        print(f"  - [{p['keyword']}] {p['title']} ({p['url']})")
    print("=" * 65)

    return published_posts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="실시간 트렌드 이슈 5개 자동 포스팅")
    parser.add_argument("--count", type=int, default=5, help="발행할 트렌드 기사 개수 (기본 5개)")
    args = parser.parse_args()

    run_trend_pipeline(count=args.count)
