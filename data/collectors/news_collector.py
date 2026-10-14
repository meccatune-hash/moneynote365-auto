# -*- coding: utf-8 -*-
"""
글로벌 주요 뉴스 RSS 수집기
- CNN Business, BBC Business, Reuters, CNBC, MarketWatch, AP News
- 미국 증시에 영향을 줄 뉴스 위주로 수집
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

NEWS_FEEDS = {
    "CNN Business": "https://rss.cnn.com/rss/money_news_international.rss",
    "BBC Business":  "https://feeds.bbci.co.uk/news/business/rss.xml",
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "CNBC Top News": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "MarketWatch":   "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "AP Business":   "https://rsshub.app/apnews/topics/business",
    "BBC World":     "https://feeds.bbci.co.uk/news/world/rss.xml",
    "Reuters World": "https://feeds.reuters.com/Reuters/worldNews",
}

FALLBACK_FEEDS = {
    "CNN Business":  "http://rss.cnn.com/rss/money_news_international.rss",
    "BBC Business":  "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/business/rss.xml",
    "CNBC Economy":  "https://www.cnbc.com/id/20910258/device/rss/rss.html",
    "Investing.com": "https://www.investing.com/rss/news_25.rss",
}


def _fetch_rss(url: str, timeout: int = 10) -> list:
    """RSS 피드에서 뉴스 항목 파싱"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        }
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()

        root = ET.fromstring(r.content)

        # RSS 2.0 또는 Atom 형식 처리
        items = []
        # RSS 2.0
        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            raw_desc = item.findtext("description", "").strip()
            link  = item.findtext("link", "").strip()
            pub   = item.findtext("pubDate", "").strip()

            image_url = ""
            enc = item.find("enclosure")
            if enc is not None and "image" in enc.attrib.get("type", ""):
                image_url = enc.attrib.get("url", "")
            if not image_url:
                import re
                m = re.search(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', raw_desc)
                if m:
                    image_url = m.group(1)
            if not image_url:
                for el in item:
                    if "media" in el.tag.lower() and el.attrib.get("url"):
                        image_url = el.attrib.get("url")
                        break

            if title:
                import re
                desc = re.sub(r'<[^>]+>', '', raw_desc)[:300]
                items.append({
                    "title":     title,
                    "desc":      desc,
                    "link":      link,
                    "pubDate":   pub,
                    "image_url": image_url,
                })

        # Atom 형식
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall(".//atom:entry", ns):
            title = entry.findtext("atom:title", "", ns).strip()
            desc  = entry.findtext("atom:summary", "", ns).strip()
            link_el = entry.find("atom:link", ns)
            link  = link_el.get("href", "") if link_el is not None else ""
            pub   = entry.findtext("atom:published", "", ns).strip()

            if title:
                import re
                desc = re.sub(r'<[^>]+>', '', desc)[:300]
                items.append({
                    "title":   title,
                    "desc":    desc,
                    "link":    link,
                    "pubDate": pub,
                })

        return items[:15]  # 최신 15개만

    except Exception as e:
        return []


def collect_news() -> dict:
    """모든 주요 뉴스 피드 수집"""
    print("📰 글로벌 뉴스 수집 중...")
    all_news  = {}
    all_items = []

    # 주요 피드 수집
    for source, url in NEWS_FEEDS.items():
        items = _fetch_rss(url)
        if not items:
            # 폴백 시도
            fallback_url = FALLBACK_FEEDS.get(source)
            if fallback_url:
                items = _fetch_rss(fallback_url)

        if items:
            all_news[source] = items
            all_items.extend([{**i, "source": source} for i in items])
            print(f"  ✅ {source}: {len(items)}개")
        else:
            print(f"  ⚠️  {source}: 수집 실패")

    # 중복 제거 (제목 유사성)
    seen_titles = set()
    unique_items = []
    for item in all_items:
        title_key = item["title"][:50].lower()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_items.append(item)

    now_kst = datetime.now(KST)
    print(f"  📊 총 {len(unique_items)}개 고유 뉴스 수집 완료")

    return {
        "by_source":  all_news,
        "all_items":  unique_items,
        "collected_at": now_kst.strftime("%Y-%m-%d %H:%M KST"),
        "total_count": len(unique_items),
    }


if __name__ == "__main__":
    result = collect_news()
    print(f"\n수집된 뉴스 {result['total_count']}개:")
    for item in result["all_items"][:20]:
        print(f"  [{item['source']}] {item['title'][:70]}")
