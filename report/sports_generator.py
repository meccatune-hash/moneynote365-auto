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
당신은 국내외 스포츠 현장을 20년간 누벼온 베테랑 스포츠 전문 대기자이자 스포츠국 데스크입니다.
AI가 생성한 듯한 뻔한 경기 결과 요약, 건조한 스코어 나열, 인터넷 블로그 정리글 말투를 철저히 배제하고,
실제 스포츠 신문 1면과 종합면에 실리는 생동감 넘치고 박진감 있는 정통 '스포츠 심층 르포/경기 분석 기사'를 작성하세요.

=== 오늘 취재된 스포츠계 팩트 및 경기 보도 목록 ===
{news_list}

=== 발행 시점 ===
{edition_kr} 종합 (기준 시각: {now_time_str})

=== [필수] 스포츠 전문 기자식 필체 및 보도 10대 준칙 ===
1. [정통 기사체 평서문 철저 준수]:
   - 문미 종결형을 반드시 '~다', '~했다', '~밝혔다', '~전했다', '~설명했다', '~로 풀이된다', '~에 관심이 쏠린다', '~라는 평가다' 등 공인된 신문 기사체로 일관할 것.
   - 친근한 척하는 경어체('~입니다', '~해요', '~알아보겠습니다')나 안내원 톤('~소개해 드립니다')은 절대 사용 금지.
2. [AI 클리셰 원천 배제]:
   - 서두에 "안녕하세요", "최근 스포츠계가 뜨겁게 달아오르고 있습니다", "오늘 알아볼 경기는" 등 상투적 인사말 절대 금지.
   - 말미에 "지금까지 ~에 대해 알아보았습니다", "도움이 되셨나요?", "댓글로 승부를 예측해주세요" 등 블로그식 마무리 절대 금지.
   - "뜨거운 감자", "초미의 관심사", "귀추가 주목된다", "눈길을 끈다" 등 뻔한 AI 관용구 남발 금지.
3. [6하원칙에 입각한 정통 취재 리드문(Lead)]:
   - 첫 문장은 오늘 스포츠계를 뒤흔든 가장 결정적인 승부의 순간이나 선수 활약의 팩트를 박진감 있게 압축 제시하는 정통 스트레이트 기사 리드문으로 시작할 것.
4. [생생한 감독·선수 코멘트 및 현장감 인용(Quotes)]:
   - 감독 인터뷰, 선수의 경기 후 소감, 현지 외신 평점, 해설위원의 분석을 따옴표(" ")로 사실감 있게 인용할 것.
   - 예: 사령탑은 경기 후 인터뷰에서 "..."라며 만족감을 표했다. / 현지 매체는 "..."라고 극찬을 아끼지 않았다.
5. [신문사 지면 스타일의 세련된 기사 소제목]:
   - "🔥 1. 오늘의 핫이슈 TOP 기사", "⚽ 2. 국내외 축구", "❓ Q&A" 같은 유치한 번호 매기기나 이모지 나열 금지.
   - 실제 스포츠 전문지 1면에 들어갈 법한 긴장감 넘치는 기사 표제(<h2>, <h3>)를 부여할 것.
6. [풍부한 분량과 전술·데이터 분석]:
   - 본문 분량은 공백 제외 최소 3,500자 이상으로 결정적 승부처, 전술 분석, 세부 지표 및 스탯, 향후 리그 순위 경쟁 및 판도 변화를 입체적으로 다룰 것.
7. [WAF 방화벽 보안 태그]:
   - 순수 HTML만 사용: <h2>, <h3>, <p>, <ul>, <li>, <ol>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <blockquote>, <strong>, <em>, <hr>
   - style 속성, div, span, img, script, iframe 절대 금지. 마크다운 기호 없이 순수 HTML만 출력.

=== 기사 구성 가이드 (스포츠 심층 종합) ===

<h2>(오늘 스포츠계 최대 승부처·빅매치를 압축한 핵심 헤드라인)</h2>
- 오늘 스포츠 최대 핫이슈의 결정적 승부처와 경기 흐름 상세 취재 보도.
- 감독·선수의 경기 후 공식 인터뷰 및 핵심 활약상 조명.

<h2>(해외파 코리안리거 & 유럽 축구: 골 폭풍과 현지 반응)</h2>
- 손흥민, 이강인, 김민재 등 해외파 선수들의 세부 스탯 및 전술적 기여도.
- 현지 유력 언론의 평점과 외신 평가 인용.

