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
당신은 대한민국 주요 일간지 및 경제지의 20년 차 베테랑 기획취재 전문 기자이자 데스크입니다.
AI가 쓴 것 같은 기계적인 설명문이나 블로그 정리글 느낌을 철저히 배제하고,
실제 신문사·통신사 전문 기자가 현장을 발로 뛰며 직접 취재하고 깊이 있게 해설한 정통 '기획 심층 르포/해설 기사'를 작성하세요.

=== 실시간 급상승 키워드 정보 ===
- 취재 키워드: {keyword}
- 화제도 및 검색 지표: {traffic_str}
- 취재 팩트 및 관련 보도 데이터:
{news_list}

=== 발행 시점 ===
{now_time_str}

=== [필수] 전문 기자식 필체 및 기사 작성 10대 원칙 ===
1. [기사체 평서문 철저 준수]:
   - 반드시 문미 종결형을 '~다', '~했다', '~밝혔다', '~전했다', '~설명했다', '~로 풀이된다', '~에 무게가 실린다', '~라는 분석이다', '~지적이다' 등 공인된 신문 기사체로 일관할 것.
   - 경어체('~입니다', '~해요', '~알아보겠습니다'), 안내원 톤('~살펴보겠습니다', '~소개해 드립니다')은 절대 사용 금지.
2. [AI 클리셰 원천 배제]:
   - 첫머리에 "안녕하세요", "최근 ~가 뜨거운 화제가 되고 있습니다", "포털을 달군 ~에 대해 알아보겠습니다" 같은 상투적 도입문 절대 금지.
   - 말미에 "지금까지 ~에 대해 알아보았습니다", "도움이 되셨나요?", "댓글로 생각을 남겨주세요", "투자의 책임은 본인에게 있습니다" 같은 블로그식 마무리 절대 금지.
   - "뜨거운 감자", "초미의 관심사", "발빠른 대처", "눈길을 끈다" 등의 판에 박힌 AI 수식어 남발 금지.
3. [6하원칙에 입각한 강렬한 리드문(Lead)]:
   - 기사 첫 단락은 누가, 언제, 어디서, 무엇을, 어떻게, 왜에 입각하여 사건의 핵심 팩트와 충격을 압축 제시하는 정통 스트레이트 기사 리드문으로 시작할 것.
   - 기사 도입부 서두에 기자 바이라인 명시 (예: `<p><strong>[머니노트365 기획취재팀]</strong></p>`).
4. [생생한 인용문(Quotes)과 취재원 명시]:
   - 실제 기사처럼 관련 업계 고위 관계자, 주무 부처 당국자, 증권가 애널리스트, 분야별 학계 전문가의 발언을 따옴표(" ")로 사실감 있게 인용할 것.
   - 예: 업계의 한 관계자는 "..."라고 전했다. / 법조계 전문가는 "..."라고 지적했다.
5. [신문 헤드라인형 소제목]:
   - "🔥 1. 왜 지금 화제인가?", "📌 2. 핵심 팩트 완벽 정리", "❓ 5. FAQ" 같은 유치한 번호 매기기나 이모지 나열 금지.
   - 실제 경제지·일간지 1면과 기획면에 들어갈 법한 세련되고 통찰력 있는 기사 소제목(<h2>, <h3>) 사용.
6. [풍부한 분량과 입체적 분석]:
   - 본문 텍스트 분량은 공백 제외 최소 3,000자 ~ 4,500자 이상으로 사건의 발단, 심층 배경, 여론과 이해관계자 반응, 산업/사회적 파급효과, 향후 전개 관전 포인트를 입체적으로 파헤칠 것.
