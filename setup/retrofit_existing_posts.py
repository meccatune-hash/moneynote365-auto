# -*- coding: utf-8 -*-
"""
기존 게시글 전체 일괄 이미지 등록 및 업데이트 스크립트 (setup/retrofit_existing_posts.py)
- 워드프레스에 발행된 모든 글을 조회
- 이미지가 없거나 2장 미만인 글에 카테고리별 맞춤 고화질 이미지 2~3장 자동 삽입
- 대표 썸네일(featured_media) 자동 설정
- 카테고리별 업로드 미디어 캐싱으로 중복 업로드 방지 및 고속 처리
- 완료 후 캐시 플러시
"""
import os
import re
import sys
import time
import base64
import requests
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

from publisher.image_manager import (
    CATEGORY_FALLBACK_IMAGES,
    download_and_upload_image,
    make_image_block
)

WP_API_URL = os.getenv("WP_API_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")

if not all([WP_API_URL, WP_USERNAME, WP_PASSWORD]):
    print("❌ 환경변수(WP_API_URL, WP_USERNAME, WP_PASSWORD)를 확인해주세요.")
    sys.exit(1)

auth_str = base64.b64encode(f"{WP_USERNAME}:{WP_PASSWORD}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth_str}",
    "Content-Type": "application/json"
}


def get_all_posts():
    """모든 공개(publish) 게시글 페이지네이션 순회 조회"""
    all_posts = []
    page = 1
    while True:
        url = f"{WP_API_URL}/posts?per_page=100&page={page}&status=publish"
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            break
        posts = resp.json()
        if not posts:
            break
        all_posts.extend(posts)
        total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
        print(f"  📄 게시글 {page}/{total_pages} 페이지 로드 완료 ({len(posts)}개)")
        if page >= total_pages:
            break
        page += 1
    return all_posts


def get_categories_map():
    """카테고리 ID -> slug 맵핑 생성"""
    r = requests.get(f"{WP_API_URL}/categories?per_page=100", headers=headers, timeout=15)
    if r.status_code == 200:
        return {c["id"]: c["slug"] for c in r.json()}
    return {}


def determine_category_slug(post, cat_map):
    """게시글의 카테고리 슬러그 판별"""
    cat_ids = post.get("categories", [])
    for cid in cat_ids:
        slug = cat_map.get(cid)
        if slug and slug in CATEGORY_FALLBACK_IMAGES:
            return slug
    for cid in cat_ids:
        slug = cat_map.get(cid)
        if slug:
            return slug
    # 제목 키워드로 fallback 판별
    title = post.get("title", {}).get("rendered", "")
    if "코인" in title or "암호화폐" in title or "비트코인" in title:
        return "crypto"
    if "미국" in title:
        return "us-stock"
    if "국내" in title or "코스피" in title:
        return "kr-stock"
    if "선물" in title or "옵션" in title:
        return "futures-options"
    if "금리" in title or "채권" in title:
        return "bonds-rates"
    if "경제" in title or "지표" in title:
        return "economic-indicators"
    if "공매도" in title:
        return "short-selling"
    if "전략" in title:
        return "investment-strategy"
    if "공부방" in title or "가이드" in title:
        return "invest-study"
    if "모닝" in title or "뉴스" in title:
        return "morning-news"
    if "정치" in title:
        return "politics"
    if "연예" in title:
        return "entertainment"
    if "스포츠" in title:
        return "sports"
    return "daily-report"


def embed_images_into_content(content: str, uploaded_imgs: list) -> str:
    """본문 적절한 위치에 2~3장의 이미지 블록 배치"""
    if not uploaded_imgs:
        return content

    updated = content

    # 1. 첫 번째 이미지: 서론/요약 직후
    img1_block = make_image_block(uploaded_imgs[0])
    if "</p>" in updated:
        first_p_idx = updated.find("</p>") + 4
        updated = updated[:first_p_idx] + "\n" + img1_block + "\n" + updated[first_p_idx:]
    elif "<hr>" in updated:
        updated = updated.replace("<hr>", f"<hr>\n{img1_block}", 1)
    else:
        updated = img1_block + "\n" + updated

    # 2. 두 번째 이미지: 중간 섹션 앞
    if len(uploaded_imgs) > 1:
        img2_block = make_image_block(uploaded_imgs[1])
        h2_matches = [m.start() for m in re.finditer(r'<h2\b', updated)]
        if len(h2_matches) >= 3:
            pos = h2_matches[2]
            updated = updated[:pos] + img2_block + "\n" + updated[pos:]
        elif len(h2_matches) >= 2:
            pos = h2_matches[1]
            updated = updated[:pos] + img2_block + "\n" + updated[pos:]
        else:
            updated += "\n" + img2_block

    # 3. 세 번째 이미지: 결론/FAQ 앞
    if len(uploaded_imgs) > 2:
        img3_block = make_image_block(uploaded_imgs[2])
        if "<h2>❓" in updated:
            updated = updated.replace("<h2>❓", f"{img3_block}\n<h2>❓", 1)
        elif "<h2>📌" in updated:
            updated = updated.replace("<h2>📌", f"{img3_block}\n<h2>📌", 1)
        else:
            h2_matches = [m.start() for m in re.finditer(r'<h2\b', updated)]
            if len(h2_matches) >= 4:
                pos = h2_matches[-2]
                updated = updated[:pos] + img3_block + "\n" + updated[pos:]
            else:
                updated += "\n" + img3_block

    return updated


