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
당신은 대한민국 방송·가요·영화계를 20년간 밀착 취재해 온 베테랑 연예부 전문 기자이자 대중문화 수석 데스크입니다.
AI가 쓴 듯한 뻔한 가십 나열, 기계적인 요약, 인터넷 블로그 정리글 말투를 철저히 배제하고,
실제 신문사·연예전문 매체에 실리는 품격 있고 현장감 넘치는 정통 '연예부 기획 심층 보도 기사'를 작성하세요.

=== 오늘 취재된 연예계 팩트 및 보도 목록 ===
{news_list}

=== 발행 시점 ===
{edition_kr} 종합 (기준 시각: {now_time_str})

=== [필수] 연예부 전문 기자식 필체 및 보도 10대 준칙 ===
1. [정통 기사체 평서문 철저 준수]:
   - 문미 종결형을 반드시 '~다', '~했다', '~밝혔다', '~전했다', '~설명했다', '~로 풀이된다', '~에 관심이 쏠린다', '~라는 평가다' 등 공인된 신문 기사체로 일관할 것.
   - 친근한 척하는 경어체('~입니다', '~해요', '~알아보겠습니다')나 안내원 톤('~소개해 드립니다')은 절대 사용 금지.
2. [AI 클리셰 원천 배제]:
   - 서두에 "안녕하세요", "최근 연예계가 뜨겁게 달아오르고 있습니다", "오늘 알아볼 소식은" 등 상투적 인사말 절대 금지.
   - 말미에 "지금까지 ~에 대해 알아보았습니다", "도움이 되셨나요?", "댓글로 생각을 남겨주세요" 등 블로그식 마무리 절대 금지.
   - "뜨거운 감자", "초미의 관심사", "귀추가 주목된다", "눈길을 끈다" 등 뻔한 AI 관용구 남발 금지.
3. [6하원칙에 입각한 정통 취재 리드문(Lead)]:
   - 첫 문장은 오늘 연예계를 뜨겁게 달군 가장 결정적인 팩트를 담담하면서도 임팩트 있게 압축 제시하는 정통 스트레이트 기사 리드문으로 시작할 것.
4. [생생한 업계 관계자 및 당사자 발언 인용(Quotes)]:
   - 소속사 공식 입장, 제작진 인터뷰, 방송 관계자 및 대중문화 평론가의 발언을 따옴표(" ")로 사실감 있게 인용할 것.
   - 예: 소속사 측 관계자는 "..."라고 공식 입장을 밝혔다. / 대중문화 평론가는 "..."라고 분석했다.
5. [신문사 지면 스타일의 세련된 기사 소제목]:
   - "🌟 1. 오늘의 핫이슈 TOP 기사", "🎬 2. 방송가 하이라이트", "❓ Q&A" 같은 유치한 번호 매기기나 이모지 나열 금지.
   - 실제 일간지 연예면과 문화면에 들어갈 법한 품격 있는 기사 표제(<h2>, <h3>)를 부여할 것.
6. [풍부한 분량과 입체적 시각]:
   - 본문 분량은 공백 제외 최소 3,500자 이상으로 사건의 내막, 방송가/가요계 반응, 글로벌 K-컬처 시장 파급력, 향후 작품 및 활동 전망을 입체적으로 다룰 것.
7. [WAF 방화벽 보안 태그]:
   - 순수 HTML만 사용: <h2>, <h3>, <p>, <ul>, <li>, <ol>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <blockquote>, <strong>, <em>, <hr>
   - style 속성, div, span, img, script, iframe 절대 금지. 마크다운 기호 없이 순수 HTML만 출력.

=== 기사 구성 가이드 (연예문화 심층 종합) ===

<h2>(오늘 연예계 최대 화제작·사건을 압축한 핵심 헤드라인)</h2>
- 오늘 연예계 최대 핫이슈의 발단과 전개 과정 상세 취재 보도.
- 소속사·제작사 공식 입장 및 핵심 당사자 발언 인용.

<h2>(방송가 레이더: 화제의 드라마·예능 승부처와 시청률 격전)</h2>
- 주요 지상파·종편·케이블 드라마/예능의 화제 장면과 연출 포인트.
- 출연진 활약상 및 시청자 반응 분석.

