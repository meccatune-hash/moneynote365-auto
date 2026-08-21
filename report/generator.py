# -*- coding: utf-8 -*-
"""
머니노트365 AI 보고서 생성기 v4
- Google SEO + AI SEO(GEO) + AdSense 완전 최적화
- E-E-A-T 구조 (경험·전문성·권위·신뢰)
- 구조화 데이터(JSON-LD) 포함
- FAQ 섹션으로 AI 검색 최적화
- 목차(TOC) 자동 생성
- 메타 데이터 완비
"""
import os, re
from datetime import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SITE_URL  = os.getenv("WP_URL", "https://kingbrightsucces.com")
SITE_NAME = "머니노트365"


# ──────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────
def pct_str(v):
    if v is None: return "N/A"
    v = float(v)
    arrow = "▲" if v >= 0 else "▼"
    sign  = "+" if v >= 0 else ""
    return f"{arrow} {sign}{v:.2f}%"


def format_market_data_for_prompt(us, kr, coin):
    lines = ["=== 오늘의 실제 시장 데이터 (정확히 반영해서 해설할 것) ===\n"]

    lines.append("【미국 주요 지수】")
    for name, d in us.get("indices", {}).items():
        if d and "error" not in d:
            lines.append(f"  {name}: {d['close']:,.2f}  {pct_str(d.get('change_pct'))}  고:{d.get('high',0):,.2f} / 저:{d.get('low',0):,.2f}")

    lines.append("\n【미국 선물】")
    for name, d in us.get("futures", {}).items():
        if d and "error" not in d:
            lines.append(f"  {name}: {d['close']:,.2f}  {pct_str(d.get('change_pct'))}")

    lines.append("\n【원자재】")
    for name, d in us.get("commodities", {}).items():
        if d and "error" not in d:
            lines.append(f"  {name}: {d['close']:,.2f}  {pct_str(d.get('change_pct'))}")

    lines.append("\n【환율】")
    for name, d in us.get("forex", {}).items():
        if d and "error" not in d:
            lines.append(f"  {name}: {d['close']:,.4f}  {pct_str(d.get('change_pct'))}")

    lines.append("\n【미국 섹터】")
    for name, d in us.get("sectors", {}).items():
        if d and "error" not in d:
            lines.append(f"  {name}: {pct_str(d.get('change_pct'))}")

    lines.append("\n【한국 증시】")
    kospi  = kr.get("kospi", {})
    kosdaq = kr.get("kosdaq", {})
    if kospi and "error" not in kospi:
        lines.append(f"  KOSPI:  {kospi['close']:,.2f}  {pct_str(kospi.get('change_pct'))}")
    if kosdaq and "error" not in kosdaq:
        lines.append(f"  KOSDAQ: {kosdaq['close']:,.2f}  {pct_str(kosdaq.get('change_pct'))}")
    for s in kr.get("top_stocks", []):
        lines.append(f"  {s['name']}: {s['close']:,.0f}원  {pct_str(s.get('change_pct'))}")

    lines.append("\n【암호화폐】")
    for cname, d in coin.get("coins", {}).items():
        if d and "error" not in d:
            lines.append(f"  {cname}: ${d.get('price_usd',0):,.2f}  24h:{pct_str(d.get('change_24h'))}")
    fg = coin.get("fear_greed", {})
    if fg:
        lines.append(f"  공포탐욕지수: {fg.get('value','N/A')} — {fg.get('classification_kr','N/A')}")

    return "\n".join(lines)


