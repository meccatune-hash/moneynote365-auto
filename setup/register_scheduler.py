# -*- coding: utf-8 -*-
"""
Windows Task Scheduler 등록 스크립트
매일 오전 08:00 자동 실행 등록
"""
import sys, io, os, subprocess

TASK_NAME = "MN365-DailyReport"
BAT_PATH = os.path.abspath("run_daily.bat")
HOUR = "08"
MINUTE = "00"

cmd = [
    "schtasks", "/Create", "/F",
    "/TN", TASK_NAME,
    "/TR", BAT_PATH,
    "/SC", "DAILY",
    "/ST", f"{HOUR}:{MINUTE}",
    "/RL", "HIGHEST",
]

result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
if result.returncode == 0:
    print(f"[OK] Windows 작업 스케줄러 등록 완료!")
    print(f"     작업명: {TASK_NAME}")
    print(f"     실행시간: 매일 오전 {HOUR}:{MINUTE}")
    print(f"     파일: {BAT_PATH}")
    print(f"\n  확인 방법:")
    print(f"  - 작업 스케줄러 열기: taskschd.msc")
    print(f"  - 또는 실행: schtasks /Query /TN {TASK_NAME}")
else:
    print(f"[FAIL] 등록 실패: {result.stderr}")
    print(f"\n  수동 등록 방법:")
    print(f"  1. Win + R → taskschd.msc 실행")
    print(f"  2. '기본 작업 만들기' 클릭")
    print(f"  3. 매일 오전 08:00 설정")
    print(f"  4. 프로그램: {BAT_PATH}")
