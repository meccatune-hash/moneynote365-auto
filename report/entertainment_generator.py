# -*- coding: utf-8 -*-
"""
연예·엔터테인먼트 뉴스 AI 리포트 생성기
- 수집된 연예 뉴스를 AI로 심층 분석
- 당일 가장 뜨거운 핫이슈 TOP 기사 엄선 및 집중 해설
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

ENTERTAINMENT_PROMPT_TEMPLATE = """
당신은 15년 경력의 대중문화 전문 칼럼니스트이자 연예부 수석 기자입니다.
아래 오늘 수집된 최신 연예계 뉴스 기사 목록을 분석하여, {edition_kr} 연예계 종합 브리핑을 작성하세요.
특히 "그날그날 가장 핫이슈가 되는 기사"를 최우선으로 선정하여 독자들의 호기심을 완벽히 충족시키는 깊이 있는 분석을 제공해야 합니다.

=== 오늘 수집된 연예 뉴스 목록 ===
{news_list}

=== 발행 시점 ===
{edition_kr} 판 (기준 시각: {now_time_str})

=== 작성 규칙 ===
1. 순수 HTML 태그만 사용: <h2>, <h3>, <p>, <ul>, li, <ol>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <blockquote>, <strong>, <em>, <hr>
2. style 속성, div, span, img, script, iframe 절대 금지 (WordPress WAF 방화벽 충돌 방지)
3. 본문 텍스트 분량은 최소 3,500자 이상으로 풍성하고 충실하게 작성할 것
4. 흥미진진하면서도 품격 있고 신뢰도 높은 어조 유지
5. 마크다운 기호(```) 없이 순수 HTML만 바로 출력

=== 필수 구성 구조 ===

<h2>🌟 오늘의 가장 뜨거운 연예계 핫이슈 TOP 기사 집중 분석</h2>
오늘 연예계에서 가장 뜨겁게 화제가 된 결정적 이슈 1~2개를 엄선하여 심층 보도:
- 사건의 배경과 전개 과정 상세 설명
- 공식 입장 및 대중·팬들의 반응
- 이번 이슈가 향후 방송가나 연예계에 미칠 파장 및 시사점

<h2>🎬 방송·예능 & 화제의 드라마 하이라이트</h2>
주요 지상파·종편·케이블 방송 및 인기 드라마/예능 관련 뉴스 4~6개 선별:
각 소제목(<h3>), 줄거리 및 핵심 포인트, 출연진 활약상, 시청률/화제성 분석.

<h2>🎤 K-POP & 가요계 레이더 (음원·컴백·콘서트)</h2>
아이돌, K-POP 아티스트의 신곡 발매, 빌보드 및 글로벌 차트 성과, 콘서트 소식 4~6개 정리:
각 소제목(<h3>), 아티스트별 신곡 콘셉트 및 글로벌 반응 상세 서술.

<h2>🎥 영화 & 글로벌 OTT (넷플릭스·디즈니+) 최신 동향</h2>
국내외 박스오피스, 신작 개봉작, 넷플릭스/디즈니+ 등 OTT 인기 콘텐츠 소식 3~5개 소개.

<h2>💬 팬덤 & SNS 실시간 핫토크</h2>
대중과 팬들이 오늘 온라인 커뮤니티(트위터/X, 인스타그램, 더쿠 등)에서 가장 열광하거나 토론한 화제의 키워드 3가지 요약.

<h2>❓ 오늘의 연예가 Q&A & 비하인드 스토리</h2>
오늘 소식 중 독자들이 가장 궁금해할 질문 4~5개와 그에 대한 명쾌한 해설.

<h2>📌 {edition_kr} 연예 브리핑 한줄 총평</h2>
오늘 연예계의 전체적인 흐름과 분위기를 관통하는 한줄 요약 및 평론 (<blockquote> 사용).

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
    return "<p>연예 뉴스 브리핑 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.</p>"


def get_current_edition() -> str:
    """현재 시간에 따라 아침(모닝) / 저녁(이브닝) 자동 판별"""
    now = datetime.now(KST)
    if now.hour < 14:
        return "morning"
    else:
        return "evening"


def generate_entertainment_report(news_data: dict, edition: str = None) -> str:
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
        news_lines = ["최신 연예계 핫이슈 및 K-POP, 드라마 관련 뉴스를 종합하여 작성해주세요."]

    news_list_str = "\n".join(news_lines)

    prompt = ENTERTAINMENT_PROMPT_TEMPLATE.format(
        news_list=news_list_str,
        edition_kr=edition_kr,
        now_time_str=now_time_str,
    )

    print(f"[AI] {edition_kr} 연예·엔터테인먼트 뉴스 브리핑 생성 중...")
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
<strong>🎬 수집 뉴스:</strong> {total_count}개 &nbsp;|&nbsp;
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
<p><strong>📰 참고 언론사:</strong> 구글 뉴스 연예, 연합뉴스 대중문화, 동아일보 연예, JTBC 엔터테인먼트</p>
<p><strong>🕐 실시간 수집 시각:</strong> {collected_at}</p>
<p><strong>🔗 관련 카테고리 둘러보기:</strong>
<a href="{SITE_URL}/category/entertainment/">연예·엔터테인먼트</a> |
<a href="{SITE_URL}/category/sports/">스포츠 뉴스</a> |
<a href="{SITE_URL}/category/morning-news/">모닝 뉴스</a> |
<a href="{SITE_URL}/category/daily-report/">일일 투자 보고서</a>
</p>
<hr>
<p><strong>※ 안내:</strong> 본 기사는 실시간 공개된 언론사 뉴스를 바탕으로 AI가 요약·분석한 대중문화 정보 콘텐츠입니다.</p>
"""

    full_html = f"{header_html}\n{body}\n{footer_html}"
    print(f"  [OK] 연예 브리핑 생성 완료 ({len(full_html):,}자)")
    return full_html


def generate_entertainment_title(edition: str = None) -> str:
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()

    if edition == "morning":
        return (f"[{now.strftime('%Y.%m.%d')}({wd}) 아침] 연예계 핫이슈 모닝 브리핑 | "
                f"오늘 가장 뜨거운 연예 뉴스 TOP & K-POP·드라마 총정리")
    else:
        return (f"[{now.strftime('%Y.%m.%d')}({wd}) 저녁] 연예계 핫이슈 이브닝 결산 | "
                f"오늘 밤 가장 화제된 연예 뉴스 TOP & 스타·방송 총정리")


def generate_entertainment_excerpt(edition: str = None) -> str:
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()

    ed_text = "아침" if edition == "morning" else "저녁"
    return (
        f"{now.strftime('%Y년 %m월 %d일')}({wd}) {ed_text} 기준, 오늘 연예계에서 가장 뜨겁게 화제가 된 "
        f"핫이슈 TOP 기사와 K-POP, 화제의 드라마·예능, 영화 최신 소식을 총정리하여 전해드립니다."
    )
