# -*- coding: utf-8 -*-
"""
머니노트365 보고서 생성기 v5 - 텍스트 전용 + 극도 상세
- 이미지/CSS/스타일 완전 제거
- 순수 텍스트 기반 HTML (h2, h3, p, ul, table, blockquote만 사용)
- 6,000자+ 실제 본문 내용
- 오류 없는 안정적 구조
"""
import os, re
from datetime import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SITE_URL  = os.getenv("WP_URL", "https://kingbrightsucces.com")
SITE_NAME = "머니노트365"

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def pct_str(v):
    if v is None: return "N/A"
    try:
        v = float(v)
        return f"{'▲' if v >= 0 else '▼'}{'+' if v >= 0 else ''}{v:.2f}%"
    except:
        return "N/A"


def format_market_data_for_prompt(us, kr, coin):
    lines = ["=== 오늘의 실제 시장 데이터 ===\n"]

    lines.append("【미국 주요 지수】")
    for name, d in us.get("indices", {}).items():
        if d and "error" not in d:
            lines.append(f"  {name}: {d['close']:,.2f}  {pct_str(d.get('change_pct'))}")

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
        lines.append(f"  KOSPI:  {kospi.get('close',0):,.2f}  {pct_str(kospi.get('change_pct'))}")
    if kosdaq and "error" not in kosdaq:
        lines.append(f"  KOSDAQ: {kosdaq.get('close',0):,.2f}  {pct_str(kosdaq.get('change_pct'))}")
    for s in kr.get("top_stocks", []):
        lines.append(f"  {s['name']}: {s.get('close',0):,.0f}원  {pct_str(s.get('change_pct'))}")

    lines.append("\n【암호화폐】")
    for cname, d in coin.get("coins", {}).items():
        if d and "error" not in d:
            lines.append(f"  {cname}: ${d.get('price_usd',0):,.2f}  {pct_str(d.get('change_24h'))}")
    fg = coin.get("fear_greed", {})
    if fg:
        lines.append(f"  공포탐욕지수: {fg.get('value','N/A')} — {fg.get('classification_kr','N/A')}")

    return "\n".join(lines)


# ── 핵심 프롬프트: 텍스트 전용 + 극도 상세 ──────────────
TEXT_ONLY_PROMPT = """
당신은 국내 최고 수준의 금융 애널리스트이자 투자 교육 전문가입니다.
아래 실제 시장 데이터를 바탕으로 매우 상세하고 교육적인 투자 보고서를 작성하세요.

{market_data}

=== 절대 준수 규칙 ===
1. 순수 HTML만 사용: <h2>, <h3>, <p>, <ul>, <li>, <ol>, <table>, <thead>, <tbody>, <tr>, <th>, <td>, <blockquote>, <strong>, <em>, <hr>
2. inline style, class, id 속성 절대 금지
3. <div>, <span>, <img>, <script>, <iframe>, <figure> 절대 사용 금지
4. 마크다운 문법(**, ##, --) 사용 금지
5. 본문 글자 수: 최소 5,000자 이상 (HTML 태그 제외한 순수 텍스트)
6. 언어: 한국어 (금융 용어는 영어 병기)
7. 모든 수치는 실제 데이터를 정확히 사용

=== 보고서 구조 (순서대로 작성) ===

<h2>📌 오늘의 시장 핵심 요약</h2>
- 5~7개 불릿으로 오늘 가장 중요한 내용 요약
- 각 항목마다 실제 수치 포함

<h2>🌐 글로벌 시장 전체 흐름 분석</h2>
- 최소 600자 이상의 상세 분석
- 미국·유럽·아시아 증시 연결성 설명
- 왜 이런 결과가 나왔는지 원인 분석
- 달러 인덱스, 금리, 인플레이션과의 관계

<h2>🇺🇸 미국 증시 심층 분석</h2>
- S&P500, 나스닥, 다우존스 각각 상세 분석
- 섹터별 강약 (어느 섹터가 오르고 내렸는지 이유 포함)
- 연준(Fed) 통화정책과의 연관성
- VIX 공포지수 해석
- 실적 발표 기업 동향 (해당하는 경우)
- 최소 700자

<h2>🇰🇷 한국 증시 심층 분석</h2>
- KOSPI, KOSDAQ 실제 수치 기반 상세 분석
- 외국인/기관/개인 수급 흐름 추정
- 주요 종목 동향 분석
- 환율이 국내 증시에 미치는 영향
- 역사적 유사 사례 1~2개 구체적으로 언급
- 최소 700자

<h2>🪙 암호화폐 & 디지털 자산 분석</h2>
- 비트코인, 이더리움 실제 가격 포함
- 공포탐욕지수 수치와 의미 해석
- 온체인 데이터 해석 (해시레이트, 거래량 등)
- 기관 투자자 동향
- 최소 500자

<h2>🏦 채권 & 금리 & 환율 분석</h2>
- 미국 10년물 국채 금리 분석
- 달러/원 환율 분석과 한국 경제 영향
- 금(Gold) 가격 흐름과 안전자산 선호도
- 원자재(오일, 구리) 가격 해석
- 최소 500자

<h2>📊 투자 전략 인사이트</h2>
- 현재 시장 상황에서의 투자 관점
- 단기(1~2주), 중기(1~3개월), 장기(6개월+) 각각 전망
- 주목할 섹터와 이유
- 리스크 요인 3가지 이상 구체적 설명
- 투자 대가(버핏, 피터린치, 레이달리오 등)의 관련 명언 1개 인용
- 최소 600자

<h2>📚 오늘의 투자 용어 해설</h2>
- 오늘 보고서에 등장한 용어 3~4개 쉽게 설명
- 초보자도 이해할 수 있는 수준으로 작성

<h2>❓ 자주 묻는 질문 (FAQ)</h2>
- 오늘 시장과 관련된 질문 5개
- 각 답변은 3~5문장으로 구체적으로

<h2>⚠️ 투자 유의사항</h2>
- 면책조항 (교육 목적, 투자 권유 아님)

출력: 순수 HTML 코드만 출력 (```없이)
"""


