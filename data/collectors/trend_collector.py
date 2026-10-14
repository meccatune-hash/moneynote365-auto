# -*- coding: utf-8 -*-
"""
실시간 트렌드 & 급상승 검색어 수집 모듈 (data/collectors/trend_collector.py)
- Google Trends 대한민국 실시간 급상승 검색어 RSS 파싱
- 검색량(approx_traffic) 기준 최고 조회율/인기 순 정렬
- 키워드별 구글 뉴스 실시간 기사 수집 및 교차 검증
- 유사 키워드 중복 제거 및 상위 5개 핵심 트렌드 선별
"""
import re
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import requests

KST = timezone(timedelta(hours=9))

GOOGLE_TRENDS_URLS = [
    "https://trends.google.co.kr/trending/rss?geo=KR",
    "https://trends.google.com/trending/rss?geo=KR",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
}


def _parse_traffic(traffic_str: str) -> int:
    """검색량 문자열(예: '1000+', '50K+', '200+')을 숫자로 변환하여 정렬용 정수 반환"""
    if not traffic_str:
        return 0
    clean = traffic_str.replace("+", "").replace(",", "").strip().upper()
    try:
        if "K" in clean:
            val = float(clean.replace("K", "")) * 1000
            return int(val)
        elif "M" in clean:
            val = float(clean.replace("M", "")) * 1000000
            return int(val)
        else:
            return int(clean)
    except Exception:
        return 0


def fetch_google_trends() -> list:
    """구글 트렌드 RSS에서 실시간 검색어 및 관련 뉴스 추출"""
    for url in GOOGLE_TRENDS_URLS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12)
            if resp.status_code != 200:
                continue

            root = ET.fromstring(resp.content)
            ns = {
                "ht": "https://trends.google.com/trending/rss"
            }

            items = root.findall("./channel/item")
            if not items:
                continue

            trends = []
            for item in items:
                title_elem = item.find("title")
                keyword = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                if not keyword:
                    continue

                traffic_elem = item.find("ht:approx_traffic", ns)
                traffic_str = traffic_elem.text.strip() if traffic_elem is not None and traffic_elem.text else "100+"
                traffic_score = _parse_traffic(traffic_str)

                pub_elem = item.find("pubDate")
                pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""

                news_items = []
                for n_elem in item.findall("ht:news_item", ns):
                    n_title = n_elem.find("ht:news_item_title", ns)
                    n_snippet = n_elem.find("ht:news_item_snippet", ns)
                    n_url = n_elem.find("ht:news_item_url", ns)
                    n_source = n_elem.find("ht:news_item_source", ns)

                    news_items.append({
                        "title": n_title.text.strip() if n_title is not None and n_title.text else "",
                        "snippet": n_snippet.text.strip() if n_snippet is not None and n_snippet.text else "",
                        "url": n_url.text.strip() if n_url is not None and n_url.text else "",
                        "source": n_source.text.strip() if n_source is not None and n_source.text else "언론사"
                    })

                trends.append({
                    "keyword": keyword,
                    "traffic_str": traffic_str,
                    "traffic_score": traffic_score,
                    "pub_date": pub_date,
                    "news_items": news_items
                })

            if trends:
                return trends
        except Exception as e:
            print(f"  [WARN] Google Trends ({url}) 수집 오류: {e}")

    return []


def fetch_news_for_keyword(keyword: str, max_count: int = 5) -> list:
    """키워드에 대한 최신 구글 뉴스 심층 검색 (배경 맥락 및 추가 팩트 확보)"""
    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://news.google.com/rss/search?q={encoded_kw}&hl=ko&gl=KR&ceid=KR:ko"
    articles = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            for it in root.findall("./channel/item")[:max_count]:
                t_elem = it.find("title")
                d_elem = it.find("description")
                s_elem = it.find("source")
                title = t_elem.text.strip() if t_elem is not None and t_elem.text else ""
                desc = d_elem.text.strip() if d_elem is not None and d_elem.text else ""
                source = s_elem.text.strip() if s_elem is not None and s_elem.text else "뉴스"

                # 태그 제거
                desc = re.sub(r"<[^>]+>", "", desc).strip()

                if title:
                    articles.append({
                        "title": title,
                        "desc": desc,
                        "source": source
                    })
    except Exception as e:
        print(f"  [WARN] {keyword} 뉴스 추가 수집 오류: {e}")

    return articles


