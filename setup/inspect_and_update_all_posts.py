# -*- coding: utf-8 -*-
"""
기존 게시글 전체 조회 및 이미지 포함 상태 점검 스크립트
"""
import os
import sys
import base64
import requests

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

WP_API_URL = os.getenv("WP_API_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")

tok = base64.b64encode(f"{WP_USERNAME}:{WP_PASSWORD}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

# 카테고리 맵핑 가져오기
r_cat = requests.get(f"{WP_API_URL}/categories?per_page=100", headers=hdrs)
cat_map = {c["id"]: c["slug"] for c in r_cat.json()} if r_cat.status_code == 200 else {}

# 모든 포스트 가져오기 (100개)
r = requests.get(f"{WP_API_URL}/posts?per_page=100&status=publish", headers=hdrs)
if r.status_code != 200:
    print(f"포스트 조회 실패: {r.status_code}")
    sys.exit(1)

posts = r.json()
print(f"사이트 전체 발행된 글: 총 {len(posts)}개\n")

need_images = []
have_images = []

for p in posts:
    pid = p["id"]
    title = p["title"]["rendered"]
    feat = p.get("featured_media", 0)
    cnt = p.get("content", {}).get("raw", p.get("content", {}).get("rendered", ""))
    img_count = cnt.count("<img")
    cat_ids = p.get("categories", [])
    cat_slugs = [cat_map.get(cid, str(cid)) for cid in cat_ids]

    if img_count < 2 or not feat:
        need_images.append((p, cat_slugs, img_count, feat))
    else:
        have_images.append((p, cat_slugs, img_count, feat))

print(f"✅ 이미 2장 이상 이미지가 있는 글: {len(have_images)}개")
print(f"⚠️ 이미지가 부족하여 업데이트 필요한 글: {len(need_images)}개\n")

for p, slugs, icnt, feat in need_images:
    print(f"  - [ID: {p['id']}] (이미지: {icnt}장, 썸네일ID: {feat}, 카테고리: {slugs}) {p['title']['rendered'][:45]}")