# ──────────────────────────────────────────────
# AI 프롬프트 (SEO + AI SEO 완전 최적화)
# ──────────────────────────────────────────────
SEO_PROMPT_TEMPLATE = """
당신은 금융 전문 애널리스트이자 SEO 전문 콘텐츠 작가입니다.
아래 실제 시장 데이터를 바탕으로 Google SEO, AI SEO(GEO), 구글 애드센스 승인 기준에 완전히 최적화된 투자 보고서를 작성하세요.

{market_data}

=== 글 작성 규칙 (반드시 준수) ===

1. 언어: 반드시 한국어로 작성 (영어 용어는 괄호로 병기)
2. 전체 분량: 최소 4,000자 이상의 본문 (HTML 태그 제외)
3. E-E-A-T 원칙 준수: 경험(Experience), 전문성(Expertise), 권위(Authority), 신뢰(Trust)

=== 콘텐츠 구조 (HTML로 작성) ===

아래 순서대로 HTML 섹션을 구성하세요. 각 섹션 ID는 반드시 포함:

① <section id="summary"> — 핵심 요약 (오늘의 TLDR)
   - 3~5개 불릿으로 오늘 시장 핵심 요약
   - 강조 박스 스타일 (background:#f0f7ff 또는 노란 배경)

② <section id="market-overview"> — 글로벌 시장 전체 흐름
   - 실제 수치 기반 분석 (정확한 포인트, 퍼센트 사용)
   - 원인 → 결과 → 영향 순서로 서술
   - "Yahoo Finance 데이터에 따르면..." 등 출처 명시

③ <section id="kr-market"> — 한국 증시 심층 분석
   - KOSPI/KOSDAQ 실제 수치 포함
   - 주요 종목 동향
   - 역사적 유사 사례 1개 이상 포함

④ <section id="us-market"> — 미국 증시 분석
   - 섹터별 강약 분석
   - 연준(Fed) 정책 관련 언급

⑤ <section id="crypto"> — 암호화폐 시장
   - BTC/ETH 실제 가격 포함
   - 공포탐욕지수 해석

⑥ <section id="commodities"> — 원자재 & 환율
   - 금, 오일, 달러 인덱스 분석

⑦ <section id="investment-insight"> — 투자 인사이트
   - 투자 대가 명언 1개 (blockquote 태그)
   - 구체적 근거 기반 관점 제시

⑧ <section id="faq"> — 자주 묻는 질문 (FAQ) ← AI SEO 핵심
   - 오늘 시장과 관련된 독자가 궁금해할 질문 5개
   - Q&A 형식으로 각각 3~5문장 답변
   - details/summary 태그 사용

⑨ <section id="disclaimer"> — 투자 유의사항

=== HTML 작성 규칙 ===
- 반드시 <h2>와 <h3>만 사용 (h1은 포스트 제목이 담당)
- 모든 이미지: alt 속성에 한국어 설명 포함
- 테이블: scope, header 속성 포함
- 링크: rel="nofollow" 또는 rel="noopener"
- <script>, <iframe> 태그 절대 사용 금지
- 줄바꿈을 <br> 대신 <p> 태그로
- 섹션마다 실제 수치(숫자%)가 1개 이상 포함

=== 제목 작성 규칙 (SEO) ===
- 제목은 별도로 생성하지 말 것 (제목은 시스템이 자동 생성)
- 본문 내 <h2>는 핵심 키워드 포함 (예: "KOSPI 분석", "비트코인 전망")

출력: 순수 HTML 코드만 출력 (```html ``` 마크다운 없이)
"""


def _call_gemini(prompt: str) -> str:
    try:
        resp = _client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return resp.text.strip()
    except Exception:
        pass
    try:
        resp = _client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        return resp.text.strip()
    except Exception as e:
        return f"<p>보고서 생성 오류: {e}</p>"


def _strip_md_fences(html: str) -> str:
    html = re.sub(r"^```html?\s*", "", html, flags=re.IGNORECASE)
    html = re.sub(r"\s*```\s*$", "", html)
    return html.strip()


def _build_toc(sections: list) -> str:
    """목차 HTML 생성"""
    items = "\n".join(
        f'<li><a href="#{sid}" style="color:#1d4ed8;text-decoration:none;">'
        f'<span style="color:#D4AF37;margin-right:0.5rem;">›</span>{label}</a></li>'
        for sid, label in sections
    )
    return f"""
<nav id="toc" aria-label="목차" style="background:#f8fafc;border:1px solid #e0e7ef;border-radius:10px;padding:1.5rem;margin:1.5rem 0;">
<h2 style="margin:0 0 1rem;font-size:1rem;color:#0A1628;font-weight:700;">📋 목차</h2>
<ol style="margin:0;padding-left:1.5rem;line-height:2.2;">{items}</ol>
</nav>"""


