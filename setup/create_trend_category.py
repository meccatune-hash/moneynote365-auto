# -*- coding: utf-8 -*-
"""
트렌드 이슈 카테고리 생성 및 확인 스크립트
"""
import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

WP_API_URL = os.getenv("WP_API_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")

tok = base64.b64encode(f"{WP_USERNAME}:{WP_PASSWORD}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

r = requests.get(f"{WP_API_URL}/categories?slug=trend-issues", headers=hdrs)
if r.status_code == 200 and r.json():
    cat = r.json()[0]
    print(f"Category already exists: ID={cat['id']}, Name={cat['name']}, Slug={cat['slug']}")
else:
    r2 = requests.post(f"{WP_API_URL}/categories", headers=hdrs, json={
        "name": "트렌드 이슈",
        "slug": "trend-issues",
        "description": "실시간 대한민국 최신 급상승 트렌드, 가장 조회율이 높고 화제가 되는 핫이슈 심층 분석"
    })
    if r2.status_code in (200, 201):
        cat = r2.json()
        print(f"Category created successfully: ID={cat['id']}, Name={cat['name']}, Slug={cat['slug']}")
    else:
        print(f"Failed to create category: {r2.status_code} {r2.text}")
