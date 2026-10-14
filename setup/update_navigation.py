# -*- coding: utf-8 -*-
"""
WordPress FSE 네비게이션 블록(ID: 111) 및 헤더 업데이트 스크립트
카테고리별 깔끔한 정리:
- 홈
- 🏛️ 정치 이슈
- 🎬 연예·엔터
- ⚽ 스포츠
- 🌅 모닝 뉴스
- 📈 금융·투자 (드롭다운: 일일보고서, 국내주식, 미국주식, 암호화폐, 투자전략, 공부방)
- ℹ️ 소개
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

nav_content = """<!-- wp:navigation-link {"label":"🏠 홈","url":"https://kingbrightsucces.com/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"🏛️ 정치 이슈","url":"https://kingbrightsucces.com/category/politics/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"🎬 연예·엔터","url":"https://kingbrightsucces.com/category/entertainment/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"⚽ 스포츠","url":"https://kingbrightsucces.com/category/sports/","isTopLevelLink":true} /-->
<!-- wp:navigation-link {"label":"🌅 모닝 뉴스","url":"https://kingbrightsucces.com/category/morning-news/","isTopLevelLink":true} /-->
<!-- wp:navigation-submenu {"label":"📈 금융·투자","url":"https://kingbrightsucces.com/category/daily-report/","isTopLevelLink":true} -->
<!-- wp:navigation-link {"label":"📋 일일 투자 보고서","url":"https://kingbrightsucces.com/category/daily-report/"} /-->
<!-- wp:navigation-link {"label":"🇰🇷 국내 주식","url":"https://kingbrightsucces.com/category/kr-stock/"} /-->
<!-- wp:navigation-link {"label":"🇺🇸 미국 주식","url":"https://kingbrightsucces.com/category/us-stock/"} /-->
<!-- wp:navigation-link {"label":"🪙 암호화폐","url":"https://kingbrightsucces.com/category/crypto/"} /-->
<!-- wp:navigation-link {"label":"💡 투자 전략","url":"https://kingbrightsucces.com/category/investment-strategy/"} /-->
<!-- wp:navigation-link {"label":"📚 투자 공부방","url":"https://kingbrightsucces.com/category/invest-study/"} /-->
<!-- /wp:navigation-submenu -->
<!-- wp:navigation-link {"label":"ℹ️ 소개","url":"https://kingbrightsucces.com/about/","isTopLevelLink":true} /-->"""

print("Updating Navigation 111...")
r = requests.post(f"{WP_API_URL}/navigation/111", json={"content": nav_content}, headers=hdrs)
print("Status:", r.status_code)
if r.status_code == 200:
    print("Navigation 111 successfully updated!")
else:
    print("Error:", r.text[:200])

# Also check header template part to ensure it explicitly references navigation 111
print("\nEnsuring Header template part references navigation 111...")
r_hdr = requests.get(f"{WP_API_URL}/template-parts/twentytwentyfive//header?context=edit", headers=hdrs)
if r_hdr.status_code == 200:
    hdr_content = r_hdr.json().get("content", {}).get("raw", "")
    # If wp:navigation doesn't have "ref":111, let's inject it
    if '"ref":111' not in hdr_content:
        new_hdr = hdr_content.replace(
            '<!-- wp:navigation',
            '<!-- wp:navigation {"ref":111'
        ).replace(
            '<!-- wp:navigation {"ref":111 {"',
            '<!-- wp:navigation {"ref":111,'
        )
        r_up = requests.post(f"{WP_API_URL}/template-parts/twentytwentyfive//header", json={"content": new_hdr}, headers=hdrs)
        print("Header updated status:", r_up.status_code)
    else:
        print("Header already references nav 111")
