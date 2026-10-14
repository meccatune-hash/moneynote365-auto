# -*- coding: utf-8 -*-
import os, sys, requests, base64
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

api = os.getenv("WP_API_URL")
tok = base64.b64encode(f"{os.getenv('WP_USERNAME')}:{os.getenv('WP_PASSWORD')}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}"}
r = requests.get(f"{api}/posts?categories=196&per_page=10", headers=hdrs)
if r.status_code == 200:
    posts = r.json()
    print(f"Total posts in category 196 (트렌드 이슈): {len(posts)}")
    for p in posts:
        print(f"ID: {p['id']} | Title: {p['title']['rendered']} | Link: {p['link']}")
else:
    print("Error:", r.status_code, r.text[:200])
