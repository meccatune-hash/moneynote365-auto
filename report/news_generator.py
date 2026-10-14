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
당신은 뉴욕 월스트리트와 런던 금융지구를 직접 발로 뛰며 글로벌 시장을 취재해 온 20년 차 국제금융 전문 대기자이자 특파원입니다.
AI가 쓴 듯한 뻔한 나열식 요약문, 기계적인 설명투, 인터넷 블로그 정리글 느낌을 철저하게 배제하고,
실제 경제 일간지 1면과 글로벌 마켓 지면에 실리는 날카롭고 현장감 넘치는 정통 '뉴욕 특파원 심층 외신 분석 기사'를 작성하세요.

=== 오늘 새벽 뉴욕·런던 등 해외 주요 외신 보도 팩트 목록 ===
{news_list}

=== [필수] 국제경제 전문 기자식 필체 및 보도 10대 준칙 ===
1. [정통 기사체 평서문 철저 준수]:
   - 반드시 문미 종결형을 '~다', '~했다', '~밝혔다', '~전했다', '~설명했다', '~로 풀이된다', '~에 무게가 실린다', '~라는 관측이다', '~지적이다' 등 공인된 신문 기사체로 일관할 것.
   - 경어체('~입니다', '~해요', '~알아보겠습니다')나 안내원 톤('~소개해 드립니다')은 절대 사용 금지.
2. [AI 클리셰 원천 배제]:
   - 서두에 "안녕하세요", "오늘 알아볼 뉴스는", "최근 뉴욕증시가 뜨겁게 달아오르고 있습니다" 등 상투적 인사말 절대 금지.
   - 말미에 "지금까지 ~에 대해 알아보았습니다", "도움이 되셨나요?", "성투하세요" 등 블로그식 마무리 절대 금지.
   - "뜨거운 감자", "초미의 관심사", "귀추가 주목된다", "발빠른 대처" 등 판에 박힌 AI 관용구 남발 금지.
3. [6하원칙에 입각한 뉴욕 특파원 리드문(Lead)]:
   - 첫 문장은 오늘 새벽 뉴욕증시와 글로벌 매크로 환경을 뒤흔든 가장 결정적인 단일 팩트를 묵직하고 강렬하게 압축 제시하는 정통 특파원 리드문으로 시작할 것.
4. [생생한 월가 전문가 멘트 및 외신 인용(Quotes)]:
   - 월가 주요 투자은행(골드만삭스, JP모건 등) 수석 이코노미스트, 연준 당국자 발언, 블룸버그/로이터 원문 보도를 따옴표(" ")로 사실감 있게 인용할 것.
   - 예: 월가의 한 수석 이코노미스트는 "..."라고 진단했다. / 연준 고위 관계자는 "..."라며 매파적 기조를 재확인했다.
5. [신문사 지면 스타일의 세련된 기사 소제목]:
   - "🌅 1. 핵심 요약", "📰 2. 경제 뉴스", "❓ Q&A" 같은 유치한 번호 매기기나 이모지 나열 금지.
   - 실제 경제지 글로벌 마켓면에 들어갈 법한 품격 있는 기사 표제(<h2>, <h3>)를 부여할 것.
6. [풍부한 분량과 국내 시장에 미칠 파장 분석]:
   - 본문 분량은 공백 제외 최소 4,000자 이상으로 뉴욕 증시 종목별 등락 요인, 연준 통화정책 기조, 지정학 리스크, 그리고 이것이 오늘 개장할 한국 코스피·코스닥 시장에 미칠 영향을 치밀하게 짚을 것.
7. [WAF 방화벽 보안 태그]:
   - 순수 HTML만 사용: <h2>, <h3>, <p>, <ul>, <li>, <ol>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <blockquote>, <strong>, <em>, <hr>
   - style 속성, div, span, img, script, iframe 절대 금지. 마크다운 기호 없이 순수 HTML만 출력.

=== 기사 구성 가이드 (글로벌 마켓 심층 분석) ===

<h2>(오늘 새벽 글로벌 금융시장을 뒤흔든 핵심 승부처 헤드라인)</h2>
- 간밤 뉴욕증시 3대 지수와 국채금리, 달러 인덱스를 움직인 결정적 요인 심층 분석.
- 주요 지표 발표 결과와 시장 반응 팩트 보도.

<h2>(월가 포커스: 빅테크 실적 모멘텀과 기술주 향방)</h2>
- 엔비디아, 애플, 마이크로소프트 등 M7 종목들의 주요 이슈와 AI 반도체 밸류체인 동향.
- 월가 주요 IB들의 투자의견 및 목표주가 조정 내역.