def are_keywords_similar(kw1: str, kw2: str) -> bool:
    """두 키워드가 실질적으로 동일한 주제인지 판별 (예: kbo vs 크보 vs 포스트시즌 일정)"""
    k1 = kw1.lower().replace(" ", "")
    k2 = kw2.lower().replace(" ", "")
    if k1 == k2 or k1 in k2 or k2 in k1:
        return True

    # 야구/스포츠 관련 키워드 군
    baseball_terms = ["kbo", "크보", "야구", "포스트시즌", "준플레이오프", "플레이오프", "한국시리즈", "프로야구"]
    k1_is_bb = any(b in k1 for b in baseball_terms)
    k2_is_bb = any(b in k2 for b in baseball_terms)
    if k1_is_bb and k2_is_bb:
        return True

    # 축구 관련 키워드 군
    football_terms = ["손흥민", "이강인", "토트넘", "epl", "챔피언스리그", "히샬리송", "뮌헨", "김민재"]
    k1_is_fb = any(f in k1 for f in football_terms)
    k2_is_fb = any(f in k2 for f in football_terms)
    if k1_is_fb and k2_is_fb:
        return True

    return False


def collect_top_trends(count: int = 5) -> list:
    """
    실시간 검색량/조회율이 가장 높은 상위 트렌드 토픽 선별
    - 트렌드 수집 및 검색량 순 정렬
    - 중복 유사 키워드 필터링
    - 키워드별 심층 뉴스 결합
    """
    raw_trends = fetch_google_trends()
    if not raw_trends:
        print("  [WARN] 구글 트렌드 수집 실패, 기본 트렌드 키워드로 대체")
        fallback_keywords = ["국내 증시 핫이슈", "실시간 환율 전망", "인공지능 AI 트렌드", "국내 경제 동향", "글로벌 테크 이슈"]
        raw_trends = [
            {"keyword": kw, "traffic_str": "1000+", "traffic_score": 1000, "news_items": []}
            for kw in fallback_keywords
        ]

    # 검색량 점수 높은 순 정렬 (내림차순)
    raw_trends.sort(key=lambda x: x.get("traffic_score", 0), reverse=True)

    selected_trends = []
    for item in raw_trends:
        kw = item["keyword"]
        # 기존 선택된 키워드와 유사한지 체크
        if any(are_keywords_similar(kw, sel["keyword"]) for sel in selected_trends):
            continue

        # 추가 뉴스 보강
        extra_news = fetch_news_for_keyword(kw, max_count=5)
        # 구글 트렌드의 news_items와 extra_news 결합
        combined_news = []
        seen_titles = set()
        for n in item.get("news_items", []):
            if n["title"] and n["title"] not in seen_titles:
                seen_titles.add(n["title"])
                combined_news.append(n)
        for n in extra_news:
            if n["title"] and n["title"] not in seen_titles:
                seen_titles.add(n["title"])
                combined_news.append(n)

        item["all_news"] = combined_news
        selected_trends.append(item)

        if len(selected_trends) >= count:
            break

    print(f"  [수집 완료] 상위 트렌드 {len(selected_trends)}건 선정")
    for idx, t in enumerate(selected_trends, 1):
        print(f"    {idx}. [{t['keyword']}] 예상 검색량: {t['traffic_str']} | 관련 뉴스 {len(t['all_news'])}건")

    return selected_trends


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    trends = collect_top_trends(5)
