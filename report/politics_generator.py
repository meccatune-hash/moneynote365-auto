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
당신은 대한민국 유력 일간지 정치부에서 20년간 국회와 용산 대통령실을 출입해 온 베테랑 정치 전문 대기자(Senior Political Reporter)이자 논설위원입니다.
AI가 생성한 듯한 건조한 요약문, 기계적인 설명투, 뻔한 블로그 정리글 느낌을 철저하게 배제하고,
실제 신문사 1면과 정치 종합면에 실리는 정통 '정치부 심층 기획 분석 기사'를 작성하세요.

=== 오늘 취재된 정치권 팩트 및 주요 보도 목록 ===
{news_list}

=== 발행 시점 ===
{edition_kr} 종합 (기준 시각: {now_time_str})

=== [필수] 정치부 전문 기자식 필체 및 보도 10대 준칙 ===
1. [정통 기사체 평서문 철저 준수]:
   - 반드시 문미 종결형을 '~다', '~했다', '~밝혔다', '~전했다', '~설명했다', '~로 풀이된다', '~에 무게가 실린다', '~라는 관측이다', '~지적이다' 등 공인된 신문 기사체로 일관할 것.
   - 친근한 척하는 경어체('~입니다', '~해요', '~알아보겠습니다'), 안내원 톤('~소개해 드립니다') 절대 금지.
2. [AI 클리셰 원천 배제]:
   - 서두에 "안녕하세요", "오늘 알아볼 내용은", "최근 정치권이 뜨겁게 달아오르고 있습니다" 등 상투적 인사말 절대 금지.
   - 말미에 "지금까지 ~에 대해 알아보았습니다", "도움이 되셨나요?", "댓글을 남겨주세요" 등 블로그식 마무리 절대 금지.
   - "뜨거운 감자", "초미의 관심사", "귀추가 주목된다", "발빠른 대처" 등 판에 박힌 AI 관용구 남발 금지.
3. [6하원칙에 입각한 정통 취재 리드문(Lead)]:
   - 첫 문장은 오늘 정국을 뒤흔든 가장 결정적인 단일 팩트를 묵직하고 강렬하게 압축하여 제시하는 정통 스트레이트 기사 리드문으로 시작할 것.
4. [생생한 정치권 워딩 및 취재원 인용(Quotes)]:
   - 여야 지도부 발언, 대통령실 고위 관계자, 상임위 핵심 의원, 정치 평론가/교수의 발언을 따옴표(" ")로 입체적으로 인용할 것.
   - 예: 여당 원내 핵심 관계자는 "..."라며 반발했다. / 야당 지도부 인사는 "..."라고 날을 세웠다.
5. [신문사 지면 스타일의 세련된 기사 소제목]:
   - "🏛️ 1. 오늘의 핫이슈 TOP 기사", "⚖️ 2. 국회 동향", "❓ Q&A" 같은 유치한 번호 매기기나 이모지 나열 금지.
   - 실제 조간·석간 신문 1면·정치면에 들어갈 법한 날카로운 기사 표제(<h2>, <h3>)를 부여할 것.
6. [풍부한 분량과 치밀한 정국 분석]:
   - 본문 분량은 공백 제외 최소 3,500자 이상으로 사건의 내막, 여야 수싸움, 법안의 쟁점 조항, 향후 총선/대선 및 국정 운영에 미칠 파장을 정밀 분석할 것.
7. [WAF 방화벽 보안 태그]:
   - 순수 HTML만 사용: <h2>, <h3>, <p>, <ul>, <li>, <ol>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <blockquote>, <strong>, <em>, <hr>
   - style 속성, div, span, img, script, iframe 절대 금지. 마크다운 기호 없이 순수 HTML만 출력.

=== 기사 구성 가이드 (정치면 심층 종합) ===

<h2>(오늘 정국을 뒤흔든 최대 승부처·쟁점을 압축한 핵심 헤드라인)</h2>
- 오늘 정치권 최대 핫이슈의 내막과 양측의 격돌 배경 상세 보도.
- 핵심 당사자 발언 및 사실관계 팩트체크.

<h2>(원내 정면충돌: 쟁점 법안 심사와 여야 원내 지도부 수싸움)</h2>
- 국회 상임위 및 본회의 쟁점, 여야 원내대표·원내수석 등의 전술적 대치 상황.
- 처리 전망과 충돌 시나리오.