<h2>(K-POP 글로벌 마켓: 음원 차트 돌풍과 신보 모멘텀)</h2>
- 국내외 음원·음반 차트(빌보드, 오리콘 등) 성과 및 글로벌 월드투어 동향.
- 컴백 아티스트의 음악적 변신과 프로듀싱 분석.

<h2>(스크린 & 글로벌 OTT: 극장가 박스오피스와 K-콘텐츠 신작)</h2>
- 극장가 흥행 성적과 넷플릭스·디즈니+ 등 OTT 글로벌 랭킹 추이.

<h2>(팬덤 여론과 문화적 시사점)</h2>
- 온라인 팬덤 커뮤니티의 능동적 반응과 대중문화적 의미 고찰.

<h2>(향후 활동 일정 및 차기 관전 포인트)</h2>
- 후속 작품 개봉, 시상식, 추가 입장 발표 등 주목할 일정.
- 오늘 연예계 흐름을 짚는 묵직한 결론 한줄평 (<blockquote> 활용).

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

    print(f"[기자 리포트] {edition_kr} 연예·엔터테인먼트 심층 기사 작성 중...")
    body = _call_gemini(prompt)

    # 기계적인 스크래퍼 테이블 및 AI 문구 전면 제거, 정통 언론사 바이라인 적용
    header_html = f"""
<p><strong>[머니노트365 연예부 = 방송·가요 취재팀]</strong> {date_kr} ({edition_kr} 종합)</p>
<hr>
"""

    footer_html = f"""
<hr>
<p><strong>[머니노트365 연예문화부 데스크]</strong> 저작권자 © 머니노트365 무단전재 및 재배포 금지</p>
<p><strong>🔗 관련 심층 기사:</strong>
<a href="{SITE_URL}/category/entertainment/">연예·엔터테인먼트</a> |
<a href="{SITE_URL}/category/sports/">스포츠 뉴스</a> |
<a href="{SITE_URL}/category/morning-news/">모닝 뉴스</a> |
<a href="{SITE_URL}/category/daily-report/">일일 투자 보고서</a>
</p>
"""

    full_html = f"{header_html}\n{body}\n{footer_html}"
    print(f"  [OK] 연예 전문 기사 생성 완료 ({len(full_html):,}자)")
    return full_html


def generate_entertainment_title(news_data: dict = None, edition: str = None) -> str:
    """실시간 연예 핫이슈를 반영한 매력적인 언론사 헤드라인 생성"""
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()
    ed_label = "아침" if edition == "morning" else "저녁"
    date_str = now.strftime(f"%Y.%m.%d({wd})")

    if news_data and news_data.get("all_items"):
        top_news = "\n".join([f"- {it.get('title')}" for it in news_data.get("all_items")[:10]])
        prompt = f"""
당신은 대한민국 연예 전문 매체 1면 헤드라인을 뽑는 20년 차 연예부 부장입니다.
오늘 취재된 다음 연예계 주요 기사 목록을 바탕으로, 오늘 가장 대중의 시선이 집중된 핫이슈를 담은 날카롭고 매력적인 1면 기사 제목 1개를 작성하세요.

취재 기사 목록:
{top_news}

조건:
1. 말머리는 [{date_str} {ed_label}] 로 시작할 것.
2. 팩트와 현장감이 살아있는 정통 연예부 헤드라인 (35자 내외).
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
        return f"[{date_str} 아침] [연예 와이드] 음원 차트 지각변동 속 스타들의 컴백 러시… K-콘텐츠 열풍"
    else:
        return f"[{date_str} 저녁] [연예 결산] 화제의 신작 돌풍과 연예계 빅이슈… 오늘 밤 가요·방송 하이라이트"


def generate_entertainment_excerpt(edition: str = None) -> str:
    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    if not edition:
        edition = get_current_edition()

    ed_text = "아침" if edition == "morning" else "저녁"
    return (
        f"{now.strftime('%Y년 %m월 %d일')}({wd}) {ed_text} 기준, 오늘 연예계에서 가장 뜨겁게 화제가 된 "
        f"핵심 스타들의 소식과 K-POP 신보, 화제의 방송·드라마를 연예 전문 기자의 시각으로 심층 분석 보도한다."
    )
