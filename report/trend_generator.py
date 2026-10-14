# -*- coding: utf-8 -*-
"""
실시간 급상승 트렌드 AI 포스팅 생성기 (report/trend_generator.py)
- 실시간 최상위 검색어 기반 단독 심층 기사 생성
- 최고 조회율(CTR) 및 구글/네이버 SEO 최적화 프롬프트
- 사실 기반 팩트 체크 + 네티즌 반응 + 전문가 분석 + FAQ 포함
- WordPress NinjaFirewall 완벽 호환 (WAF 안전 HTML)
"""
import os
import re
import json
from datetime import datetime, timezone, timedelta
from google import genai
from dotenv import load_dotenv

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

KST = timezone(timedelta(hours=9))
SITE_URL = os.getenv("WP_URL", "https://kingbrightsucces.com")
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

TREND_ARTICLE_PROMPT = """
당신은 대한민국 최고의 디지털 미디어 트렌드 분석가이자 바이럴 SEO 콘텐츠 총괄 에디터입니다.
현재 대한민국에서 실시간 검색량과 관심도가 폭발하고 있는 핫트렌드 키워드와 관련 뉴스 정보를 바탕으로,
포털 사이트와 구글 검색에서 최고 조회율을 기록할 수 있는 프리미엄 심층 트렌드 포스팅을 작성하세요.

=== 실시간 급상승 키워드 정보 ===
- 키워드: {keyword}
- 예상 검색량/화제도: {traffic_str}
- 관련 뉴스 기사 및 팩트 데이터:
{news_list}

=== 기준 일시 ===
{now_time_str}

=== 작성 원칙 및 품질 기준 ===
1. 클릭률(CTR)과 체류 시간을 극대화하는 매력적인 스토리텔링과 신뢰도 높은 팩트 전달.
2. 텍스트 분량: 최소 3,000자 ~ 4,500자 이상의 매우 풍부하고 깊이 있는 구성.
3. 순수 HTML 태그만 사용할 것: <h2>, <h3>, <p>, <ul>, <li>, <ol>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <blockquote>, <strong>, <em>, <hr>
4. style 속성, script, div, span, img, iframe 절대 금지 (WordPress WAF 방화벽 보안 호환)
5. 마크다운 기호(```html) 없이 순수 HTML 본문만 출력할 것.

=== 필수 목차 구조 (본문에 순서대로 충실히 반영) ===

<h2>🔥 1. 실시간 검색어 급상승: 왜 지금 화제인가?</h2>
- 키워드가 갑자기 실시간 검색어 상위에 오르고 포털을 뜨겁게 달군 결정적인 발단과 배경.
- 대중들의 이목이 집중된 핵심 계기 설명.

<h2>📌 2. 핵심 팩트 완벽 정리 & 타임라인</h2>
- 지금까지 확인된 구체적인 사건 전개, 공식 발표, 주요 수치 및 데이터.
- 관련 당사자 및 기관들의 입장과 주요 발언.

<h2>💬 3. 네티즌 반응 및 온라인 커뮤니티 여론 동향</h2>
- 주요 온라인 커뮤니티, SNS, 포털 댓글에서 나타난 대중들의 생생한 여론과 상반된 반응.
- 화제가 되고 있는 주요 쟁점과 논란 포인트.

<h2>💡 4. 전문가 시각 & 관련 분야에 미치는 파급 효과</h2>
- 이번 이슈가 해당 분야(경제, 산업, 연예, 스포츠 등)나 일상생활에 미칠 직간접적 파장.
- 놓치지 말아야 할 구조적 시사점과 맥락 해설.

<h2>❓ 5. 가장 많이 묻는 질문 FAQ BEST 3</h2>
- 이 이슈와 관련해 네티즌들이 가장 궁금해하는 핵심 질문 3가지와 명쾌한 답변 (Q&A 형식).

<h2>🔮 6. 향후 일정 및 관전 포인트 (총평)</h2>
- 앞으로 예정된 주요 발표, 경기, 후속 조치 등 주목해야 할 일정.
- 이번 트렌드를 바라보는 균형 잡힌 결론 한줄평 (<blockquote> 활용).

출력 형식: 순수 HTML만 바로 출력하세요.
"""


def _call_gemini(prompt: str) -> str:
    """Gemini API 호출 및 마크다운 정리"""
    models = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.5-pro"]
    for model in models:
        try:
            resp = _client.models.generate_content(model=model, contents=prompt)
            text = resp.text.strip()
            text = re.sub(r"^```html?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```\s*$", "", text)
            if len(text) > 400:
                return text.strip()
        except Exception as e:
            print(f"  [AI 모델 {model}] 오류: {str(e)[:80]}")
            continue
    return "<p>트렌드 콘텐츠 생성 중 일시적인 오류가 발생했습니다. 잠시 후 갱신됩니다.</p>"


