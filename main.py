# -*- coding: utf-8 -*-
"""
머니노트365 메인 실행 파일 v3
python -X utf8 main.py
"""
import os, sys, json, logging
from datetime import datetime

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.collectors.us_market import collect_us_market
from data.collectors.kr_market import collect_kr_market
from data.collectors.crypto    import collect_crypto
from report.generator          import generate_daily_report, generate_title, generate_excerpt
from publisher.wp_publisher    import publish_post
from publisher.image_fetcher   import get_all_media_html

os.makedirs("logs", exist_ok=True)
os.makedirs("logs/data", exist_ok=True)

# 로그: 파일만 사용 (stdout 충돌 방지)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("logs/daily.log", encoding="utf-8")]
)
log = logging.getLogger(__name__)


def pprint(msg):
    """안전한 출력 (파일 로그 + 콘솔)"""
    try:
        print(msg)
    except Exception:
        pass
    try:
        log.info(msg)
    except Exception:
        pass


def get_id_by_slug(endpoint, slug):
    import requests, base64
    from dotenv import load_dotenv
    load_dotenv()
    api = os.getenv("WP_API_URL")
    tok = base64.b64encode(f"{os.getenv('WP_USERNAME')}:{os.getenv('WP_PASSWORD')}".encode()).decode()
    r = requests.get(f"{api}/{endpoint}?slug={slug}",
                     headers={"Authorization": f"Basic {tok}"}, timeout=10)
    if r.status_code == 200 and r.json():
        return r.json()[0]["id"]
    return None


def get_tag_ids(slugs):
    import requests, base64
    from dotenv import load_dotenv
    load_dotenv()
    api = os.getenv("WP_API_URL")
    tok = base64.b64encode(f"{os.getenv('WP_USERNAME')}:{os.getenv('WP_PASSWORD')}".encode()).decode()
    ids = []
    for slug in slugs:
        r = requests.get(f"{api}/tags?slug={slug}",
                         headers={"Authorization": f"Basic {tok}"}, timeout=10)
        if r.status_code == 200 and r.json():
            ids.append(r.json()[0]["id"])
    return ids


def run_daily_report():
    start = datetime.now()
    pprint("=" * 55)
    pprint("  머니노트365 일일 보고서 파이프라인 시작")
    pprint("=" * 55)

    # Step 1: 시장 데이터 수집
    pprint("\n[Step 1] 시장 데이터 수집")
    us_data     = collect_us_market()
    kr_data     = collect_kr_market()
    crypto_data = collect_crypto()

    today_str = datetime.now().strftime("%Y%m%d")
    with open(f"logs/data/{today_str}_market.json", "w", encoding="utf-8") as f:
        json.dump({"us": us_data, "kr": kr_data, "crypto": crypto_data},
                  f, ensure_ascii=False, indent=2, default=str)

    # Step 2: 미디어 (이미지 + 차트) 수집
    pprint("\n[Step 2] 이미지 & 차트 수집")
    try:
        media_html = get_all_media_html()
        pprint(f"  [OK] 미디어 {len(media_html)}개 준비 완료")
    except Exception as e:
        pprint(f"  [WARN] 미디어 수집 오류: {e}")
        media_html = {}

    # Step 3: AI 상세 보고서 생성
    pprint("\n[Step 3] AI 상세 투자 보고서 생성")
    content = generate_daily_report(us_data, kr_data, crypto_data, media_html)
    title   = generate_title(us_data, kr_data, crypto_data)
    excerpt = generate_excerpt(us_data, kr_data, crypto_data)
    pprint(f"  [OK] 보고서 생성: {len(content):,}자")

    # Step 4: WordPress 발행
    pprint("\n[Step 4] WordPress 발행")
    cat_id  = get_id_by_slug("categories", "daily-report")
    tag_ids = get_tag_ids(["kospi", "sp500", "bitcoin", "vix", "fomc"])

    post_id, post_url = publish_post(
        title=title,
        content=content,
        category_ids=[cat_id] if cat_id else [],
        tag_ids=tag_ids,
        excerpt=excerpt,
        status="publish",
    )

    elapsed = (datetime.now() - start).seconds
    if post_id:
        pprint(f"\n[완료] {elapsed}초 소요")
        pprint(f"  제목: {title}")
        pprint(f"  URL:  {post_url}")
    else:
        pprint("\n[실패] 발행 오류")

    return post_id, post_url


if __name__ == "__main__":
    run_daily_report()