def flush_cache():
    """WP Super Cache 캐시 삭제"""
    try:
        r = requests.post(
            f"{WP_API_URL}/plugins/wp-super-cache/wp-cache",
            headers=headers,
            json={"cache": "clear"},
            timeout=10
        )
        print(f"🧹 [WP Super Cache] 캐시 플러시 완료 (상태: {r.status_code})")
    except Exception as e:
        print(f"⚠️ [WP Super Cache] 캐시 플러시 예외 (무시 가능): {e}")


def main():
    print("=" * 60)
    print("🚀 [기존 게시글 전체 이미지 등록 및 업데이트 시작]")
    print("=" * 60)

    cat_map = get_categories_map()
    all_posts = get_all_posts()
    print(f"\n📊 총 발행된 게시글 수: {len(all_posts)}개\n")

    # 카테고리별 업로드된 이미지 캐시: {slug: [img1, img2, img3]}
    category_media_cache = {}

    def get_or_upload_category_images(cat_slug: str):
        if cat_slug in category_media_cache:
            return category_media_cache[cat_slug]

        pool = CATEGORY_FALLBACK_IMAGES.get(cat_slug, CATEGORY_FALLBACK_IMAGES.get("default", []))
        print(f"  📥 카테고리 '{cat_slug}' 미디어 라이브러리 이미지 등록 중 ({len(pool)}장)...")
        uploaded = []
        for idx, item in enumerate(pool, 1):
            res = download_and_upload_image(
                image_url=item["url"],
                caption=item["caption"],
                source=item["source"],
                title_for_alt=f"{cat_slug} 테마",
                idx=idx
            )
            if res:
                uploaded.append(res)
            time.sleep(0.3)

        category_media_cache[cat_slug] = uploaded
        return uploaded

    updated_count = 0
    skipped_count = 0

    for i, post in enumerate(all_posts, 1):
        pid = post["id"]
        title = post.get("title", {}).get("rendered", "")
        feat = post.get("featured_media", 0)
        content_raw = post.get("content", {}).get("raw") or post.get("content", {}).get("rendered", "")
        img_count = content_raw.count("<img")

        # 이미 이미지 2장 이상 + featured_media 있으면 건너뜀
        if img_count >= 2 and feat:
            print(f"[{i}/{len(all_posts)}] [ID: {pid}] ⏭️ 이미지({img_count}장) 및 썸네일({feat}) 이미 충족: {title[:30]}")
            skipped_count += 1
            continue

        cat_slug = determine_category_slug(post, cat_map)
        uploaded_imgs = get_or_upload_category_images(cat_slug)

        if not uploaded_imgs:
            print(f"[{i}/{len(all_posts)}] [ID: {pid}] ⚠️ 카테고리 '{cat_slug}' 이미지 준비 실패로 건너뜀")
            continue

        featured_id = feat if feat else uploaded_imgs[0]["id"]
        new_content = content_raw

        # 본문에 이미지가 부족하면 새로 삽입
        if img_count < 2:
            new_content = embed_images_into_content(content_raw, uploaded_imgs)

        # 워드프레스 업데이트 호출
        update_payload = {}
        if img_count < 2:
            update_payload["content"] = new_content
        if not feat:
            update_payload["featured_media"] = featured_id

        if update_payload:
            try:
                up_resp = requests.post(
                    f"{WP_API_URL}/posts/{pid}",
                    headers=headers,
                    json=update_payload,
                    timeout=20
                )
                if up_resp.status_code == 200:
                    print(f"[{i}/{len(all_posts)}] [ID: {pid}] ✅ 업데이트 성공! (카테고리: {cat_slug}, 대표썸네일: {featured_id}) - {title[:35]}")
                    updated_count += 1
                else:
                    print(f"[{i}/{len(all_posts)}] [ID: {pid}] ❌ 업데이트 실패: {up_resp.status_code} - {up_resp.text[:100]}")
            except Exception as e:
                print(f"[{i}/{len(all_posts)}] [ID: {pid}] ❌ 업데이트 에러: {e}")

        time.sleep(0.4)

    print("\n" + "=" * 60)
    print(f"🎉 [기존 게시글 전체 이미지 업데이트 완료]")
    print(f" - 총 게시글: {len(all_posts)}개")
    print(f" - 신규 이미지/썸네일 등록 완료: {updated_count}개")
    print(f" - 기존 충족 유지: {skipped_count}개")
    print("=" * 60)

    flush_cache()


if __name__ == "__main__":
    main()