def _build_schema(title: str, date_str: str, description: str,
                  us: dict, kr: dict, coin: dict) -> str:
    """JSON-LD 구조화 데이터 - WordPress head에 추가 필요하지만
    post_meta로 저장해서 테마/플러그인이 처리하도록 함"""
    kospi_val = kr.get("kospi", {}).get("close", 0)
    sp500_val = us.get("indices", {}).get("S&P500", {}).get("close", 0)
    btc_val   = coin.get("coins", {}).get("bitcoin", {}).get("price_usd", 0)

    # FAQ 스키마용 데이터
    faq_items = [
        {
            "question": f"오늘 KOSPI는 얼마입니까?",
            "answer": f"오늘 KOSPI는 {kospi_val:,.2f}포인트를 기록했습니다. "
                      f"{kr.get('kospi',{}).get('change_pct',0):+.2f}% 등락했습니다."
        },
        {
            "question": f"S&P500 오늘 종가는 얼마입니까?",
            "answer": f"미국 S&P500은 {sp500_val:,.2f}포인트에 마감했습니다. "
                      f"{us.get('indices',{}).get('S&P500',{}).get('change_pct',0):+.2f}% 변동했습니다."
        },
        {
            "question": "오늘 비트코인 가격은 얼마입니까?",
            "answer": f"비트코인(BTC)은 현재 ${btc_val:,.0f} USD에 거래되고 있습니다."
        },
    ]

    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["answer"]
                }
            }
            for faq in faq_items
        ]
    }

    article_schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": title,
        "description": description,
        "datePublished": date_str,
        "dateModified": date_str,
        "author": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": SITE_URL
        },
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": SITE_URL,
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE_URL}/wp-content/uploads/mn365-logo.png"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": SITE_URL
        },
        "about": ["주식 시장", "코스피", "비트코인", "투자"],
        "inLanguage": "ko-KR",
        "isAccessibleForFree": True
    }

    import json
    return json.dumps({"faq": faq_schema, "article": article_schema},
                      ensure_ascii=False)


