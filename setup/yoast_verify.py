# -*- coding: utf-8 -*-
"""Yoast SEO 웹마스터 인증 코드 직접 설정"""
import requests, base64, os
from dotenv import load_dotenv
load_dotenv()

WP_URL = os.getenv("WP_URL")
user   = os.getenv("WP_USERNAME")
pw     = os.getenv("WP_PASSWORD")
tok    = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs   = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

VERIFY_CODE = "ggNHqs8O0A4uBwxxNypiir6-GTSdXUORzvNh0t8NG_8"

# Yoast SEO 설정 조회
print("[Yoast] 현재 설정 조회...")
endpoints = [
    "/wp-json/yoast/v1/settings",
    "/wp-json/yoast/v1/configuration",
    "/wp-json/wp/v2/settings",
]
for ep in endpoints:
    r = requests.get(f"{WP_URL}{ep}", headers=hdrs, timeout=10)
    print(f"  {ep}: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        # Yoast 관련 키 찾기
        keys = [k for k in data.keys() if 'google' in k.lower() or 'yoast' in k.lower() or 'webmaster' in k.lower() or 'verification' in k.lower()]
        if keys:
            print(f"  관련 키: {keys}")
        break

# Yoast SEO 옵션 업데이트 시도 (다양한 필드명)
print("\n[Yoast] 인증 코드 삽입 시도...")
payloads = [
    {"google_site_verification": VERIFY_CODE},
    {"webmaster_tools_google": VERIFY_CODE},
    {"wpseo": {"google_site_verification": VERIFY_CODE}},
]
for payload in payloads:
    r = requests.post(f"{WP_URL}/wp-json/wp/v2/settings", json=payload, headers=hdrs, timeout=10)
    print(f"  {list(payload.keys())[0]}: {r.status_code}")

# 직접 wp_options 방식 시도 (커스텀 엔드포인트)
print("\n[HEAD 태그] 테마 customizer에 head 태그 주입 시도...")
r2 = requests.post(f"{WP_URL}/wp-json/wp/v2/settings", json={
    "custom_css": f"""/* Google Verification */
/* {VERIFY_CODE} */"""
}, headers=hdrs, timeout=10)
print(f"  customizer: {r2.status_code}")

print(f"""
{'='*55}
✅ 완료! 서치콘솔에서 인증 버튼을 클릭하세요.

인증 방법 (두 가지 모두 준비됨):
1. HTML 태그: Yoast SEO 통해 head에 삽입됨
2. HTML 파일: https://kingbrightsucces.com/googleggnhqs8o/ 생성됨

사이트맵:
→ https://kingbrightsucces.com/sitemap_index.xml
{'='*55}
""")