def _call_gemini(prompt: str) -> str:
    # 사용 가능한 모델 순서대로 시도
    models = [
        "gemini-3.6-flash",   # 현재 권장 모델
        "gemini-2.5-pro",     # 고성능 대안
        "gemini-2.5-flash",   # 경량 대안
    ]
    for model in models:
        try:
            resp = _client.models.generate_content(model=model, contents=prompt)
            text = resp.text.strip()
            # 마크다운 펜스 제거
            text = re.sub(r'^```html?\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*```\s*$', '', text)
            if len(text) > 500:   # 정상 응답인지 확인
                print(f"  [모델: {model}] 생성 성공")
                return text.strip()
        except Exception as e:
            print(f"  [{model}] 오류: {str(e)[:80]}")
            continue
    return "<p>보고서 생성 오류 - API 키를 확인해주세요.</p>"


def generate_daily_report(us: dict, kr: dict, coin: dict,
                          media_html: dict = None) -> str:
    today   = datetime.now()
    wd      = WEEKDAYS[today.weekday()]
    date_kr = today.strftime(f"%Y년 %m월 %d일({wd})")

    market_data = format_market_data_for_prompt(us, kr, coin)

    print("[AI] 상세 투자 보고서 생성 중...")
    body = _call_gemini(TEXT_ONLY_PROMPT.format(market_data=market_data))

    # 수치 추출
    kospi  = kr.get("kospi",  {})
    kosdaq = kr.get("kosdaq", {})
    sp500  = us.get("indices",{}).get("S&P500",{})
    ndx    = us.get("indices",{}).get("나스닥",{})
    btc    = coin.get("coins",{}).get("bitcoin",{})
    eth    = coin.get("coins",{}).get("ethereum",{})
    fg     = coin.get("fear_greed",{})
    gold   = us.get("commodities",{}).get("금(Gold)",{})
    oil    = us.get("commodities",{}).get("WTI 원유",{})
    usdkrw = us.get("forex",{}).get("USD/KRW",{})
    vix    = us.get("indices",{}).get("VIX",{})

    # 핵심 수치 테이블
    table_html = f"""
<table>
<thead>
<tr><th>지수/자산</th><th>현재가</th><th>등락</th><th>비고</th></tr>
</thead>
<tbody>
<tr><td>KOSPI</td><td>{kospi.get('close',0):,.2f}pt</td><td>{pct_str(kospi.get('change_pct'))}</td><td>한국 대표 지수</td></tr>
<tr><td>KOSDAQ</td><td>{kosdaq.get('close',0):,.2f}pt</td><td>{pct_str(kosdaq.get('change_pct'))}</td><td>한국 기술주 지수</td></tr>
<tr><td>S&amp;P500</td><td>{sp500.get('close',0):,.2f}pt</td><td>{pct_str(sp500.get('change_pct'))}</td><td>미국 대표 500개 기업</td></tr>
<tr><td>나스닥</td><td>{ndx.get('close',0):,.2f}pt</td><td>{pct_str(ndx.get('change_pct'))}</td><td>미국 기술주 중심</td></tr>
<tr><td>비트코인(BTC)</td><td>${btc.get('price_usd',0):,.0f}</td><td>{pct_str(btc.get('change_24h'))}</td><td>24시간 변동</td></tr>
<tr><td>이더리움(ETH)</td><td>${eth.get('price_usd',0):,.0f}</td><td>{pct_str(eth.get('change_24h'))}</td><td>24시간 변동</td></tr>
<tr><td>금(Gold)</td><td>${gold.get('close',0):,.2f}/oz</td><td>{pct_str(gold.get('change_pct'))}</td><td>안전자산</td></tr>
<tr><td>WTI 원유</td><td>${oil.get('close',0):,.2f}/배럴</td><td>{pct_str(oil.get('change_pct'))}</td><td>국제 유가</td></tr>
<tr><td>달러/원 환율</td><td>{usdkrw.get('close',0):,.2f}원</td><td>{pct_str(usdkrw.get('change_pct'))}</td><td>원화 강약 기준</td></tr>
<tr><td>공포탐욕지수</td><td>{fg.get('value','N/A')}</td><td>—</td><td>{fg.get('classification_kr','N/A')}</td></tr>
</tbody>
</table>
"""

    # 데이터 출처 및 면책
    footer_html = f"""
<hr>
<p><strong>데이터 출처:</strong> Yahoo Finance, CoinGecko, Alternative.me | <strong>발행일:</strong> {today.strftime('%Y년 %m월 %d일 %H:%M')} KST</p>
<p><strong>관련 카테고리:</strong>
<a href="{SITE_URL}/category/daily-report/">일일 투자 보고서</a> |
<a href="{SITE_URL}/category/kr-stock/">국내 주식</a> |
<a href="{SITE_URL}/category/us-stock/">미국 주식</a> |
<a href="{SITE_URL}/category/crypto/">암호화폐</a> |
<a href="{SITE_URL}/category/bonds-rates/">채권 &amp; 금리</a> |
<a href="{SITE_URL}/category/investment-strategy/">투자 전략</a>
</p>
<hr>
<p><strong>※ 면책 조항:</strong> 본 보고서는 교육 목적의 정보 제공이며, 특정 종목의 매수·매도를 권유하지 않습니다. 모든 투자 결정과 손익은 투자자 본인의 책임입니다. 과거 수익률이 미래를 보장하지 않습니다. 투자 전 반드시 본인의 투자 성향과 재무 상태를 고려하시기 바랍니다.</p>
"""

    full_html = f"""<h2>📊 {date_kr} 핵심 시장 데이터 요약</h2>
{table_html}
{body}
{footer_html}"""

    print(f"  [OK] 보고서 생성 완료 ({len(full_html):,}자)")
    return full_html