def generate_daily_report(us: dict, kr: dict, coin: dict,
                          media_html: dict = None) -> str:
    if media_html is None:
        media_html = {}

    today    = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    wd       = weekdays[today.weekday()]

    market_data = format_market_data_for_prompt(us, kr, coin)

    print("[AI] 상세 투자 보고서 생성 중...")
    ai_body = _call_gemini(SEO_PROMPT_TEMPLATE.format(market_data=market_data))
    ai_body = _strip_md_fences(ai_body)

    # ── 데이터 추출 ──────────────────────────────────
    kospi  = kr.get("kospi", {})
    kosdaq = kr.get("kosdaq", {})
    sp500  = us.get("indices", {}).get("S&P500", {})
    btc    = coin.get("coins", {}).get("bitcoin", {})
    fg     = coin.get("fear_greed", {})
    usdkrw = us.get("forex", {}).get("USD/KRW", {})
    gold   = us.get("commodities", {}).get("금(Gold)", {})

    sp_pct   = sp500.get("change_pct", 0) or 0
    ksp_pct  = kospi.get("change_pct", 0) or 0
    btc_pct  = btc.get("change_24h", 0) or 0

    def trend(v): return "상승" if float(v) >= 0 else "하락"
    market_mood = "글로벌 증시 혼조" if abs(sp_pct - ksp_pct) > 2 else (
        "글로벌 증시 상승" if sp_pct >= 0 and ksp_pct >= 0 else "글로벌 증시 약세"
    )

    title    = generate_title(us, kr, coin)
    excerpt  = generate_excerpt(us, kr, coin)

    # ── 목차 ─────────────────────────────────────────
    toc = _build_toc([
        ("summary",           "오늘의 핵심 요약"),
        ("market-overview",   "글로벌 시장 전체 흐름"),
        ("kr-market",         "한국 증시 심층 분석"),
        ("us-market",         "미국 증시 분석"),
        ("crypto",            "암호화폐 시장"),
        ("commodities",       "원자재 & 환율"),
        ("investment-insight","투자 인사이트"),
        ("faq",               "자주 묻는 질문 (FAQ)"),
    ])

    # ── 리드 섹션 (히어로 + 핵심 수치) ──────────────
    sp_color  = "#dc2626" if sp_pct  < 0 else "#16a34a"
    ksp_color = "#dc2626" if ksp_pct < 0 else "#16a34a"
    btc_color = "#dc2626" if btc_pct < 0 else "#16a34a"

    lead_html = f"""
<header class="report-header" style="background:#0A1628;color:white;padding:2.5rem 2rem;border-radius:14px;margin-bottom:2rem;">
  <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
    <span style="background:#D4AF37;color:#0A1628;font-size:0.75rem;font-weight:800;padding:0.25rem 0.75rem;border-radius:20px;">📔 일일 투자 보고서</span>
    <time datetime="{date_str}" style="color:#94a3b8;font-size:0.85rem;">{today.strftime('%Y년 %m월 %d일')} ({wd})</time>
  </div>
  <h1 style="color:#FFD700;font-size:1.5rem;font-weight:800;margin:0 0 0.75rem;line-height:1.3;">{title}</h1>
  <p style="color:#cbd5e1;margin:0;font-size:0.95rem;">{excerpt}</p>
</header>

<div class="market-ticker" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:0.75rem;margin-bottom:1.5rem;" aria-label="주요 지수 현황">
  <div style="background:white;border:1px solid #e0e7ef;border-radius:10px;padding:1rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
    <div style="font-size:0.75rem;color:#64748b;font-weight:600;">KOSPI</div>
    <div style="font-size:1.35rem;font-weight:800;color:#0A1628;">{kospi.get('close',0):,.2f}</div>
    <div style="font-size:0.9rem;font-weight:700;color:{ksp_color};">{ksp_pct:+.2f}%</div>
  </div>
  <div style="background:white;border:1px solid #e0e7ef;border-radius:10px;padding:1rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
    <div style="font-size:0.75rem;color:#64748b;font-weight:600;">S&amp;P500</div>
    <div style="font-size:1.35rem;font-weight:800;color:#0A1628;">{sp500.get('close',0):,.2f}</div>
    <div style="font-size:0.9rem;font-weight:700;color:{sp_color};">{sp_pct:+.2f}%</div>
  </div>
  <div style="background:white;border:1px solid #e0e7ef;border-radius:10px;padding:1rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
    <div style="font-size:0.75rem;color:#64748b;font-weight:600;">비트코인</div>
    <div style="font-size:1.35rem;font-weight:800;color:#0A1628;">${btc.get('price_usd',0):,.0f}</div>
    <div style="font-size:0.9rem;font-weight:700;color:{btc_color};">{btc_pct:+.2f}%</div>
  </div>
  <div style="background:white;border:1px solid #e0e7ef;border-radius:10px;padding:1rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
    <div style="font-size:0.75rem;color:#64748b;font-weight:600;">공포탐욕지수</div>
    <div style="font-size:1.35rem;font-weight:800;color:#0A1628;">{fg.get('value','N/A')}</div>
    <div style="font-size:0.9rem;font-weight:700;color:#64748b;">{fg.get('classification_kr','N/A')}</div>
  </div>
  <div style="background:white;border:1px solid #e0e7ef;border-radius:10px;padding:1rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
    <div style="font-size:0.75rem;color:#64748b;font-weight:600;">원/달러</div>
    <div style="font-size:1.35rem;font-weight:800;color:#0A1628;">{usdkrw.get('close',0):,.1f}</div>
    <div style="font-size:0.9rem;font-weight:700;color:#64748b;">원</div>
  </div>
  <div style="background:white;border:1px solid #e0e7ef;border-radius:10px;padding:1rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
    <div style="font-size:0.75rem;color:#64748b;font-weight:600;">금(Gold)</div>
    <div style="font-size:1.35rem;font-weight:800;color:#0A1628;">${gold.get('close',0):,.1f}</div>
    <div style="font-size:0.9rem;font-weight:700;color:'#16a34a' if gold.get('change_pct',0)>=0 else '#dc2626';">{gold.get('change_pct',0):+.2f}%</div>
  </div>
</div>

{media_html.get('main_image', '')}
"""

    # ── 읽기 예상 시간 ────────────────────────────────
    word_count   = len(ai_body) // 2
    reading_min  = max(1, word_count // 400)
    reading_info = f"""
<div style="display:flex;gap:1rem;align-items:center;font-size:0.82rem;color:#64748b;margin-bottom:1.5rem;padding:0.75rem 1rem;background:#f8fafc;border-radius:8px;border:1px solid #e0e7ef;">
  <span>🕐 읽기 예상 시간: <strong>{reading_min}분</strong></span>
  <span>·</span>
  <span>📊 데이터 출처: Yahoo Finance, CoinGecko</span>
  <span>·</span>
  <span>📅 업데이트: {today.strftime('%Y년 %m월 %d일 %H:%M')}</span>
</div>
"""

    # ── 작성자 바 ──────────────────────────────────────
    author_bar = f"""
<div class="author-bar" style="display:flex;align-items:center;gap:1rem;padding:1rem 1.5rem;background:#f0f7ff;border-radius:10px;margin:2rem 0;border:1px solid #bfdbfe;">
  <div style="background:#0A1628;color:#D4AF37;width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;">📔</div>
  <div>
    <div style="font-weight:700;color:#0A1628;">머니노트365 AI 애널리스트</div>
    <div style="font-size:0.82rem;color:#64748b;">실시간 글로벌 시장 데이터 기반 자동 분석 | Yahoo Finance · CoinGecko 데이터</div>
  </div>
</div>
"""

    # ── 면책조항 ───────────────────────────────────────
    disclaimer = """
<section id="disclaimer" style="background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:1.25rem 1.5rem;margin:2.5rem 0;">
<h2 style="color:#c2410c;font-size:1rem;margin:0 0 0.5rem;">⚠️ 투자 유의사항 (면책 조항)</h2>
<p style="margin:0;font-size:0.88rem;color:#7c2d12;">본 보고서는 <strong>교육 및 정보 제공 목적</strong>으로만 작성되었으며, 특정 종목의 매수·매도를 권유하는 투자 권유가 아닙니다. 모든 투자 결정은 본인의 판단과 책임하에 이루어져야 하며, 투자 손실에 대한 책임은 투자자 본인에게 있습니다. 과거 수익률이 미래 수익률을 보장하지 않습니다.</p>
</section>
"""

    # ── 내부 링크 섹션 ────────────────────────────────
    internal_links = f"""
<div style="background:#f8fafc;border:1px solid #e0e7ef;border-radius:10px;padding:1.5rem;margin:2rem 0;">
<h2 style="margin:0 0 1rem;font-size:1rem;color:#0A1628;">🔗 관련 카테고리</h2>
<div style="display:flex;flex-wrap:wrap;gap:0.5rem;">
<a href="{SITE_URL}/category/daily-report/" style="background:#0A1628;color:white;padding:0.35rem 0.85rem;border-radius:20px;font-size:0.82rem;text-decoration:none;">📋 일일 보고서</a>
<a href="{SITE_URL}/category/kr-stock/" style="background:#1a3a6c;color:white;padding:0.35rem 0.85rem;border-radius:20px;font-size:0.82rem;text-decoration:none;">🇰🇷 국내 주식</a>
<a href="{SITE_URL}/category/us-stock/" style="background:#1a3a6c;color:white;padding:0.35rem 0.85rem;border-radius:20px;font-size:0.82rem;text-decoration:none;">🇺🇸 미국 주식</a>
<a href="{SITE_URL}/category/crypto/" style="background:#1a3a6c;color:white;padding:0.35rem 0.85rem;border-radius:20px;font-size:0.82rem;text-decoration:none;">🪙 암호화폐</a>
<a href="{SITE_URL}/category/bonds-rates/" style="background:#1a3a6c;color:white;padding:0.35rem 0.85rem;border-radius:20px;font-size:0.82rem;text-decoration:none;">🏦 채권 &amp; 금리</a>
<a href="{SITE_URL}/category/investment-strategy/" style="background:#1a3a6c;color:white;padding:0.35rem 0.85rem;border-radius:20px;font-size:0.82rem;text-decoration:none;">💡 투자 전략</a>
<a href="{SITE_URL}/category/invest-study/" style="background:#1a3a6c;color:white;padding:0.35rem 0.85rem;border-radius:20px;font-size:0.82rem;text-decoration:none;">📚 투자 공부방</a>
</div>
</div>
"""

    # ── 토론 CTA ──────────────────────────────────────
    discussion = f"""
<div style="background:#0A1628;color:white;border-radius:12px;padding:2rem;margin:2rem 0;text-align:center;">
<h2 style="color:#FFD700;margin:0 0 0.75rem;">💬 오늘의 토론 주제</h2>
<p style="color:#94a3b8;margin:0 0 1.5rem;">여러분은 오늘 시장을 어떻게 보시나요?</p>
<div style="display:grid;gap:0.75rem;text-align:left;max-width:600px;margin:0 auto;">
<div style="background:rgba(255,255,255,0.08);border-radius:8px;padding:0.75rem 1rem;font-size:0.9rem;">
Q1. KOSPI {ksp_pct:+.2f}% 상황에서 추가 매수 vs 관망?</div>
<div style="background:rgba(255,255,255,0.08);border-radius:8px;padding:0.75rem 1rem;font-size:0.9rem;">
Q2. 공포탐욕지수 {fg.get('value','N/A')}에서 코인 시장 전망은?</div>
<div style="background:rgba(255,255,255,0.08);border-radius:8px;padding:0.75rem 1rem;font-size:0.9rem;">
Q3. 현재 환율({usdkrw.get('close',0):,.1f}원) 수준에서 달러 비중 조절 전략은?</div>
</div>
<p style="color:#64748b;font-size:0.82rem;margin:1.25rem 0 0;">댓글로 의견을 나눠주세요!</p>
</div>
"""

    # ── 전체 조합 ──────────────────────────────────────
    full_html = f"""<article class="mn365-report" lang="ko" itemscope itemtype="https://schema.org/NewsArticle">

<meta itemprop="datePublished" content="{date_str}">
<meta itemprop="dateModified" content="{date_str}">
<meta itemprop="author" content="머니노트365 AI 애널리스트">
<meta itemprop="publisher" content="머니노트365">
<meta itemprop="inLanguage" content="ko-KR">

{lead_html}
{reading_info}
{toc}

{ai_body}

{author_bar}
{media_html.get('youtube_links', '')}
{internal_links}
{discussion}
{disclaimer}

<div style="text-align:center;padding:1.5rem;color:#94a3b8;font-size:0.8rem;border-top:1px solid #e0e7ef;margin-top:2rem;">
<p>데이터 출처: Yahoo Finance, CoinGecko, Alternative.me | {today.strftime('%Y년 %m월 %d일')} 발행</p>
<p><a href="{SITE_URL}/privacy-policy-2/" style="color:#64748b;">개인정보처리방침</a> · <a href="{SITE_URL}/disclaimer/" style="color:#64748b;">면책조항</a> · <a href="{SITE_URL}/about/" style="color:#64748b;">소개</a></p>
</div>

</article>"""

    print(f"  [OK] 보고서 생성 완료 ({len(full_html):,}자)")
    return full_html


def generate_title(us: dict, kr: dict, coin: dict) -> str:
    today    = datetime.now()
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    wd       = weekdays[today.weekday()]
    date_str = today.strftime("%Y.%m.%d")

    sp500 = us.get("indices", {}).get("S&P500", {})
    kospi = kr.get("kospi", {})
    btc   = coin.get("coins", {}).get("bitcoin", {})

    sp_pct  = sp500.get("change_pct", 0) or 0
    ksp_pct = kospi.get("change_pct", 0) or 0
    btc_pct = btc.get("change_24h", 0) or 0

    sp_abs  = abs(sp_pct)
    ksp_abs = abs(ksp_pct)
    btc_abs = abs(btc_pct)

    if   ksp_pct <= -3: mood = "급락 주의"
    elif ksp_pct <= -1: mood = "하락 지속"
    elif ksp_pct >= 2:  mood = "강세 반등"
    elif ksp_pct >= 0:  mood = "소폭 상승"
    else:               mood = "혼조 마감"

    return (f"[{date_str}({wd})] 머니노트365 일일 투자 보고서 | "
            f"S&P500 {sp_pct:+.2f}% · KOSPI {ksp_pct:+.2f}% · "
            f"BTC {btc_pct:+.2f}% — {mood}")


def generate_excerpt(us: dict, kr: dict, coin: dict) -> str:
    sp500 = us.get("indices", {}).get("S&P500", {})
    kospi = kr.get("kospi", {})
    kosdaq = kr.get("kosdaq", {})
    btc   = coin.get("coins", {}).get("bitcoin", {})
    fg    = coin.get("fear_greed", {})
    gold  = us.get("commodities", {}).get("금(Gold)", {})
    usdkrw = us.get("forex", {}).get("USD/KRW", {})

    today = datetime.now()
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    wd = weekdays[today.weekday()]

    sp_pct  = sp500.get("change_pct", 0) or 0
    ksp_pct = kospi.get("change_pct", 0) or 0
    btc_pct = btc.get("change_24h", 0) or 0

    return (
        f"{today.strftime('%Y년 %m월 %d일')}({wd}) 글로벌 시장 종합 분석. "
        f"KOSPI {kospi.get('close',0):,.2f}pt({ksp_pct:+.2f}%), "
        f"S&P500 {sp500.get('close',0):,.2f}pt({sp_pct:+.2f}%), "
        f"BTC ${btc.get('price_usd',0):,.0f}({btc_pct:+.2f}%), "
        f"금 ${gold.get('close',0):,.1f}, 원달러 {usdkrw.get('close',0):,.1f}원. "
        f"공포탐욕지수 {fg.get('value','N/A')}({fg.get('classification_kr','N/A')}). "
        f"역사적 사례와 함께하는 상세 투자 해설."
    )


def get_seo_meta(us: dict, kr: dict, coin: dict, title: str) -> dict:
    """Yoast SEO 메타데이터 생성"""
    excerpt = generate_excerpt(us, kr, coin)
    sp_pct  = us.get("indices", {}).get("S&P500", {}).get("change_pct", 0) or 0
    ksp_pct = kr.get("kospi", {}).get("change_pct", 0) or 0
    btc_pct = coin.get("coins", {}).get("bitcoin", {}).get("change_24h", 0) or 0

    today = datetime.now()
    focus_kw = (
        f"오늘 코스피 {today.strftime('%m월%d일')}, "
        f"S&P500 전망, 비트코인 시세, 글로벌 투자 보고서"
    )

    # 메타 제목 (60자 이내)
    meta_title = f"오늘 KOSPI {ksp_pct:+.2f}% · BTC {btc_pct:+.2f}% | {today.strftime('%m/%d')} 투자 보고서 — 머니노트365"
    if len(meta_title) > 60:
        meta_title = meta_title[:57] + "..."

    return {
        "yoast_meta": {
            "_yoast_wpseo_title":          meta_title,
            "_yoast_wpseo_metadesc":       excerpt[:155],
            "_yoast_wpseo_focuskw":        focus_kw,
            "_yoast_wpseo_canonical":      "",
            "_yoast_wpseo_schema_article_type": "NewsArticle",
            "_yoast_wpseo_is_cornerstone_content": "0",
        },
        "og_meta": {
            "_og_title":       title[:70],
            "_og_description": excerpt[:200],
            "_og_type":        "article",
        }
    }