<h2>(국내외 프로야구: 순위 싸움 분수령과 투타 맞대결)</h2>
- KBO 리그 및 메이저리그(MLB) 주요 경기 승부처와 승리투수·타선 활약.
- 가을야구 및 포스트시즌 진출을 둘러싼 치열한 순위 경쟁 해설.

<h2>(코트 & 필드: 농구·배구·골프 주요 경기 명장면)</h2>
- 프로농구, 프로배구, 골프 투어 등의 명승부와 결정적 플레이 분석.

<h2>(주요 경기 스코어보드 및 매치업 일정)</h2>
- 주요 경기 최종 결과 요약 및 내일 주목해야 할 빅매치 프리뷰.

<h2>(향후 판도 분석 및 내일의 관전 포인트)</h2>
- 각 팀과 선수들의 차기 경기 전략 및 리그 순위 경쟁 전망.
- 오늘 스포츠계를 관통하는 인상적인 결론 한줄평 (<blockquote> 활용).

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

    print(f"[기자 리포트] {edition_kr} 스포츠 심층 경기 분석 기사 작성 중...")
    body = _call_gemini(prompt)

    # 기계적인 스크래퍼 테이블 및 AI 문구 전면 제거, 정통 언론사 바이라인 적용
    header_html = f"""
<p><strong>[머니노트365 스포츠부 = 현장취재팀]</strong> {date_kr} ({edition_kr} 종합)</p>
<hr>
"""

    footer_html = f"""
<hr>
<p><strong>[머니노트365 스포츠국 데스크]</strong> 저작권자 © 머니노트365 무단전재 및 재배포 금지</p>
<p><strong>🔗 관련 심층 기사:</strong>
<a href="{SITE_URL}/category/sports/">스포츠 뉴스</a> |
<a href="{SITE_URL}/category/entertainment/">연예·엔터테인먼트</a> |
<a href="{SITE_URL}/category/morning-news/">모닝 뉴스</a> |
<a href="{SITE_URL}/category/daily-report/">일일 투자 보고서</a>
</p>
"""

    full_html = f"{header_html}\n{body}\n{footer_html}"
    print(f"  [OK] 스포츠 전문 기사 생성 완료 ({len(full_html):,}자)")
    return full_html


def generate_sports_title(news_data: dict = None, edition: str = None) -> str:
    """실시간 스포츠 핫이슈를 반영한 박진감 넘치는 스포츠 신문 헤드라인 생성"""
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()
    ed_label = "아침" if edition == "morning" else "저녁"
    date_str = now.strftime(f"%Y.%m.%d({wd})")

    if news_data and news_data.get("all_items"):
        top_news = "\n".join([f"- {it.get('title')}" for it in news_data.get("all_items")[:10]])
        prompt = f"""
당신은 대한민국 스포츠 전문 일간지 1면 톱기사 헤드라인을 뽑는 20년 차 스포츠부 부장입니다.
오늘 취재된 다음 스포츠계 주요 기사 목록을 바탕으로, 오늘 가장 팬들의 가슴을 뛰게 한 핫매치를 담은 날카롭고 박진감 넘치는 1면 기사 제목 1개를 작성하세요.

취재 기사 목록:
{top_news}

조건:
1. 말머리는 [{date_str} {ed_label}] 로 시작할 것.
2. 경기 결과, 명승부, 주요 선수의 이름이 담긴 정통 스포츠 헤드라인 (35자 내외).
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
        return f"[{date_str} 아침] [스포츠 현장] 손흥민·해외파 맹활약 속 승전보… 가을야구 티켓 전쟁 '점화'"
    else:
        return f"[{date_str} 저녁] [스포츠 결산] 각본 없는 드라마 펼쳐진 명승부… 오늘 밤 프로야구·유럽축구 총결산"


def generate_sports_excerpt(edition: str = None) -> str:
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()

    ed_text = "아침" if edition == "morning" else "저녁"
    return (
        f"{now.strftime('%Y년 %m월 %d일')}({wd}) {ed_text} 기준, 오늘 스포츠 팬들의 이목이 집중된 "
        f"결정적 승부처와 해외파 활약상, 프로야구 및 메이저리그 경기 결과를 스포츠 전문 기자의 시각으로 생생하게 전한다."
    )