def generate_trend_title(keyword: str, news_list_str: str) -> str:
    """클릭률(CTR)과 검색 노출을 극대화하는 매력적인 제목 생성"""
    prompt = f"""
다음 실시간 급상승 키워드와 관련 뉴스 정보를 바탕으로, 독자의 호기심을 자극하고 구글/네이버 포털 검색에서 클릭률(CTR)이 가장 높은 매력적인 블로그 포스팅 제목 1개를 작성하세요.

키워드: {keyword}
관련 뉴스:
{news_list_str[:500]}

조건:
1. 제목에 반드시 키워드 "{keyword}"가 자연스럽게 포함될 것.
2. 35자 내외의 직관적이고 임팩트 있는 문장.
3. "[실시간 트렌드]" 또는 "🔥" 머리말 포함 가능.
4. 큰따옴표나 부가 설명 없이 제목 문자열 1줄만 정확히 출력.
"""
    try:
        resp = _client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        title = resp.text.strip().replace('"', '').replace("'", "")
        # 첫 줄만 취함
        title = title.split("\n")[0].strip()
        if keyword in title and len(title) >= 10:
            return title
    except Exception:
        pass
    return f"🔥 [실시간 트렌드] {keyword} 화제의 결정적 이유 & 핵심 총정리"


def generate_trend_excerpt(keyword: str, title: str) -> str:
    """검색엔진 스니펫 및 메인 카드용 매력적인 2줄 요약문"""
    prompt = f"""
제목: {title}
키워드: {keyword}

위 트렌드 기사에 대한 검색엔진 요약문(메타 디스크립션)을 80~120자 내외로 1~2문장으로 작성하세요. 독자가 클릭하고 싶게 유도해야 합니다.
설명이나 기호 없이 요약문 텍스트만 출력하세요.
"""
    try:
        resp = _client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        excerpt = resp.text.strip().split("\n")[0].strip()
        if len(excerpt) > 20:
            return excerpt
    except Exception:
        pass
    return f"대한민국 실시간 검색어 급상승 키워드 '{keyword}' 화제의 배경과 핵심 팩트, 대중의 반응 및 향후 전망을 알기 쉽게 총정리해 드립니다."


def generate_trend_tags(keyword: str) -> list:
    """트렌드 기사에 부여할 추천 태그 목록 (최대 7개)"""
    base_tags = [keyword, "트렌드이슈", "실시간검색어", "핫이슈", "실시간트렌드", "인기검색어", "화제"]
    return base_tags


def build_trend_post(trend_item: dict) -> dict:
    """
    개별 트렌드 아이템을 받아 완성된 WordPress 포스팅 데이터 딕셔너리 생성
    - title
    - content (WAF 호환 HTML)
    - excerpt
    - tags
    """
    keyword = trend_item.get("keyword", "핫트렌드")
    traffic_str = trend_item.get("traffic_str", "1000+")
    news_items = trend_item.get("all_news", [])

    now = datetime.now(KST)
    wd = WEEKDAYS[now.weekday()]
    now_time_str = now.strftime(f"%Y년 %m월 %d일({wd}) %H:%M KST")

    news_lines = []
    for n in news_items[:8]:
        news_lines.append(f"[{n.get('source', '뉴스')}] {n.get('title', '')}\n요약: {n.get('desc', n.get('snippet', ''))}\n")
    news_list_str = "\n".join(news_lines) if news_lines else f"'{keyword}' 관련 실시간 검색어 급상승 핫이슈"

    print(f"\n[AI] '{keyword}' 트렌드 심층 기사 생성 중...")
    body_html = _call_gemini(
        TREND_ARTICLE_PROMPT.format(
            keyword=keyword,
            traffic_str=traffic_str,
            news_list=news_list_str,
            now_time_str=now_time_str,
        )
    )

    title = generate_trend_title(keyword, news_list_str)
    excerpt = generate_trend_excerpt(keyword, title)
    tags = generate_trend_tags(keyword)

    # 상단 요약 배지 HTML (WAF 호환: table과 blockquote 활용)
    header_html = f"""
<blockquote>
<p><strong>🔥 실시간 트렌드 핫이슈 브리핑</strong></p>
<p><strong>키워드:</strong> {keyword} &nbsp;|&nbsp; <strong>화제도(검색량):</strong> {traffic_str} &nbsp;|&nbsp; <strong>기준 일시:</strong> {now_time_str}</p>
<p><em>본 기사는 포털 사이트 및 구글 트렌드 실시간 급상승 빅데이터와 언론 보도 팩트를 종합하여 머니노트365 AI 트렌드 분석팀이 심층 분석한 리포트입니다.</em></p>
</blockquote>
<hr>
"""

    footer_html = f"""
<hr>
<blockquote>
<p><strong>💡 머니노트365 트렌드 인사이트:</strong> 실시간 급상승 키워드는 사회적 관심과 대중의 니즈를 가장 빠르게 보여주는 지표입니다. 본 정보는 최신 팩트를 기반으로 작성되었으며, 새로운 소식이 업데이트되는 대로 지속 갱신됩니다.</p>
<p>🔍 <strong>관련 태그:</strong> #{keyword} #트렌드이슈 #실시간검색어 #핫이슈 #실시간트렌드</p>
</blockquote>
"""

    full_content = header_html + body_html + footer_html

    return {
        "keyword": keyword,
        "title": title,
        "content": full_content,
        "excerpt": excerpt,
        "tags": tags,
    }
