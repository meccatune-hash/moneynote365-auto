import requests, os, base64, re, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from dotenv import load_dotenv
load_dotenv()
api = os.getenv("WP_API_URL")
tok = base64.b64encode(f"{os.getenv('WP_USERNAME')}:{os.getenv('WP_PASSWORD')}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}"}

r = requests.get(f"{api}/posts?categories=196&per_page=5", headers=hdrs)
for p in r.json():
    pid = p["id"]
    title = p["title"]["rendered"]
    feat = p.get("featured_media")
    cnt = p.get("content", {}).get("rendered", "")
    imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', cnt)
    print(f"[{pid}] {title}")
    print(f"  - 대표 썸네일(featured_media ID): {feat}")
    print(f"  - 본문 포함 사진 개수: {len(imgs)}장")
    for img in imgs:
        print(f"    * {img}")
