# -*- coding: utf-8 -*-
import requests, base64, os
from dotenv import load_dotenv

load_dotenv()

api  = os.getenv("WP_API_URL")
user = os.getenv("WP_USERNAME")
pw   = os.getenv("WP_PASSWORD")
tok  = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

# 1. Update header template part
r_hdr = requests.get(f"{api}/template-parts/twentytwentyfive//header?context=edit", headers=hdrs)
hdr_raw = r_hdr.json().get("content", {}).get("raw", "")
print("Current header contains ref:111?", "ref\":111" in hdr_raw or "ref\": 111" in hdr_raw)

if "ref\":111" not in hdr_raw:
    # Replace <!-- wp:navigation /--> with <!-- wp:navigation {"ref":111} /-->
    new_hdr = hdr_raw.replace("<!-- wp:navigation /-->", '<!-- wp:navigation {"ref":111} /-->')
    r_post = requests.post(f"{api}/template-parts/twentytwentyfive//header", json={"content": new_hdr}, headers=hdrs)
    print("Header update status:", r_post.status_code)

# 2. Check active plugins
r_plugins = requests.get(f"{api}/plugins", headers=hdrs)
if r_plugins.status_code == 200:
    for p in r_plugins.json():
        if p.get("status") == "active":
            print("Active plugin:", p.get("plugin"), p.get("name"))
