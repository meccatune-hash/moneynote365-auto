# -*- coding: utf-8 -*-
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()
api  = os.getenv("WP_API_URL")
user = os.getenv("WP_USERNAME")
pw   = os.getenv("WP_PASSWORD")
tok  = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

print("SEO 플러그인 설치 시도...")
for plugin in ["wordpress-seo", "seo-by-rank-math"]:
    r = requests.post(f"{api}/plugins", json={"slug": plugin, "status": "active"}, headers=hdrs, timeout=30)
    print(f"  {plugin}: HTTP {r.status_code}")
    if r.status_code in (200, 201):
        print(f"    설치 성공!")
        break
    else:
        print(f"    {r.text[:100]}")
