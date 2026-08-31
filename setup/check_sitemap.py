# -*- coding: utf-8 -*-
import requests, re

WP_URL = "https://kingbrightsucces.com"
SITEMAP = f"{WP_URL}/sitemap_index.xml"

print("[1] 사이트맵 확인...")
r = requests.get(SITEMAP, timeout=10)
print(f"  sitemap_index.xml: HTTP {r.status_code}")

total_urls = 0
sitemaps = re.findall(r"<loc>(.*?)</loc>", r.text)
for s in sitemaps:
    r2 = requests.get(s, timeout=10)
    urls = re.findall(r"<loc>(.*?)</loc>", r2.text)
    name = s.split("/")[-1]
    total_urls += len(urls)
    print(f"  {name}: {len(urls)}개 URL")

print(f"\n  총 {total_urls}개 URL 색인 대기 중")
print(f"\n[2] 사이트맵 URL:")
print(f"  {SITEMAP}")
print("\n완료!")
