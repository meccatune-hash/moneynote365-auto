# -*- coding: utf-8 -*-
"""
머니노트365 모닝 뉴스 생성기
- CNN, BBC, Reuters 등 수집 뉴스를 AI로 한국어 분석
- 미국 증시 영향도 평가
- 텍스트 전용, SEO 최적화
"""
import os, re
from datetime import datetime, timezone, timedelta
from google import genai
from dotenv import load_dotenv

load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

KST      = timezone(timedelta(hours=9))
SITE_URL = os.getenv("WP_URL", "https://kingbrightsucces.com")
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


MORNING_NEWS_PROMPT = """
당신은 월스트리트에서 20년 경력의 글로벌 금융 애널리스트입니다.
아래 오늘 새벽 주요 해외 언론(CNN, BBC, Reuters, CNBC)에서 수집한 뉴스 목록을 분석하여,
한국 투자자를 위한 아침 모닝 브리핑을 작성하세요.

=== 오늘 수집된 글로벌 뉴스 ===
{news_list}

=== 작성 규칙 ===
1. 순수 HTML만 사용: <h2>, <h3>, <p>, <ul>, <li>, <ol>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <blockquote>, <strong>, <em>, <hr>
2. inline style, div, span, img, script, iframe 절대 금지
3. 전체 본문 최소 4,000자 이상 (HTML 태그 제외)
4. 한국어로 작성 (영어 원문 용어는 괄호로 병기)
5. 각 뉴스에 반드시 "미국 증시 영향도" 평가 포함 (🔴 강한 악재 / 🟡 중립 / 🟢 강한 호재)

=== 보고서 구조 ===

<h2>🌅 오늘의 글로벌 새벽 뉴스 브리핑 핵심 요약</h2>
오늘 오전 7시 기준, 미국·유럽 증시에 영향을 줄 핵심 뉴스 3~5개를 불릿 형식으로 요약.
각 항목에 영향도 이모지 포함.

<h2>📰 경제 & 금융 주요 뉴스 (심층 분석)</h2>
수집된 뉴스 중 경제·금융 관련 뉴스 5~7개 선별.
각 뉴스마다:
- <h3> 소제목: 뉴스 핵심 내용 (20자 내외 한국어)
- <p> 원문 출처와 핵심 내용 200~300자 설명
- <p> <strong>미국 증시 영향:</strong> 영향도와 구체적 이유 설명
- <p> <strong>한국 투자자 관점:</strong> 국내 시장/종목에 미치는 영향

<h2>🌏 정치 & 지정학 리스크 뉴스</h2>
지정학 리스크, 정치 불확실성, 무역 갈등 관련 뉴스 3~5개.
각 뉴스마다 동일한 형식 (소제목 + 분석 + 영향도)

<h2>🏢 기업 & 산업 주요 뉴스</h2>
주요 기업 실적, M&A, 신제품, 규제 관련 뉴스 3~5개.
특히 빅테크(애플, 엔비디아, 마이크로소프트, 구글, 아마존), 반도체, AI 관련 뉴스 우선

<h2>🏦 중앙은행 & 금리 동향</h2>
연준(Fed), ECB, BOJ 등 중앙은행 관련 최신 소식.
금리 전망, 인플레이션 지표 발표 예정 일정 포함.
없으면 최근 주요 발언 기반으로 작성.

<h2>📊 오늘 주목할 경제지표 & 일정</h2>
오늘 날짜 기준으로 예정된 주요 경제지표 발표 일정:
- 미국: CPI, PPI, 고용지표, GDP, 소매판매, 연준 회의 등
- 유럽: ECB 결정, PMI 등
- 한국: 한국은행 기준금리, 수출 지표 등
(정확한 정보가 없으면 일반적인 주요 발표 시간대 안내)

<h2>💡 오늘의 투자 시사점 & 전략</h2>
위 뉴스들을 종합한 오늘의 시장 방향성 전망.
- 단기 투자자 관점
- 장기 투자자 관점  
- 주목할 섹터와 이유
- 오늘 특히 조심해야 할 리스크
투자 대가 관련 명언 1개 인용 (<blockquote> 태그 사용)

<h2>❓ 오늘의 뉴스 FAQ</h2>
오늘 뉴스에서 독자들이 가장 궁금해할 질문 5개 Q&A 형식으로.
각 답변은 3~5문장으로 상세하게.

<h2>📚 오늘의 투자 용어</h2>
오늘 뉴스에 등장한 경제/금융 용어 3~4개 쉬운 설명.

<h2>⚠️ 면책 조항</h2>
투자 권유 아님, 교육 목적 안내문 (2~3줄)

출력: 순수 HTML만 출력 (```없이)
"""


