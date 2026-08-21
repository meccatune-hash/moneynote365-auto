# -*- coding: utf-8 -*-
import requests, os
from dotenv import load_dotenv
load_dotenv()

token   = os.getenv("GITHUB_TOKEN")
user    = os.getenv("GITHUB_USERNAME")
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

r = requests.get(
    f"https://api.github.com/repos/{user}/moneynote365-auto/actions/runs?per_page=5",
    headers=headers, timeout=10
)
if r.status_code == 200:
    runs = r.json().get("workflow_runs", [])
    if runs:
        for run in runs:
            print(f"{run['created_at']}  상태:{run['status']}  결과:{run['conclusion']}  이름:{run['name']}")
    else:
        print("실행 기록 없음 - GitHub Actions가 한 번도 실행되지 않았음")
else:
    print(f"조회 실패: {r.status_code}")
