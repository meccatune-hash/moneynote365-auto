# -*- coding: utf-8 -*-
"""
상록 교육 콘텐츠 일괄 발행
모든 카테고리에 AdSense 최적화 가이드 글 발행
"""
import sys, os, requests, base64, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from report.evergreen_generator import EVERGREEN_TOPICS, generate_evergreen_post
from publisher.wp_publisher      import publish_post, sanitize_for_waf

api  = os.getenv("WP_API_URL")
user = os.getenv("WP_USERNAME")
pw   = os.getenv("WP_PASSWORD")
tok  = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}


def get_cat_id(slug):
    r = requests.get(f"{api}/categories?slug={slug}", headers=hdrs, timeout=10)
    items = r.json()
    return items[0]["id"] if items else None


def get_tag_ids(slugs):
    ids = []
    for slug in slugs:
        r = requests.get(f"{api}/tags?slug={slug}", headers=hdrs, timeout=10)
        items = r.json()
        if items:
            ids.append(items[0]["id"])
    return ids


print("=" * 60)
print("  머니노트365 상록 교육 콘텐츠 일괄 발행")
print("  (애드센스 승인 최적화 가이드 글)")
print("=" * 60)

# 전체 발행할 글 목록 구성
all_tasks = []
for cat_slug, topics in EVERGREEN_TOPICS.items():
    for topic in topics:
        all_tasks.append((cat_slug, topic))

total = len(all_tasks)
print(f"\n총 {total}개 교육 콘텐츠 발행 예정\n")

ok_count  = 0
results   = []

for i, (cat_slug, topic) in enumerate(all_tasks):
    print(f"[{i+1:2d}/{total}] 카테고리: {cat_slug}")

    try:
        # 콘텐츠 생성
        post_data = generate_evergreen_post(cat_slug, topic)
        clean     = sanitize_for_waf(post_data["content"])

        # 카테고리 & 태그
        cat_id  = get_cat_id(cat_slug)
        tag_ids = get_tag_ids(["투자교육", "머니노트365", "투자가이드"])

        # 발행
        pid, url = publish_post(
            title        = post_data["title"],
            content      = clean,
            category_ids = [cat_id] if cat_id else [],
            tag_ids      = tag_ids,
            excerpt      = post_data["excerpt"],
            status       = "publish",
        )

        if url:
            print(f"  ✅ 발행: {url[:70]}")
            ok_count += 1
            results.append((cat_slug, True, post_data["title"][:40]))
        else:
            print(f"  ❌ 발행 실패")
            results.append((cat_slug, False, "발행 실패"))

    except Exception as e:
        print(f"  ❌ 오류: {str(e)[:80]}")
        results.append((cat_slug, False, str(e)[:50]))

    # 연속 발행 시 잠시 대기 (API 부하 방지)
    if i < total - 1:
        time.sleep(5)

# 최종 결과
print(f"\n{'=' * 60}")
print(f"  완료: {ok_count}/{total}개 발행 성공")
print(f"{'=' * 60}")
for cat, ok, title in results:
    mark = "✅" if ok else "❌"
    print(f"  {mark} [{cat}] {title}")
print("=" * 60)