def _call_gemini(prompt: str) -> str:
    models = ["gemini-3.6-flash", "gemini-2.5-pro", "gemini-2.5-flash"]
    for model in models:
        try:
            resp = _client.models.generate_content(model=model, contents=prompt)
            text = resp.text.strip()
            text = re.sub(r'^```html?\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*```\s*$', '', text)
            if len(text) > 500:
                print(f"  [모델: {model}] 생성 성공 ({len(text):,}자)")
                return text.strip()
        except Exception as e:
            print(f"  [{model}] 오류: {str(e)[:80]}")
            continue
    return "<p>뉴스 브리핑 생성 오류. 잠시 후 다시 시도해주세요.</p>"


def generate_morning_news(news_data: dict) -> str:
    now     = datetime.now(KST)
    wd      = WEEKDAYS[now.weekday()]
    date_kr = now.strftime(f"%Y년 %m월 %d일({wd})")

    # 뉴스 목록 텍스트 구성
    news_lines = []
    for item in news_data.get("all_items", [])[:50]:   # 최대 50개
        source = item.get("source", "")
        title  = item.get("title", "")
        desc   = item.get("desc", "")[:150]
        news_lines.append(f"[{source}] {title}\n  요약: {desc}\n")

    if not news_lines:
        news_lines = ["뉴스 수집에 실패했습니다. 최근 주요 글로벌 경제 뉴스를 바탕으로 작성해주세요."]

    news_list = "\n".join(news_lines)

    print("[AI] 모닝 뉴스 브리핑 생성 중...")
    body = _call_gemini(MORNING_NEWS_PROMPT.format(news_list=news_list))

    # 핵심 통계 테이블
    total_count   = news_data.get("total_count", 0)
    by_source     = news_data.get("by_source", {})
    collected_at  = news_data.get("collected_at", now.strftime("%Y-%m-%d %H:%M KST"))

    source_rows = "\n".join(
        f"<tr><td>{src}</td><td>{len(items)}개</td></tr>"
        for src, items in by_source.items()
    )

    header_html = f"""
<p><strong>📅 발행일:</strong> {date_kr} 오전 7:00 KST &nbsp;|&nbsp;
<strong>📰 수집 뉴스:</strong> {total_count}개 &nbsp;|&nbsp;
<strong>🌐 출처:</strong> CNN, BBC, Reuters, CNBC, MarketWatch</p>

<table>
<thead>
<tr><th>뉴스 출처</th><th>수집 기사 수</th></tr>
</thead>
<tbody>
{source_rows}
<tr><td><strong>합계</strong></td><td><strong>{total_count}개</strong></td></tr>
</tbody>
</table>

<hr>
"""

    footer_html = f"""
<hr>
<p><strong>📰 참고 원문 출처:</strong> CNN Business, BBC Business News, Reuters, CNBC, MarketWatch</p>
<p><strong>🕐 데이터 수집 시간:</strong> {collected_at}</p>
<p><strong>🔗 관련 카테고리:</strong>
<a href="{SITE_URL}/category/daily-report/">일일 투자 보고서</a> |
<a href="{SITE_URL}/category/us-stock/">미국 주식</a> |
<a href="{SITE_URL}/category/economic-indicators/">경제 지표</a> |
<a href="{SITE_URL}/category/investment-strategy/">투자 전략</a>
</p>
<hr>
<p><strong>※ 면책 조항:</strong> 본 뉴스 브리핑은 교육 목적의 정보 제공이며, 투자 권유가 아닙니다. 모든 투자 결정과 책임은 투자자 본인에게 있습니다.</p>
"""

    full_html = f"{header_html}\n{body}\n{footer_html}"
    print(f"  [OK] 모닝 뉴스 생성 완료 ({len(full_html):,}자)")
    return full_html


def generate_news_title() -> str:
    now = datetime.now(KST)
    wd  = WEEKDAYS[now.weekday()]
    return (f"[{now.strftime('%Y.%m.%d')}({wd})] 머니노트365 모닝 뉴스 브리핑 | "
            f"미국 증시 영향 글로벌 뉴스 총정리 (CNN·BBC·Reuters·CNBC)")


def generate_news_excerpt() -> str:
    now = datetime.now(KST)
    wd  = WEEKDAYS[now.weekday()]
    return (
        f"{now.strftime('%Y년 %m월 %d일')}({wd}) 오전 7시 기준, "
        f"미국 증시에 영향을 줄 글로벌 주요 뉴스를 CNN, BBC, Reuters, CNBC에서 종합했습니다. "
        f"경제·금융·지정학 리스크 분석과 한국 투자자를 위한 시사점을 담았습니다."
    )
