# -*- coding: utf-8 -*-
import requests, re

print("구글 인증 메타태그 확인 중...")
r = requests.get("https://kingbrightsucces.com", timeout=10)
head = r.text[:5000]

VERIFY = "ggNHqs8O0A4uBwxxNypiir6-GTSdXUORzvNh0t8NG_8"

if "google-site-verification" in head.lower():
    tag = re.search(r'<meta[^>]*google-site-verification[^>]*>', head, re.IGNORECASE)
    print("✅ 구글 인증 메타태그 발견!")
    if tag:
        print(f"태그 내용: {tag.group()}")
    if VERIFY in head:
        print("✅ 인증 코드 일치 확인!")
    else:
        print("⚠️  다른 인증 코드가 있습니다 (코드 불일치)")
else:
    print("❌ 구글 인증 메타태그 없음 — 아직 설정 안 됨")
    print("\n현재 head에 있는 meta 태그들:")
    metas = re.findall(r'<meta[^>]+>', head, re.IGNORECASE)
    for m in metas:
        print(f"  {m[:120]}")