<h2>(연준 통화정책 레이더: 금리 경로와 매크로 지표 점검)</h2>
- 파월 의장 및 FOMC 위원들의 최근 발언 분석, CPI·PPI·고용지표 발표 파장.
- 채권 금리 추이 및 금리 인하/동결 시나리오별 파급 효과.

<h2>(지정학 리스크 및 글로벌 원자재·환율 동향)</h2>
- 유가(WTI), 금값, 원달러 환율 등 핵심 원자재 및 통화 시장 움직임.

<h2>(오늘의 개장 체크포인트: 한국 증시 영향 및 섹터별 대응)</h2>
- 간밤 외신이 오늘 국내 KOSPI, KOSDAQ 시장 및 주요 업종(반도체, 2차전지, 자동차 등)에 미칠 직간접 영향.

<h2>(글로벌 마켓 총평 및 투자 관전 포인트)</h2>
- 오늘 하루 글로벌 투자자들이 예의주시해야 할 분수령 이벤트.
- 시장을 관통하는 통찰력 있는 한줄 결론 (<blockquote> 활용).

출력: 순수 HTML만 출력
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
    for item in news_data.get("all_items", [])[:50]:
        source = item.get("source", "")
        title  = item.get("title", "")
        desc   = item.get("desc", "")[:150]
        news_lines.append(f"[{source}] {title}\n  요약: {desc}\n")

    if not news_lines:
        news_lines = ["뉴스 수집에 실패했습니다. 최근 주요 글로벌 경제 뉴스를 바탕으로 작성해주세요."]

    news_list = "\n".join(news_lines)

    print(f"[특파원 리포트] {date_kr} 글로벌 금융 심층 분석 기사 작성 중...")
    body = _call_gemini(MORNING_NEWS_PROMPT.format(news_list=news_list))

    # 기계적인 스크래퍼 테이블 및 면책조항 전면 제거, 정통 언론사 바이라인 적용
    header_html = f"""
<p><strong>[머니노트365 뉴욕 특파원 = 글로벌 금융 데스크]</strong> {date_kr} (월가 모닝 브리핑)</p>
<hr>
"""

    footer_html = f"""
<hr>
<p><strong>[머니노트365 국제경제부]</strong> 저작권자 © 머니노트365 무단전재 및 재배포 금지</p>
<p><strong>🔗 관련 심층 리포트:</strong>
<a href="{SITE_URL}/category/daily-report/">일일 투자 보고서</a> |
<a href="{SITE_URL}/category/us-stock/">미국 주식</a> |
<a href="{SITE_URL}/category/economic-indicators/">경제 지표</a> |
<a href="{SITE_URL}/category/investment-strategy/">투자 전략</a>
</p>
"""

    full_html = f"{header_html}\n{body}\n{footer_html}"
    print(f"  [OK] 모닝 뉴스 전문 기사 생성 완료 ({len(full_html):,}자)")
    return full_html


def generate_news_title(news_data: dict = None) -> str:
    """새벽 월가 핫이슈를 담은 날카로운 경제지 1면 헤드라인 생성"""
    now = datetime.now(KST)
    wd  = WEEKDAYS[now.weekday()]
    date_str = now.strftime(f"%Y.%m.%d({wd})")

    if news_data and news_data.get("all_items"):
        top_news = "\n".join([f"- {it.get('title')}" for it in news_data.get("all_items")[:10]])
        prompt = f"""
당신은 대한민국 대표 경제지 1면 글로벌 마켓 헤드라인을 뽑는 20년 차 국제부장입니다.
오늘 새벽 타전된 주요 외신 뉴스 목록을 바탕으로, 오늘 한국 증시 개장을 앞둔 투자자들의 시선을 사로잡는 날카로운 신문 1면 기사 제목 1개를 작성하세요.

외신 기사 목록:
{top_news}

조건:
1. 말머리는 [{date_str}] 로 시작할 것.
2. 뉴욕증시 동향, 금리, 빅테크 움직임을 포착한 정통 경제 헤드라인 (35자 내외).
3. "총정리", "알아보자", "모닝 뉴스 브리핑" 같은 상투적이고 기계적인 블로그 문구 절대 금지.
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

    return f"[{date_str}] [글로벌 마켓] 美 연준 금리 경로 주시 속 빅테크 혼조… 뉴욕증시 향방은"


def generate_news_excerpt() -> str:
    now = datetime.now(KST)
    wd  = WEEKDAYS[now.weekday()]
    return (
        f"{now.strftime('%Y년 %m월 %d일')}({wd}) 뉴욕 금융시장 마감 기준, "
        f"미국 증시와 글로벌 매크로 지표의 주요 변동 요인을 뉴욕 특파원의 시각으로 심층 분석하고 한국 시장에 미칠 파장을 짚어본다."
    )
