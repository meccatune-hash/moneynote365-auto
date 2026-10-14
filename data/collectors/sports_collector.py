# -*- coding: utf-8 -*-
"""
스포츠 뉴스 RSS 수집기
- 구글 뉴스 스포츠 섹션, 축구/야구 핫이슈 검색
- 연합뉴스 스포츠, 동아일보 스포츠, JTBC 스포츠
- 국내외 축구(손흥민/이강인/EPL), 야구(KBO/MLB), 골프, 농구, 배구 등 종합 스포츠 수집
"""
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

KST = timezone(timedelta(hours=9))

SPORTS_FEEDS = {
    "구글 스포츠 헤드라인": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=ko&gl=KR&ceid=KR:ko",
    "구글 축구·해외파 핫이슈": "https://news.google.com/rss/search?q=%ED%95%B4%EC%99%B8%EC%B6%95%EA%B5%AC+%EC%86%90%ED%9D%A5%EB%AF%BC+%EC%9D%B4%EA%B0%95%EC%9D%B8&hl=ko&gl=KR&ceid=KR:ko",
    "구글 야구·KBO·MLB":    "https://news.google.com/rss/search?q=KBO+%ED%94%84%EB%A1%9C%EC%95%BC%EA%B5%AC+MLB&hl=ko&gl=KR&ceid=KR:ko",
    "SBS 스포츠":            "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=09&plink=RSSREADER",
    "연합뉴스 스포츠":        "https://www.yna.co.kr/rss/sports.xml",
    "동아일보 스포츠":        "https://rss.donga.com/sports.xml",
    "JTBC 스포츠":           "https://fs.jtbc.co.kr/RSS/sports.xml",
}


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&#39;', "'", text)
    return text.strip()


def _parse_pub_date(pub_str: str):
    if not pub_str:
        return None
    try:
        return parsedate_to_datetime(pub_str)
    except Exception:
        return None


def _fetch_rss(url: str, timeout: int = 10) -> list:
    """RSS 피드 파싱"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        }
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()

        root = ET.fromstring(r.content)
        items = []

        # RSS 2.0
        for item in root.findall(".//item"):
            title = _clean_text(item.findtext("title", ""))
            raw_desc = item.findtext("description", "")
            desc  = _clean_text(raw_desc)[:300]
            link  = item.findtext("link", "").strip()
            pub   = item.findtext("pubDate", "").strip()
            dt    = _parse_pub_date(pub)

            # 이미지 URL 추출
            image_url = ""
            enc = item.find("enclosure")
            if enc is not None and "image" in enc.attrib.get("type", ""):
                image_url = enc.attrib.get("url", "")
            if not image_url:
                m = re.search(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', raw_desc)
                if m:
                    image_url = m.group(1)
            if not image_url:
                for el in item:
                    if "media" in el.tag.lower() and el.attrib.get("url"):
                        image_url = el.attrib.get("url")
                        break

            if title:
                items.append({
                    "title":     title,
                    "desc":      desc,
                    "link":      link,
                    "pubDate":   pub,
                    "timestamp": dt.timestamp() if dt else 0,
                    "image_url": image_url,
                })

        # Atom 형식
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall(".//atom:entry", ns):
            title = _clean_text(entry.findtext("atom:title", "", ns))
            desc  = _clean_text(entry.findtext("atom:summary", "", ns))[:300]
            link_el = entry.find("atom:link", ns)
            link  = link_el.get("href", "") if link_el is not None else ""
            pub   = entry.findtext("atom:published", "", ns).strip()
            dt    = _parse_pub_date(pub)

            if title:
                items.append({
                    "title":     title,
                    "desc":      desc,
                    "link":      link,
                    "pubDate":   pub,
                    "timestamp": dt.timestamp() if dt else 0,
                })

        return items[:25]
    except Exception as e:
        return []


def collect_sports_news() -> dict:
    """스포츠 뉴스 피드 종합 수집"""
    print("⚽ 스포츠 뉴스 수집 중...")
    by_source = {}
    all_items = []

    for source, url in SPORTS_FEEDS.items():
        items = _fetch_rss(url)
        if items:
            by_source[source] = items
            for item in items:
                all_items.append({**item, "source": source})
            print(f"  ✅ {source}: {len(items)}개")
        else:
            print(f"  ⚠️  {source}: 수집 실패 또는 0개")

    # 제목 유사도 기준 중복 제거
    seen_titles = set()
    unique_items = []
    for item in all_items:
        normalized = re.sub(r'[\s\W]+', '', item["title"][:40].lower())
        if normalized not in seen_titles:
            seen_titles.add(normalized)
            unique_items.append(item)

    # 최신순 정렬
    unique_items.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    now_kst = datetime.now(KST)
    print(f"  📊 총 {len(unique_items)}개 고유 스포츠 뉴스 수집 완료")

    return {
        "by_source":    by_source,
        "all_items":    unique_items,
        "collected_at": now_kst.strftime("%Y-%m-%d %H:%M KST"),
        "total_count":  len(unique_items),
    }


if __name__ == "__main__":
    res = collect_sports_news()
    print(f"\n수집 완료: {res['total_count']}건")
    for it in res["all_items"][:10]:
        print(f"- [{it['source']}] {it['title']}")
