# -*- coding: utf-8 -*-
"""
전체 자동 발행 포스팅 통합 이미지 관리 모듈 (publisher/image_manager.py)
- 모든 카테고리(정치, 연예, 스포츠, 모닝뉴스, 트렌드, 일일투자보고서, 주식, 코인 등)에
  자동으로 연관성 높은 고품질 이미지 2~3장 수집, 워드프레스 미디어 라이브러리 업로드 및 본문/썸네일 자동 삽입
"""
import os
import re
import sys
import time
import requests
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()

from publisher.wp_publisher import upload_image

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
}

# 카테고리별 검증된 고화질 로열티 프리 기본 이미지 풀 (기사 내 실시간 사진 부재 시 안정적 폴백)
CATEGORY_FALLBACK_IMAGES = {
    "politics": [
        {"url": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=800&q=80", "caption": "대한민국 국회 및 주요 정책 회의 현장", "source": "정치 현장 자료"},
        {"url": "https://images.unsplash.com/photo-1575320181282-9afab399332c?w=800&q=80", "caption": "정부 주요 부처 및 공공 정책 브리핑", "source": "정책 보도 자료"},
        {"url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&q=80", "caption": "원내 법안 심사 및 사법·입법 주요 현안", "source": "국회 현장 자료"},
    ],
    "entertainment": [
        {"url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&q=80", "caption": "K-POP 및 글로벌 라이브 콘서트 현장", "source": "연예가 보도자료"},
        {"url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&q=80", "caption": "화제의 방송 프로그램 및 드라마 제작 현장", "source": "방송가 소식"},
        {"url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800&q=80", "caption": "국내외 주요 영화제 및 문화 엔터테인먼트", "source": "문화예술 자료"},
    ],
    "sports": [
        {"url": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800&q=80", "caption": "국내외 축구 및 주요 리그 경기 현장", "source": "스포츠 현장 자료"},
        {"url": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800&q=80", "caption": "열기 가득한 프로 스포츠 경기장", "source": "스포츠 경기 취재 자료"},
        {"url": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80", "caption": "선수들의 열정과 결정적 승부의 순간", "source": "스포츠 미디어"},
    ],
    "morning-news": [
        {"url": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80", "caption": "글로벌 경제 및 주요 외신 헤드라인 브리핑", "source": "글로벌 뉴스 데스크"},
        {"url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&q=80", "caption": "세계 금융 허브 및 주요 증권 거래소 전경", "source": "해외 비즈니스"},
        {"url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80", "caption": "글로벌 공급망 및 세계 경제 흐름", "source": "국제 통상 자료"},
    ],
    "daily-report": [
        {"url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80", "caption": "글로벌 증시 및 일일 금융시장 주요 지표", "source": "금융시장 분석"},
        {"url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&q=80", "caption": "뉴욕 월스트리트 및 미국 주요 거래소 동향", "source": "뉴욕증시 자료"},
        {"url": "https://images.unsplash.com/photo-1516245834210-c4c142787335?w=800&q=80", "caption": "주요 자산 시장 및 디지털 금융 트렌드", "source": "투자시장 리포트"},
    ],
    "kr-stock": [
        {"url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80", "caption": "국내 증시 및 코스피·코스닥 시장 시세 동향", "source": "한국 거래소 자료"},
        {"url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&q=80", "caption": "국내 주요 상장 기업 실적 및 증권가 분석", "source": "시장 리서치"},
        {"url": "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=800&q=80", "caption": "투자자 수급 동향 및 주가 지표 차트", "source": "증시 데이터 분석"},
    ],
    "us-stock": [
        {"url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&q=80", "caption": "뉴욕증권거래소(NYSE) 및 나스닥 주요 지수 동향", "source": "뉴욕증시 자료"},
        {"url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&q=80", "caption": "월스트리트 주요 금융 기관 및 글로벌 테크 기업", "source": "해외 비즈니스"},
        {"url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80", "caption": "미국 S&P500 및 빅테크 종목 모멘텀", "source": "글로벌 마켓"},
    ],
    "global-stock": [
        {"url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80", "caption": "글로벌 증시 및 아시아·유럽 주요 지수 흐름", "source": "국제 금융 시장"},
        {"url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&q=80", "caption": "세계 거시경제 환경 및 주요국 주식 시장", "source": "글로벌 증권 브리핑"},
        {"url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&q=80", "caption": "해외 자산 배분 및 글로벌 펀드 플로우", "source": "글로벌 리포트"},
    ],
    "crypto": [
        {"url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80", "caption": "블록체인 네트워크 및 디지털 자산 생태계", "source": "가상자산 리서치"},
        {"url": "https://images.unsplash.com/photo-1516245834210-c4c142787335?w=800&q=80", "caption": "비트코인 및 주요 암호화폐 시세 흐름", "source": "암호화폐 시장 동향"},
        {"url": "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=800&q=80", "caption": "디지털 금융 혁신 및 온체인 데이터 분석", "source": "디지털 에셋 뉴스"},
    ],
    "bonds-rates": [
        {"url": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&q=80", "caption": "중앙은행 기준금리 결정 및 국채 수익률 추이", "source": "통화정책 자료"},
        {"url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&q=80", "caption": "채권 시장 자금 흐름 및 글로벌 금리 동향", "source": "채권시장 분석"},
        {"url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80", "caption": "금리 인하·인상 전망 및 매크로 지표 분석", "source": "금융 통계"},
    ],
    "economic-indicators": [
        {"url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&q=80", "caption": "주요 경제 성장률 및 인플레이션 지표 발표", "source": "경제 통계청 자료"},
        {"url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80", "caption": "고용·소비·물가 등 거시 경제 핵심 지표", "source": "매크로 지표 리포트"},
        {"url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80", "caption": "글로벌 교역량 및 산업 생산 동향", "source": "국제 경제 기구"},
    ],
    "futures-options": [
        {"url": "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=800&q=80", "caption": "파생상품 시장 변동성 및 선물·옵션 만기 동향", "source": "파생시장 브리핑"},
        {"url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80", "caption": "헤지 펀드 포지션 및 기관 수급 분석", "source": "시장 전략 자료"},
        {"url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&q=80", "caption": "지수 선물 베이시스 및 옵션 변동성 지표", "source": "선물옵션 분석"},
    ],
    "investment-strategy": [
        {"url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&q=80", "caption": "중장기 자산 배분 및 포트폴리오 최적화 전략", "source": "투자 전략 연구"},
        {"url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=800&q=80", "caption": "리스크 관리 및 수익률 제고 방안 모색", "source": "자산운용 인사이트"},
        {"url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&q=80", "caption": "시장 사이클 대응 및 섹터 로테이션 전략", "source": "투자 리포트"},
    ],
    "invest-study": [
        {"url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&q=80", "caption": "기초 금융 지식 및 실전 투자 분석 기법", "source": "투자 공부방"},
        {"url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&q=80", "caption": "재무제표 읽기 및 기업 펀더멘털 분석", "source": "금융 아카데미"},
        {"url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&q=80", "caption": "워런 버핏 등 대가들의 투자 철학 분석", "source": "투자 가이드"},
    ],
    "short-selling": [
        {"url": "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=800&q=80", "caption": "대차거래 잔고 및 주요 종목 공매도 비중 추이", "source": "공매도 종합 포털"},
        {"url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80", "caption": "숏커버링 가능성 및 하방 압력 점검", "source": "증시 리스크 분석"},
        {"url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&q=80", "caption": "외국인·기관 공매도 거래 대금 분석", "source": "시장 데이터"},
    ],
    "default": [
        {"url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80", "caption": "실시간 경제 및 주요 사회적 관심 현안", "source": "머니노트365 자료"},
        {"url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&q=80", "caption": "급변하는 시장 트렌드 및 산업 현장", "source": "산업 비즈니스 자료"},
        {"url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80", "caption": "심층 데이터 및 최신 트렌드 브리핑", "source": "미디어 인사이트"},
    ]
}


def download_and_upload_image(image_url: str, caption: str, source: str, title_for_alt: str, idx: int):
    """
    외부 이미지 URL을 다운로드하여 워드프레스 미디어 라이브러리에 업로드
    반환: {"id": media_id, "url": media_url, "caption": caption, "source": source} or None
    """
    if not image_url or not image_url.startswith("http"):
        return None

    try:
        resp = requests.get(image_url, headers=HEADERS, timeout=12)
        if resp.status_code == 200 and len(resp.content) > 1000:
            # 안전한 ASCII 임시 파일명 생성 (Latin-1 헤더 충돌 방지)
            tmp_filename = f"temp_wp_{int(time.time() * 1000)}_{idx}.jpg"
            with open(tmp_filename, "wb") as f:
                f.write(resp.content)

            alt_text = f"{title_for_alt} 관련 현장 사진 {idx}"
            mid, murl = upload_image(tmp_filename, title=alt_text)

            if os.path.exists(tmp_filename):
                os.remove(tmp_filename)

            if mid and murl:
                return {
                    "id": mid,
                    "url": murl,
                    "caption": caption,
                    "source": source
                }
    except Exception as e:
        print(f"    [WARN] 이미지 다운로드/업로드 건너뜀 ({image_url[:40]}...): {e}")

    return None


def make_image_block(img_dict: dict) -> str:
    """WAF에 안전하고 워드프레스 FSE와 호환되는 표준 이미지 블록 HTML 생성"""
    img_id = img_dict.get("id", "")
    url = img_dict.get("url", "")
    caption = img_dict.get("caption", "관련 현장 사진")
    source = img_dict.get("source", "보도자료")

    return f"""
<!-- wp:image {{"id":{img_id},"sizeSlug":"large","linkDestination":"none"}} -->
<figure class="wp-block-image size-large">
<img src="{url}" alt="{caption}" />
<figcaption>▲ {caption} (사진 출처: {source})</figcaption>
</figure>
<!-- /wp:image -->
"""


def get_image_candidates(category_type: str, news_items: list = None, max_images: int = 3) -> list:
    """
    뉴스 수집 데이터에서 실제 보도 사진을 우선 추출하고,
    부족할 경우 카테고리별 고화질 검증 이미지 풀에서 보충하여 2~3개 반환
    """
    candidates = []
    seen_urls = set()

    # 1. 수집된 뉴스 기사에서 실제 보도 사진 추출
    if news_items:
        for item in news_items:
            img_url = item.get("image_url") or item.get("pic")
            if img_url and img_url not in seen_urls and img_url.startswith("http"):
                seen_urls.add(img_url)
                title = item.get("title", "")
                clean_title = re.sub(r'\[.*?\]', '', title).strip()
                if len(clean_title) > 35:
                    clean_title = clean_title[:35] + "..."
                if not clean_title:
                    clean_title = "관련 주요 보도 현장"

                source = item.get("source") or "언론사 보도자료"
                candidates.append({
                    "url": img_url,
                    "caption": clean_title,
                    "source": source
                })
                if len(candidates) >= max_images:
                    break

    # 2. 부족한 경우 카테고리별 검증된 고화질 기본 풀에서 채움
    if len(candidates) < max_images:
        pool = CATEGORY_FALLBACK_IMAGES.get(category_type, CATEGORY_FALLBACK_IMAGES["default"])
        for fb in pool:
            if fb["url"] not in seen_urls:
                seen_urls.add(fb["url"])
                candidates.append(fb)
                if len(candidates) >= max_images:
                    break

    return candidates[:max_images]


def enrich_post_with_images(content: str, category_type: str, title: str,
                            news_items: list = None, max_images: int = 3) -> tuple:
    """
    게시글 본문(content)을 받아 관련 이미지 2~3장을 업로드하고 본문 및 썸네일에 자동 삽입
    반환: (featured_media_id, updated_content)
    """
    # 이미 본문에 wp:image 블록이 충분히 포함되어 있다면 추가 작업 건너뜀
    if content.count("<!-- wp:image") >= max_images:
        return None, content

    candidates = get_image_candidates(category_type, news_items=news_items, max_images=max_images)
    if not candidates:
        return None, content

    print(f"  📷 [이미지 매니저] '{category_type}' 관련 사진 {len(candidates)}장 업로드 시작")
    uploaded = []
    for idx, c in enumerate(candidates, 1):
        res = download_and_upload_image(
            image_url=c["url"],
            caption=c["caption"],
            source=c["source"],
            title_for_alt=title,
            idx=idx
        )
        if res:
            uploaded.append(res)
            print(f"    ✅ 사진 {idx} 등록 성공 (ID: {res['id']}) - {res['source']}")

    if not uploaded:
        return None, content

    featured_media_id = uploaded[0]["id"]
    updated_content = content

    # 1. 첫 번째 사진: 상단 헤더/요약 직후(또는 첫 번째 h2 앞)에 삽입
    img1_block = make_image_block(uploaded[0])
    if "</p>" in updated_content:
        # 첫 번째 문단 직후에 삽입
        first_p_idx = updated_content.find("</p>") + 4
        updated_content = updated_content[:first_p_idx] + "\n" + img1_block + "\n" + updated_content[first_p_idx:]
    elif "<hr>" in updated_content:
        updated_content = updated_content.replace("<hr>", f"<hr>\n{img1_block}", 1)
    else:
        updated_content = img1_block + "\n" + updated_content

    # 2. 두 번째 사진: 본문 중간 (2번째 또는 3번째 h2 앞)에 삽입
    if len(uploaded) > 1:
        img2_block = make_image_block(uploaded[1])
        h2_matches = [m.start() for m in re.finditer(r'<h2\b', updated_content)]
        if len(h2_matches) >= 3:
            pos = h2_matches[2]
            updated_content = updated_content[:pos] + img2_block + "\n" + updated_content[pos:]
        elif len(h2_matches) >= 2:
            pos = h2_matches[1]
            updated_content = updated_content[:pos] + img2_block + "\n" + updated_content[pos:]
        else:
            updated_content += "\n" + img2_block

    # 3. 세 번째 사진: 본문 후반부 (FAQ 또는 결론 섹션 앞)에 삽입
    if len(uploaded) > 2:
        img3_block = make_image_block(uploaded[2])
        if "<h2>❓" in updated_content:
            updated_content = updated_content.replace("<h2>❓", f"{img3_block}\n<h2>❓", 1)
        elif "<h2>📌" in updated_content:
            updated_content = updated_content.replace("<h2>📌", f"{img3_block}\n<h2>📌", 1)
        else:
            h2_matches = [m.start() for m in re.finditer(r'<h2\b', updated_content)]
            if len(h2_matches) >= 4:
                pos = h2_matches[-2]
                updated_content = updated_content[:pos] + img3_block + "\n" + updated_content[pos:]
            else:
                updated_content += "\n" + img3_block

    print(f"  ✨ [이미지 매니저] 총 {len(uploaded)}장 사진 배치 완료 (대표 썸네일 ID: {featured_media_id})")
    return featured_media_id, updated_content
