# -*- coding: utf-8 -*-
"""
자동 스케줄러 - 일일 시장 보고서 및 연예·스포츠 뉴스 자동 발행
- 연예 뉴스: 매일 오전 07:30 / 오후 18:30
- 스포츠 뉴스: 매일 오전 07:45 / 오후 18:45
- 시장 보고서: 매일 오전 08:00
python scheduler.py 로 백그라운드 실행
"""
import schedule
import time
import logging
from datetime import datetime

from main import run_daily_report
from main_entertainment import run_entertainment_pipeline
from main_sports import run_sports_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SCHEDULER] %(message)s",
    handlers=[
        logging.FileHandler("logs/scheduler.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


def job_market_report():
    log.info("스케줄된 일일 시장 투자 보고서 실행 시작")
    try:
        run_daily_report()
    except Exception as e:
        log.error(f"시장 보고서 실행 중 오류: {e}")


def job_entertainment_morning():
    log.info("스케줄된 [아침 모닝] 연예 뉴스 브리핑 실행")
    try:
        run_entertainment_pipeline(edition="morning")
    except Exception as e:
        log.error(f"연예 뉴스(모닝) 실행 오류: {e}")


def job_entertainment_evening():
    log.info("스케줄된 [저녁 이브닝] 연예 뉴스 결산 실행")
    try:
        run_entertainment_pipeline(edition="evening")
    except Exception as e:
        log.error(f"연예 뉴스(이브닝) 실행 오류: {e}")


def job_sports_morning():
    log.info("스케줄된 [아침 모닝] 스포츠 뉴스 브리핑 실행")
    try:
        run_sports_pipeline(edition="morning")
    except Exception as e:
        log.error(f"스포츠 뉴스(모닝) 실행 오류: {e}")


def job_sports_evening():
    log.info("스케줄된 [저녁 이브닝] 스포츠 뉴스 결산 실행")
    try:
        run_sports_pipeline(edition="evening")
    except Exception as e:
        log.error(f"스포츠 뉴스(이브닝) 실행 오류: {e}")


# ============================================================
# 스케줄 등록 (하루 2회 아침 / 저녁)
# ============================================================
# 아침 발행
schedule.every().day.at("07:30").do(job_entertainment_morning)
schedule.every().day.at("07:45").do(job_sports_morning)
schedule.every().day.at("08:00").do(job_market_report)

# 저녁 발행
schedule.every().day.at("18:30").do(job_entertainment_evening)
schedule.every().day.at("18:45").do(job_sports_evening)

log.info("=" * 60)
log.info("머니노트365 자동 통합 스케줄러 시작")
log.info("  [아침] 07:30 연예 뉴스 | 07:45 스포츠 뉴스 | 08:00 시장 보고서")
log.info("  [저녁] 18:30 연예 뉴스 | 18:45 스포츠 뉴스")
log.info("종료: Ctrl+C")
log.info("=" * 60)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(30)
