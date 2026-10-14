# -*- coding: utf-8 -*-
"""
정치·연예·스포츠 뉴스 통합 자동 발행 실행기
- 아침/저녁 하루 2회 모든 카테고리를 순차적으로 발행
- 하나의 작업이 실패해도 다른 작업은 정상 발행되도록 예외 처리
- 발행 완료 후 WP Super Cache 자동 플러시
사용법:
  python run_all_news.py --edition morning
  python run_all_news.py --edition evening
  python run_all_news.py  (시간에 따라 자동 판별)
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

from main_politics import run_politics_pipeline
from main_entertainment import run_entertainment_pipeline
from main_sports import run_sports_pipeline

KST = timezone(timedelta(hours=9))


def flush_wp_cache():
    """WP Super Cache 플러시"""
    api = os.getenv("WP_API_URL")
    user = os.getenv("WP_USERNAME")
    pw = os.getenv("WP_PASSWORD")
    tok = base64.b64encode(f"{user}:{pw}".encode()).decode()
    hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}
    try:
        requests.post(f"{api}/plugins/wp-super-cache/wp-cache", json={"status": "active"}, headers=hdrs, timeout=10)
        print("  🧹 [WP Super Cache] 홈페이지 캐시 플러시 완료")
    except Exception as e:
        print(f"  [WARN] 캐시 플러시 오류: {e}")


def get_current_edition() -> str:
    now = datetime.now(KST)
    return "morning" if now.hour < 14 else "evening"


def run_all(edition: str = None):
    now = datetime.now(KST)
    if not edition:
        edition = get_current_edition()

    edition_kr = "아침 모닝 브리핑" if edition == "morning" else "저녁 이브닝 결산"

    print("=" * 65)
    print(f"  🚀 머니노트365 뉴스 종합 자동 발행 시작 ({edition_kr})")
    print(f"  시각: {now.strftime('%Y-%m-%d %H:%M KST')}")
    print("=" * 65)

    results = {}

    # 1. 정치 이슈
    print(f"\n[1/3] 🏛️ 정치 이슈 ({edition_kr}) 발행 시작...")
    try:
        pid, purl = run_politics_pipeline(edition=edition)
        results["정치 이슈"] = purl if purl else "발행 실패"
    except Exception as e:
        print(f"  ❌ 정치 이슈 오류 발생: {e}")
        results["정치 이슈"] = f"오류: {e}"

    # 2. 연예·엔터테인먼트
    print(f"\n[2/3] 🎬 연예·엔터테인먼트 ({edition_kr}) 발행 시작...")
    try:
        eid, eurl = run_entertainment_pipeline(edition=edition)
        results["연예·엔터"] = eurl if eurl else "발행 실패"
    except Exception as e:
        print(f"  ❌ 연예·엔터 오류 발생: {e}")
        results["연예·엔터"] = f"오류: {e}"

    # 3. 스포츠 뉴스
    print(f"\n[3/3] ⚽ 스포츠 뉴스 ({edition_kr}) 발행 시작...")
    try:
        sid, surl = run_sports_pipeline(edition=edition)
        results["스포츠 뉴스"] = surl if surl else "발행 실패"
    except Exception as e:
        print(f"  ❌ 스포츠 뉴스 오류 발생: {e}")
        results["스포츠 뉴스"] = f"오류: {e}"

    # 4. 캐시 플러시
    print("\n[4/4] 워드프레스 캐시 정리...")
    flush_wp_cache()

    print("\n" + "=" * 65)
    print(f"  📊 {edition_kr} 발행 결과 요약:")
    for k, v in results.items():
        print(f"  - {k}: {v}")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all news publishers")
    parser.add_argument("--edition", choices=["morning", "evening"], default=None,
                        help="morning or evening edition")
    args = parser.parse_args()
    run_all(edition=args.edition)
