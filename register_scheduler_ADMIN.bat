@echo off
chcp 65001 >nul
echo ============================================
echo   머니노트365 매일 자동 실행 등록
echo   [반드시 관리자로 실행하세요]
echo ============================================
echo.

:: 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [오류] 관리자 권한이 필요합니다!
    echo.
    echo 이 파일을 우클릭 후 [관리자로 실행]을 선택하세요.
    pause
    exit /b 1
)

:: 작업 등록
schtasks /Create /F ^
    /TN "MN365-DailyReport" ^
    /TR "C:\Users\mecca\.gemini\antigravity\scratch\moneynote365-auto\run_daily.bat" ^
    /SC DAILY ^
    /ST "08:00" ^
    /RL HIGHEST

if %ERRORLEVEL% == 0 (
    echo.
    echo [성공] 매일 오전 08:00 자동 실행 등록 완료!
    echo.
    echo 등록된 작업 확인:
    schtasks /Query /TN "MN365-DailyReport" /FO LIST
) else (
    echo.
    echo [실패] 아래 방법으로 수동 등록하세요:
    echo   1. Win+R 키 누르기
    echo   2. taskschd.msc 입력 후 엔터
    echo   3. 기본 작업 만들기 클릭
    echo   4. 이름: MN365-DailyReport
    echo   5. 매일 오전 08:00 설정
    echo   6. 프로그램: C:\Users\mecca\.gemini\antigravity\scratch\moneynote365-auto\run_daily.bat
)
echo.
pause