<h2>(용산 대통령실 & 내각 주요 정책 드라이브 및 대외 행보)</h2>
- 국정 쇄신 과제, 민생·경제 입법 당정 협의, 안보·외교 주요 현안.

<h2>(민심의 풍향계: 여론 지표와 총선·정국 파장)</h2>
- 최근 여론조사 추이 및 지역별·세대별 표심 향방 분석.

<h2>(막전막후: 정치권 촌철살인과 주요 발언의 정치학)</h2>
- 오늘 화제가 된 주요 인사들의 발언과 그 이면에 깔린 정치적 셈법 분석.

<h2>(정국 관전 포인트 및 내일의 분수령)</h2>
- 앞으로 예정된 주요 표결, 청문회, 당정 협의 등 분수령 일정.
- 정국을 관통하는 묵직한 결론 한줄평 (<blockquote> 활용).

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

    print(f"[기자 리포트] {edition_kr} 정치 심층 기사 작성 중...")
    body = _call_gemini(prompt)

    # 기계적인 스크래퍼 테이블 및 AI 문구 전면 제거, 정통 언론사 바이라인 적용
    header_html = f"""
<p><strong>[머니노트365 정치부 = 국회·용산 특별취재팀]</strong> {date_kr} ({edition_kr} 종합)</p>
<hr>
"""

    footer_html = f"""
<hr>
<p><strong>[머니노트365 정치부 데스크]</strong> 저작권자 © 머니노트365 무단전재 및 재배포 금지</p>
<p><strong>🔗 관련 심층 기사:</strong>
<a href="{SITE_URL}/category/politics/">정치 이슈</a> |
<a href="{SITE_URL}/category/economic-indicators/">경제 지표</a> |
<a href="{SITE_URL}/category/morning-news/">모닝 뉴스</a> |
<a href="{SITE_URL}/category/daily-report/">일일 투자 보고서</a>
</p>
"""

    full_html = f"{header_html}\n{body}\n{footer_html}"
    print(f"  [OK] 정치 전문 기사 생성 완료 ({len(full_html):,}자)")
    return full_html


def generate_politics_title(news_data: dict = None, edition: str = None) -> str:
    """실시간 정치 핫이슈를 반영한 날카로운 신문 1면 헤드라인 생성"""
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()
    ed_label = "아침" if edition == "morning" else "저녁"
    date_str = now.strftime(f"%Y.%m.%d({wd})")

    # 수집된 핫이슈 기사들을 기반으로 실제 기자 헤드라인 생성 시도
    if news_data and news_data.get("all_items"):
        top_news = "\n".join([f"- {it.get('title')}" for it in news_data.get("all_items")[:10]])
        prompt = f"""
당신은 대한민국 일간지 1면 헤드라인을 뽑는 20년 차 정치부 부장입니다.
오늘 취재된 다음 정치권 주요 기사 목록을 바탕으로, 오늘 가장 결정적인 핫이슈를 담은 날카롭고 품격 있는 신문 1면 기사 제목 1개를 작성하세요.

취재 기사 목록:
{top_news}

조건:
1. 말머리는 [{date_str} {ed_label}] 로 시작할 것.
2. 팩트와 긴장감이 살아있는 정통 정치부 헤드라인 (35자 내외).
3. "총정리", "알아보자", "핫이슈 모닝 브리핑" 같은 상투적이고 기계적인 블로그 문구 절대 금지.
4. 제목 1줄만 정확히 출력.
"""
        try:
            resp = _client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
            title = resp.text.strip().replace('"', '').replace("'", "")
            title = title.split("\n")[0].strip()
            if len(title) >= 15:
                return title
        except Exception:
            pass

    if edition == "morning":
        return f"[{date_str} 아침] [정치 레이더] 본회의 앞두고 與野 대치 격화… 주요 쟁점 법안 '전운'"
    else:
        return f"[{date_str} 저녁] [정치 결산] 상임위 공방 속 정국 급랭… 내일 여야 지도부 수싸움 분수령"


def generate_politics_excerpt(edition: str = None) -> str:
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()

    ed_text = "아침" if edition == "morning" else "저녁"
    return (
        f"{now.strftime('%Y년 %m월 %d일')}({wd}) {ed_text} 기준, 오늘 정치권을 뒤흔든 핵심 쟁점과 "
        f"여야 원내 지도부의 수싸움, 대통령실 주요 정책 방향을 국회 현장 기자의 시각으로 심층 분석 보도한다."
    )
