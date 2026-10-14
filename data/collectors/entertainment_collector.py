# -*- coding: utf-8 -*-
"""
연예·엔터테인먼트 뉴스 RSS 수집기
- 구글 뉴스 연예 섹션 & 핫이슈 검색
- 연합뉴스 연예, 동아일보 연예, JTBC 연예
- 국내외 K-POP, 드라마, 예능, 영화, 스타 핫이슈 수집
"""
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

KST = timezone(timedelta(hours=9))

ENTERTAINMENT_FEEDS = {
    "구글 연예 헤드라인": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=ko&gl=KR&ceid=KR:ko",
    "구글 연예 핫이슈":   "https://news.google.com/rss/search?q=%EC%97%B0%EC%98%88%EA%B3%84+%ED%95%AB%EC%9D%B4%EC%8A%88&hl=ko&gl=KR&ceid=KR:ko",
    "SBS 연예":          "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=04&plink=RSSREADER",
    "연합뉴스 연예":      "https://www.yna.co.kr/rss/entertainment.xml",
    "동아일보 연예":      "https://rss.donga.com/entertainment.xml",
    "JTBC 연예":         "https://fs.jtbc.co.kr/RSS/entertainment.xml",
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


def collect_entertainment_news() -> dict:
    """연예계 뉴스 피드 종합 수집"""
    print("🎬 연예·엔터테인먼트 뉴스 수집 중...")
    by_source = {}
    all_items = []

    for source, url in ENTERTAINMENT_FEEDS.items():
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
        # 주요 키워드 추출용 정규화
        normalized = re.sub(r'[\s\W]+', '', item["title"][:40].lower())
        if normalized not in seen_titles:
            seen_titles.add(normalized)
            unique_items.append(item)

    # 최신순 정렬
    unique_items.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    now_kst = datetime.now(KST)
    print(f"  📊 총 {len(unique_items)}개 고유 연예 뉴스 수집 완료")

    return {
        "by_source":    by_source,
        "all_items":    unique_items,
        "collected_at": now_kst.strftime("%Y-%m-%d %H:%M KST"),
        "total_count":  len(unique_items),
    }


if __name__ == "__main__":
    res = collect_entertainment_news()
    print(f"\n수집 완료: {res['total_count']}건")
    for it in res["all_items"][:10]:
        print(f"- [{it['source']}] {it['title']}")
