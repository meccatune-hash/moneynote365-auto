# -*- coding: utf-8 -*-
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()

api  = os.getenv("WP_API_URL")
user = os.getenv("WP_USERNAME")
pw   = os.getenv("WP_PASSWORD")
tok  = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

# 카테고리 생성
cats = [
    {"name": "모닝 뉴스", "slug": "morning-news",
     "description": "매일 오전 7시, CNN·BBC·Reuters·CNBC 글로벌 뉴스 종합 브리핑. 미국 증시 영향 분석."},
]
print("[카테고리 생성]")
for c in cats:
    r = requests.post(f"{api}/categories", json=c, headers=hdrs, timeout=10)
    d = r.json()
    if r.status_code == 201:
        print(f"  ✅ [{c['name']}] ID:{d['id']} 생성 완료")
    elif r.status_code == 422:
        print(f"  ℹ️  [{c['name']}] 이미 존재")
    else:
        print(f"  ❌ {r.status_code}: {r.text[:80]}")

# 태그 생성
print("\n[태그 생성]")
tags = ["글로벌뉴스", "미국증시", "cnn", "bbc", "reuters",
        "모닝브리핑", "경제뉴스", "투자뉴스", "cnbc", "marketwatch",
        "새벽뉴스", "월스트리트", "주식뉴스"]
for t in tags:
    r = requests.post(f"{api}/tags", json={"name": t, "slug": t}, headers=hdrs, timeout=10)
    if r.status_code == 201:
        print(f"  ✅ [{t}]")
    elif r.status_code == 422:
        print(f"  ℹ️  [{t}] 이미 있음")

print("\n완료!")