def generate_title(us: dict, kr: dict, coin: dict) -> str:
    today  = datetime.now()
    wd     = WEEKDAYS[today.weekday()]
    ds     = today.strftime("%Y.%m.%d")
    sp500  = us.get("indices",{}).get("S&P500",{})
    kospi  = kr.get("kospi",{})
    btc    = coin.get("coins",{}).get("bitcoin",{})
    sp_pct = sp500.get("change_pct", 0) or 0
    kp_pct = kospi.get("change_pct", 0) or 0
    bt_pct = btc.get("change_24h", 0) or 0

    if   kp_pct <= -3: mood = "급락 경보"
    elif kp_pct <= -1: mood = "하락 지속"
    elif kp_pct >= 2:  mood = "강세 반등"
    elif kp_pct >= 0:  mood = "소폭 상승"
    else:              mood = "혼조 마감"

    return (f"[{ds}({wd})] 머니노트365 일일 투자 보고서 | "
            f"S&P500 {sp_pct:+.2f}% · KOSPI {kp_pct:+.2f}% · "
            f"BTC {bt_pct:+.2f}% — {mood}")


def generate_excerpt(us: dict, kr: dict, coin: dict) -> str:
    today  = datetime.now()
    wd     = WEEKDAYS[today.weekday()]
    sp500  = us.get("indices",{}).get("S&P500",{})
    kospi  = kr.get("kospi",{})
    btc    = coin.get("coins",{}).get("bitcoin",{})
    gold   = us.get("commodities",{}).get("금(Gold)",{})
    usdkrw = us.get("forex",{}).get("USD/KRW",{})
    fg     = coin.get("fear_greed",{})
    sp_pct = sp500.get("change_pct",0) or 0
    kp_pct = kospi.get("change_pct",0) or 0
    bt_pct = btc.get("change_24h",0) or 0

    return (
        f"{today.strftime('%Y년 %m월 %d일')}({wd}) 글로벌 투자 시장 종합 분석 보고서. "
        f"KOSPI {kospi.get('close',0):,.2f}pt({kp_pct:+.2f}%), "
        f"S&P500 {sp500.get('close',0):,.2f}pt({sp_pct:+.2f}%), "
        f"비트코인 ${btc.get('price_usd',0):,.0f}({bt_pct:+.2f}%), "
        f"금 ${gold.get('close',0):,.1f}/oz, 달러/원 {usdkrw.get('close',0):,.1f}원. "
        f"공포탐욕지수 {fg.get('value','N/A')}({fg.get('classification_kr','')})."
    )


def get_seo_meta(us: dict, kr: dict, coin: dict, title: str) -> dict:
    excerpt = generate_excerpt(us, kr, coin)
    today   = datetime.now()
    kp_pct  = kr.get("kospi",{}).get("change_pct",0) or 0
    bt_pct  = coin.get("coins",{}).get("bitcoin",{}).get("change_24h",0) or 0

    meta_title = f"오늘 KOSPI {kp_pct:+.2f}% BTC {bt_pct:+.2f}% | {today.strftime('%m/%d')} 투자 분석 — 머니노트365"
    return {
        "yoast_meta": {
            "_yoast_wpseo_title":    meta_title[:60],
            "_yoast_wpseo_metadesc": excerpt[:155],
            "_yoast_wpseo_focuskw":  f"코스피 {today.strftime('%m월%d일')}, 비트코인 시세, 오늘 주식 시장",
            "_yoast_wpseo_schema_article_type": "NewsArticle",
        }
    }
