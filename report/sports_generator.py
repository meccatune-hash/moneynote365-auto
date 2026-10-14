# -*- coding: utf-8 -*-
"""
스포츠 뉴스 AI 리포트 생성기
- 수집된 스포츠 뉴스를 AI로 심층 분석
- 당일 가장 뜨거운 스포츠 핫이슈 TOP 기사 엄선 및 집중 해설
- 아침(모닝) / 저녁(이브닝) 판별 및 맞춤형 브리핑 생성
- SEO 친화적 순수 HTML 포맷 (인라인 스타일 배제, WAF 호환)
"""
import os
import re
from datetime import datetime, timezone, timedelta
from google import genai
from dotenv import load_dotenv

load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

KST = timezone(timedelta(hours=9))
SITE_URL = os.getenv("WP_URL", "https://kingbrightsucces.com")
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

SPORTS_PROMPT_TEMPLATE = """
당신은 15년 경력의 베테랑 스포츠 전문 기자이자 칼럼니스트입니다.
아래 오늘 수집된 최신 국내외 스포츠 뉴스 기사 목록을 분석하여, {edition_kr} 스포츠 종합 브리핑을 작성하세요.
특히 "그날그날 가장 핫이슈가 되는 기사"를 최우선으로 선정하여 스포츠 팬들이 경기 흐름과 핵심 쟁점을 한눈에 파악할 수 있도록 깊이 있게 해설해야 합니다.

=== 오늘 수집된 스포츠 뉴스 목록 ===
{news_list}

=== 발행 시점 ===
{edition_kr} 판 (기준 시각: {now_time_str})

=== 작성 규칙 ===
1. 순수 HTML 태그만 사용: <h2>, <h3>, <p>, <ul>, <li>, <ol>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <blockquote>, <strong>, <em>, <hr>
2. style 속성, div, span, img, script, iframe 절대 금지 (WordPress WAF 방화벽 충돌 방지)
3. 본문 텍스트 분량은 최소 3,500자 이상으로 흥미롭고 상세하게 작성할 것
4. 생동감 넘치며 전문적이고 객관적인 스포츠 전문 필체 유지
5. 마크다운 기호(```) 없이 순수 HTML만 바로 출력

=== 필수 구성 구조 ===

<h2>🔥 오늘의 가장 뜨거운 스포츠 핫이슈 TOP 기사 집중 분석</h2>
오늘 스포츠계에서 가장 화제가 된 결정적 승부, 선수 활약 또는 빅뉴스 1~2개를 엄선하여 심층 보도:
- 경기 내용 또는 이슈의 구체적인 전개 과정과 배경
- 주요 기록 및 데이터, 승부처 분석
- 선수/감독의 코멘트 및 향후 리그 판도에 미치는 영향

<h2>⚽ 국내외 축구 레이더 (해외파 & 주요 리그)</h2>
손흥민, 이강인, 김민재 등 해외파 코리안리거 소식, EPL, 챔피언스리그, K리그 관련 뉴스 4~6개 선별:
각 소제목(<h3>), 경기 결과, 골/도움 활약상, 현지 언론 평점 및 반응 분석.

<h2>⚾ 프로야구(KBO) & 메이저리그(MLB) 종합</h2>
국내 KBO 리그 소식 및 MLB(오타니, 메이저리그 포스트시즌/순위 등) 주요 뉴스 4~6개 정리:
각 소제목(<h3>), 경기 주요 승부처 및 투타 기록, 선수 인터뷰 및 순위 경쟁 분석.

<h2>🏀 농구·배구·골프 & 기타 종목 하이라이트</h2>
국내외 프로농구(KBL/NBA), 프로배구(V리그), PGA/LPGA 골프 투어 등 주요 인기 종목 소식 3~5개 정리.

<h2>📊 주요 경기 결과 & 오늘/내일 주목할 경기 일정</h2>
팬들이 놓치지 말아야 할 주요 경기 스코어 요약 및 중계/일정 안내.

<h2>💬 스포츠 팬 여론 & 전문가 관전평</h2>
온라인 스포츠 커뮤니티 팬들의 실시간 반응과 전문가 관전 포인트 3가지 정리.

<h2>📌 {edition_kr} 스포츠 브리핑 한줄 총평</h2>
오늘 하루 스포츠계를 요약하는 인상적인 한줄 명언 또는 총평 (<blockquote> 사용).

출력: 순수 HTML만 출력
"""


