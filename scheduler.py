# -*- coding: utf-8 -*-
"""
자동 스케줄러 - 매일 오전 8시 자동 실행
python scheduler.py 로 백그라운드 실행
"""
import schedule
import time
import logging
from datetime import datetime
from main import run_daily_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SCHEDULER] %(message)s",
    handlers=[
        logging.FileHandler("logs/scheduler.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


def job():
    log.info("스케줄된 일일 보고서 실행 시작")
    try:
        run_daily_report()
    except Exception as e:
        log.error(f"보고서 실행 중 오류: {e}")


def weekly_report():
    """매주 월요일 주간 전망 보고서 (추후 구현)"""
    log.info("주간 보고서 실행 예정")


# ============================================================
# 스케줄 설정
# ============================================================
schedule.every().day.at("08:00").do(job)          # 매일 오전 8시
schedule.every().monday.at("07:00").do(weekly_report)  # 월요일 주간 전망

log.info("="*50)
log.info("머니노트365 스케줄러 시작")
log.info("매일 오전 08:00 자동 발행 예정")
log.info("종료: Ctrl+C")
log.info("="*50)

while True:
    schedule.run_pending()
    time.sleep(60)
