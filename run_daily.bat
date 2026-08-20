@echo off
chcp 65001 >nul
cd /d "C:\Users\mecca\.gemini\antigravity\scratch\moneynote365-auto"
python -X utf8 main.py >> logs\cron.log 2>&1
