# -*- coding: utf-8 -*-
"""
자동 스케줄러 - 일일 시장 보고서 및 정치·연예·스포츠 뉴스 자동 발행
- 아침: 07:00 뉴스 종합 발행(정치, 연예, 스포츠) | 08:00 시장 투자 보고서
- 저녁: 18:30 뉴스 종합 결산(정치, 연예, 스포츠)
python scheduler.py 로 백그라운드 실행
"""
import schedule
import time
import logging
from datetime import datetime

from main import run_daily_report
from run_all_news import run_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SCHEDULER] %(message)s",
    handlers=[
        logging.FileHandler("logs/scheduler.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


def job_morning_news():
    log.info("⏰ [아침 07:00] 정치·연예·스포츠 모닝 브리핑 일괄 실행 시작")
    try:
        run_all(edition="morning")
    except Exception as e:
        log.error(f"아침 뉴스 일괄 실행 오류: {e}")


def job_market_report():
    log.info("⏰ [오전 08:00] 일일 시장 투자 보고서 실행 시작")
    try:
        run_daily_report()
    except Exception as e:
        log.error(f"시장 보고서 실행 오류: {e}")


def job_evening_news():
    log.info("⏰ [저녁 18:30] 정치·연예·스포츠 이브닝 결산 일괄 실행 시작")
    try:
        run_all(edition="evening")
    except Exception as e:
        log.error(f"저녁 뉴스 일괄 실행 오류: {e}")


# ============================================================
# 스케줄 등록
# ============================================================
schedule.every().day.at("07:00").do(job_morning_news)
schedule.every().day.at("08:00").do(job_market_report)
schedule.every().day.at("18:30").do(job_evening_news)

log.info("=" * 65)
log.info("머니노트365 통합 스케줄러 시작")
log.info("  [아침] 07:00 뉴스 종합(정치/연예/스포츠) | 08:00 시장 투자보고서")
log.info("  [저녁] 18:30 뉴스 결산(정치/연예/스포츠)")
log.info("종료: Ctrl+C")
log.info("=" * 65)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(30)