7. [WAF 방화벽 보안 태그 규칙]:
   - 순수 HTML만 사용: <h2>, <h3>, <p>, <ul>, <li>, <ol>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <blockquote>, <strong>, <em>, <hr>
   - style 속성, div, span, img, script, iframe 절대 금지. 마크다운(```html) 없이 순수 HTML만 출력.

=== 기사 구성 가이드 (기자식 기획 르포 포맷) ===

<p><strong>[머니노트365 기획취재팀]</strong></p>
(사건의 본질을 관통하는 6하 원칙 압축 리드문 단락)

<h2>(사건의 발단과 전면화 과정을 압축한 기사 소제목)</h2>
- 이슈가 촉발된 결정적 트리거와 구체적인 정황 팩트 상세 보도.

<h2>(이해관계자 입장과 구체적 팩트 타임라인)</h2>
- 확인된 공식 발표, 수치 데이터, 당사자들의 상반된 입장 및 공식 해명.
- 표(<table>) 또는 일자별 타임라인 활용.

<h2>(현장 여론 및 업계 안팎의 반응)</h2>
- 현장에서 체감하는 대중과 소비자의 반응, 주요 커뮤니티의 여론 분출 양상.
- 관련 업계 관계자 및 실무진의 생생한 내부 반응 인용.

<h2>(구조적 시사점과 산업·사회에 미칠 파장)</h2>
- 이번 사안이 단발성 이슈를 넘어 제도, 산업 생태계, 시장 전반에 미칠 중장기적 나비효과.
- 분야별 수석 연구원/전문가의 분석적 코멘트 인용.

<h2>(쟁점 분석: 사실과 오해, 핵심 쟁점 심층 문답)</h2>
- 독자나 대중이 가장 오해하기 쉽거나 혼선을 빚는 핵심 쟁점 3가지를 기자가 직접 팩트체크하는 심층 Q&A.

<h2>(향후 분수령 및 관전 포인트)</h2>
- 앞으로 예정된 중대 결정, 사법적/행정적 절차, 시장의 향방.
- 이번 사안을 관통하는 묵직한 결론 한줄평 (<blockquote> 활용).

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
    """베테랑 언론사 데스크 스타일의 품격 있고 흡인력 강한 기사 표제(헤드라인) 생성"""
    prompt = f"""
당신은 대한민국 일간지·경제지 1면 헤드라인을 뽑는 20년 차 편집 데스크입니다.
다음 실시간 급상승 키워드와 취재 정보를 바탕으로, AI가 지은 것 같은 블로그식 낚시성 제목("🔥 [실시간 트렌드] 키워드의 모든 것 총정리")을 절대 쓰지 말고,
독자의 시선을 사로잡는 정통 언론사 단독/기획 기사형 표제 1개를 작성하세요.

키워드: {keyword}
관련 취재 팩트:
{news_list_str[:500]}

조건:
1. 반드시 키워드 "{keyword}"를 핵심 주어/목적어로 자연스럽게 포함할 것.
2. 언론사 머리말 말머리 [이슈분석], [초점], [단독], [현장], [기획] 중 1개를 적절히 선택하여 시작.
3. 팩트와 수치, 혹은 긴장감 있는 대립 구도를 담아 35자 내외로 간결하고 묵직하게 작성.
4. "총정리", "알아보자", "이유는?", "확인 필수" 같은 싸구려 블로그 어투 절대 금지.
5. 따옴표나 군더더기 없이 헤드라인 문자열 1줄만 정확히 출력.
"""
    try:
        resp = _client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        title = resp.text.strip().replace('"', '').replace("'", "")
        title = title.split("\n")[0].strip()
        if keyword in title and len(title) >= 10:
            return title
    except Exception:
        pass
    return f"[이슈분석] {keyword} 급부상 배경과 업계 안팎에 미치는 파장"


def generate_trend_excerpt(keyword: str, title: str) -> str:
    """기사 서두 전문(리드문) 스타일의 품격 있는 1~2줄 요약문"""
    prompt = f"""
제목: {title}
키워드: {keyword}

위 기사의 핵심 팩트와 시사점을 신문사 1면 리드문(전문) 스타일로 80~120자 내외(1~2문장)로 작성하세요.
"총정리해 드립니다", "알아보겠습니다" 같은 블로그 말투는 절대 쓰지 말고, 정통 기사체(~다)로 작성하세요.
설명이나 기호 없이 요약문 텍스트만 출력하세요.
"""
    try:
        resp = _client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        excerpt = resp.text.strip().split("\n")[0].strip()
        if len(excerpt) > 20:
            return excerpt
    except Exception:
        pass
    return f"최근 화제의 중심에 선 '{keyword}' 사안의 구체적 전개 과정과 핵심 쟁점, 그리고 향후 관련 시장과 산업에 미칠 파장을 심층 보도한다."


def generate_trend_tags(keyword: str) -> list:
    """트렌드 기사에 부여할 추천 태그 목록 (최대 7개)"""
    base_tags = [keyword, "트렌드이슈", "실시간검색어", "핫이슈", "실시간트렌드", "인기검색어", "화제"]
    return base_tags


def make_image_block(img_dict: dict, default_caption: str = "") -> str:
    """WAF 안전한 표준 워드프레스 이미지 블록 생성"""
    img_id = img_dict.get("id", "")
    url = img_dict.get("url", "")
    caption = img_dict.get("caption") or default_caption
    source = img_dict.get("source", "언론사 보도자료")
    return f"""
<!-- wp:image {{"id":{img_id},"sizeSlug":"large","linkDestination":"none"}} -->
<figure class="wp-block-image size-large">
<img src="{url}" alt="{caption}" />
<figcaption>▲ {caption} (사진 출처: {source})</figcaption>
</figure>
<!-- /wp:image -->
"""


def build_trend_post(trend_item: dict, uploaded_images: list = None) -> dict:
    """
    개별 트렌드 아이템을 받아 완성된 WordPress 포스팅 데이터 딕셔너리 생성
    - title
    - content (WAF 호환 HTML + 관련 사진 2~3장 포함)
    - excerpt
    - tags
    - featured_media_id (대표 썸네일)
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

    # 상단 요약 배지 HTML
    header_html = f"""
<blockquote>
<p><strong>🔥 실시간 트렌드 핫이슈 브리핑</strong></p>
<p><strong>키워드:</strong> {keyword} &nbsp;|&nbsp; <strong>화제도(검색량):</strong> {traffic_str} &nbsp;|&nbsp; <strong>기준 일시:</strong> {now_time_str}</p>
<p><em>본 기사는 포털 사이트 및 구글 트렌드 실시간 급상승 빅데이터와 언론 보도 팩트를 종합하여 머니노트365 AI 트렌드 분석팀이 심층 분석한 리포트입니다.</em></p>
</blockquote>
<hr>
"""

    # 이미지 본문 적절한 위치에 삽입
    featured_media_id = None
    if uploaded_images and len(uploaded_images) > 0:
        featured_media_id = uploaded_images[0]["id"]

        # 사진 1: 상단 헤더 바로 아래 대표 사진
        img1_html = make_image_block(uploaded_images[0], f"'{keyword}' 관련 대표 현장 사진")
        header_html += img1_html

        # 사진 2: 팩트 정리 후(네티즌 반응 앞) 삽입
        if len(uploaded_images) > 1:
            img2_html = make_image_block(uploaded_images[1], f"'{keyword}' 핵심 사건 관련 보도 현장")
            if "<h2>💬 3." in body_html:
                body_html = body_html.replace("<h2>💬 3.", f"{img2_html}\n<h2>💬 3.")
            elif "<h2>3." in body_html:
                body_html = body_html.replace("<h2>3.", f"{img2_html}\n<h2>3.")
            else:
                body_html = img2_html + body_html

        # 사진 3: FAQ 직전 삽입
        if len(uploaded_images) > 2:
            img3_html = make_image_block(uploaded_images[2], f"'{keyword}' 대중 반응 및 현장 이모저모")
            if "<h2>❓ 5." in body_html:
                body_html = body_html.replace("<h2>❓ 5.", f"{img3_html}\n<h2>❓ 5.")
            elif "<h2>5." in body_html:
                body_html = body_html.replace("<h2>5.", f"{img3_html}\n<h2>5.")
            else:
                body_html += img3_html

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
        "featured_media_id": featured_media_id,
    }
