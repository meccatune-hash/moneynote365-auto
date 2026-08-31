# -*- coding: utf-8 -*-
"""GitHub Actions 실행 기록 확인"""
import requests, os
from dotenv import load_dotenv
load_dotenv()

OWNER = "meccatune-hash"
REPO  = "moneynote365-auto"
TOKEN = os.getenv("GITHUB_TOKEN")
hdrs  = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}

print("="*60)
print("  GitHub Actions 실행 기록 확인")
print("="*60)

# 모든 워크플로우 실행 기록
r = requests.get(
    f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs?per_page=20",
    headers=hdrs, timeout=10
)
runs = r.json().get("workflow_runs", [])

print(f"\n최근 20개 실행 기록:")
for run in runs:
    name   = run["name"]
    status = run["status"]
    concl  = run.get("conclusion", "running")
    dt     = run["created_at"][:16].replace("T", " ")
    event  = run["event"]
    mark   = "✅" if concl == "success" else ("🔄" if status == "in_progress" else "❌")
    print(f"  {mark} [{dt}] {name} | {event} | {concl}")