def _call_gemini(prompt: str) -> str:
    models = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.5-pro"]
    for model in models:
        try:
            resp = _client.models.generate_content(model=model, contents=prompt)
            text = resp.text.strip()
            text = re.sub(r'^```html?\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*```\s*$', '', text)
            if len(text) > 500:
                print(f"  [AI 모델: {model}] 생성 성공 ({len(text):,}자)")
                return text.strip()
        except Exception as e:
            print(f"  [{model}] 오류: {str(e)[:80]}")
            continue
    return "<p>스포츠 뉴스 브리핑 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.</p>"


def get_current_edition() -> str:
    """현재 시간에 따라 아침(모닝) / 저녁(이브닝) 자동 판별"""
    now = datetime.now(KST)
    if now.hour < 14:
        return "morning"
    else:
        return "evening"


def generate_sports_report(news_data: dict, edition: str = None) -> str:
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    date_kr = now.strftime(f"%Y년 %m월 %d일({wd})")

    if not edition:
        edition = get_current_edition()

    edition_kr = "아침 모닝" if edition == "morning" else "저녁 이브닝"
    now_time_str = now.strftime("%H:%M KST")

    # 뉴스 항목 텍스트 구성 (최대 50개)
    news_lines = []
    for item in news_data.get("all_items", [])[:50]:
        source = item.get("source", "")
        title = item.get("title", "")
        desc = item.get("desc", "")[:150]
        news_lines.append(f"[{source}] {title}\n  요약: {desc}\n")

    if not news_lines:
        news_lines = ["최신 국내외 스포츠 축구, 야구, 농구, 골프 핫이슈 뉴스를 종합하여 작성해주세요."]

    news_list_str = "\n".join(news_lines)

    prompt = SPORTS_PROMPT_TEMPLATE.format(
        news_list=news_list_str,
        edition_kr=edition_kr,
        now_time_str=now_time_str,
    )

    print(f"[AI] {edition_kr} 스포츠 뉴스 브리핑 생성 중...")
    body = _call_gemini(prompt)

    total_count = news_data.get("total_count", len(news_data.get("all_items", [])))
    by_source = news_data.get("by_source", {})
    collected_at = news_data.get("collected_at", now.strftime("%Y-%m-%d %H:%M KST"))

    source_rows = "\n".join(
        f"<tr><td>{src}</td><td>{len(items)}개</td></tr>"
        for src, items in by_source.items()
    )

    header_html = f"""
<p><strong>📅 발행일시:</strong> {date_kr} {now_time_str} ({edition_kr} 브리핑) &nbsp;|&nbsp;
<strong>⚽ 수집 뉴스:</strong> {total_count}개 &nbsp;|&nbsp;
<strong>🌐 출처:</strong> 구글 뉴스, 연합뉴스, 동아일보, JTBC</p>

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
<p><strong>📰 참고 언론사:</strong> 구글 뉴스 스포츠, 연합뉴스 스포츠, 동아일보 스포츠, JTBC 스포츠</p>
<p><strong>🕐 실시간 수집 시각:</strong> {collected_at}</p>
<p><strong>🔗 관련 카테고리 둘러보기:</strong>
<a href="{SITE_URL}/category/sports/">스포츠 뉴스</a> |
<a href="{SITE_URL}/category/entertainment/">연예·엔터테인먼트</a> |
<a href="{SITE_URL}/category/morning-news/">모닝 뉴스</a> |
<a href="{SITE_URL}/category/daily-report/">일일 투자 보고서</a>
</p>
<hr>
<p><strong>※ 안내:</strong> 본 기사는 실시간 공개된 언론사 뉴스를 바탕으로 AI가 종합 정리·분석한 스포츠 정보 콘텐츠입니다.</p>
"""

    full_html = f"{header_html}\n{body}\n{footer_html}"
    print(f"  [OK] 스포츠 브리핑 생성 완료 ({len(full_html):,}자)")
    return full_html


def generate_sports_title(edition: str = None) -> str:
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()

    if edition == "morning":
        return (f"[{now.strftime('%Y.%m.%d')}({wd}) 아침] 스포츠 핫이슈 모닝 브리핑 | "
                f"오늘 가장 뜨거운 스포츠 경기 & 해외파·프로야구 총정리")
    else:
        return (f"[{now.strftime('%Y.%m.%d')}({wd}) 저녁] 스포츠 핫이슈 이브닝 결산 | "
                f"오늘 밤 가장 화제된 스포츠 뉴스 TOP & 경기 하이라이트 총정리")


def generate_sports_excerpt(edition: str = None) -> str:
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()

    ed_text = "아침" if edition == "morning" else "저녁"
    return (
        f"{now.strftime('%Y년 %m월 %d일')}({wd}) {ed_text} 기준, 오늘 가장 화제가 된 스포츠 "
        f"핫이슈 TOP 기사와 손흥민·이강인 등 해외파, 프로야구, 메이저리그 주요 경기 결과를 총정리해 드립니다."
    )
