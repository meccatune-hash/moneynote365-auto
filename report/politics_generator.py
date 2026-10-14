# -*- coding: utf-8 -*-
"""
정치 이슈 뉴스 AI 리포트 생성기
- 수집된 정치권 뉴스를 AI로 심층 분석
- 당일 가장 뜨거운 정치 핫이슈 TOP 기사 엄선 및 객관적 해설
- 아침(모닝) / 저녁(이브닝) 판별 및 맞춤형 브리핑 생성
- 공정성, 객관성, 중립성 기반의 심층 해설
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

POLITICS_PROMPT_TEMPLATE = """
당신은 20년 경력의 정치부 수석 데스크이자 정치 평론가입니다.
아래 오늘 수집된 최신 정치권 뉴스 기사 목록을 분석하여, {edition_kr} 정치 종합 브리핑을 작성하세요.
특히 "그날그날 가장 핫이슈가 되는 정치권 기사"를 최우선으로 선정하여 사실(Fact)에 기반한 객관적이고 균형 잡힌 심층 분석을 제공해야 합니다.

=== 오늘 수집된 정치 뉴스 목록 ===
{news_list}

=== 발행 시점 ===
{edition_kr} 판 (기준 시각: {now_time_str})

=== 작성 규칙 ===
1. 순수 HTML 태그만 사용: <h2>, <h3>, <p>, <ul>, <li>, <ol>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <blockquote>, <strong>, <em>, <hr>
2. style 속성, div, span, img, script, iframe 절대 금지 (WordPress WAF 방화벽 충돌 방지)
3. 본문 텍스트 분량은 최소 3,500자 이상으로 매우 상세하고 충실하게 작성할 것
4. 여야 및 각 정파의 입장을 공정하고 균형 있게 반영하는 객관적 저널리즘 필체 유지
5. 마크다운 기호(```) 없이 순수 HTML만 바로 출력

=== 필수 구성 구조 ===

<h2>🏛️ 오늘의 가장 뜨거운 정치권 핫이슈 TOP 기사 집중 분석</h2>
오늘 정치권에서 가장 큰 파장과 논쟁을 일으킨 결정적 핫이슈 1~2개를 엄선하여 심층 분석:
- 이슈의 발단과 전개 과정 (상세한 팩트 정리)
- 여당과 야당, 정부 등 주요 당사자들의 공식 입장 비교
- 향후 정국 및 정책에 미칠 파장과 시사점

<h2>⚖️ 국회 & 여야 정당 동향 (원내 공방 및 법안 심사)</h2>
국회 상임위원회, 본회의, 각 당 지도부(원내대표·당대표) 주요 발언 및 법안 처리 동향 4~6개 선별:
각 소제목(<h3>), 여야 간 쟁점 사항, 찬반 논리, 처리 전망 상세 서술.

<h2>🏢 대통령실 & 행정부 정책 주요 소식</h2>
대통령실 브리핑, 국무회의, 정부 주요 부처의 핵심 정책 발표 및 외교/안보 현안 3~5개 소개.

<h2>📊 여론조사 & 민심의 흐름</h2>
정당 지지도, 국정 수행 평가, 주요 사회적 갈등 현안에 대한 여론 동향 분석 (신뢰도와 데이터 중심 서술).

<h2>💬 오늘의 정치권 주요 발언 & 촌철살인</h2>
오늘 정치권 주요 인사들이 남긴 화제의 발언 3~4가지와 그 정치적 함의 요약.

<h2>❓ 알기 쉬운 오늘의 정치 쟁점 Q&A</h2>
오늘 뉴스 중 유권자·시민들이 가장 궁금해할 법안 내용이나 정치 용어 4~5개에 대한 명쾌한 해설.

<h2>📌 {edition_kr} 정국 전망 및 한줄 총평</h2>
오늘 하루 정치권을 총괄하는 통찰력 있는 한줄 평론 (<blockquote> 사용).

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
    return "<p>정치 뉴스 브리핑 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.</p>"


def get_current_edition() -> str:
    now = datetime.now(KST)
    if now.hour < 14:
        return "morning"
    else:
        return "evening"


def generate_politics_report(news_data: dict, edition: str = None) -> str:
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
        news_lines = ["최신 국회, 여야 정당, 대통령실 및 정책 관련 핫이슈 뉴스를 종합하여 작성해주세요."]

    news_list_str = "\n".join(news_lines)

    prompt = POLITICS_PROMPT_TEMPLATE.format(
        news_list=news_list_str,
        edition_kr=edition_kr,
        now_time_str=now_time_str,
    )

    print(f"[AI] {edition_kr} 정치 이슈 브리핑 생성 중...")
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
<strong>🏛️ 수집 뉴스:</strong> {total_count}개 &nbsp;|&nbsp;
<strong>🌐 출처:</strong> 구글 뉴스, 연합뉴스, 동아일보, SBS, JTBC</p>

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
<p><strong>📰 참고 언론사:</strong> 구글 뉴스 정치, 연합뉴스 정치부, 동아일보 정치, SBS 정치, JTBC 뉴스</p>
<p><strong>🕐 실시간 수집 시각:</strong> {collected_at}</p>
<p><strong>🔗 관련 카테고리 둘러보기:</strong>
<a href="{SITE_URL}/category/politics/">정치 이슈</a> |
<a href="{SITE_URL}/category/economic-indicators/">경제 지표</a> |
<a href="{SITE_URL}/category/daily-report/">일일 투자 보고서</a> |
<a href="{SITE_URL}/category/morning-news/">모닝 뉴스</a>
</p>
<hr>
<p><strong>※ 공정성 및 객관성 안내:</strong> 본 브리핑은 실시간 보도된 주요 언론사들의 팩트 기사를 바탕으로 인공지능(AI)이 중립적이고 객관적인 관점에서 정리·요약한 정보성 콘텐츠입니다.</p>
"""

    full_html = f"{header_html}\n{body}\n{footer_html}"
    print(f"  [OK] 정치 브리핑 생성 완료 ({len(full_html):,}자)")
    return full_html


def generate_politics_title(edition: str = None) -> str:
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()

    if edition == "morning":
        return (f"[{now.strftime('%Y.%m.%d')}({wd}) 아침] 정치권 핫이슈 모닝 브리핑 | "
                f"오늘 가장 뜨거운 정치 뉴스 TOP & 국회·정당 총정리")
    else:
        return (f"[{now.strftime('%Y.%m.%d')}({wd}) 저녁] 정치권 핫이슈 이브닝 결산 | "
                f"오늘 밤 가장 화제된 정치 뉴스 TOP & 여야 공방·정책 총정리")


def generate_politics_excerpt(edition: str = None) -> str:
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()

    ed_text = "아침" if edition == "morning" else "저녁"
    return (
        f"{now.strftime('%Y년 %m월 %d일')}({wd}) {ed_text} 기준, 오늘 정치권에서 가장 뜨겁게 화제가 된 "
        f"핫이슈 TOP 기사와 국회, 여야 정당 동향, 대통령실 정책 소식을 객관적으로 총정리해 드립니다."
    )
