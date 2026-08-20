# -*- coding: utf-8 -*-
"""
AI Daily Investment Report Generator - Enhanced Version
Long-form, explanatory style with images, charts, and videos
"""
import os, json
from datetime import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def format_market_data_for_prompt(us_data, kr_data, crypto_data):
    def pct_str(v):
        if v is None: return "N/A"
        v = float(v)
        return f"{'▲' if v >= 0 else '▼'} {'+' if v >= 0 else ''}{v:.2f}%"

    lines = ["=== 오늘의 실제 시장 데이터 (정확히 반영해서 해설할 것) ===\n"]

    lines.append("【미국 주요 지수】")
    for name, d in us_data.get("indices", {}).items():
        if d and "error" not in d:
            lines.append(f"  {name}: {d['close']:,.2f}  {pct_str(d.get('change_pct'))}  (고가:{d.get('high',0):,.2f} / 저가:{d.get('low',0):,.2f})")

    lines.append("\n【미국 선물 (다음 장 예고)】")
    for name, d in us_data.get("futures", {}).items():
        if d and "error" not in d:
            lines.append(f"  {name}: {d['close']:,.2f}  {pct_str(d.get('change_pct'))}")

    lines.append("\n【원자재】")
    for name, d in us_data.get("commodities", {}).items():
        if d and "error" not in d:
            lines.append(f"  {name}: {d['close']:,.2f}  {pct_str(d.get('change_pct'))}")

    lines.append("\n【환율】")
    for name, d in us_data.get("forex", {}).items():
        if d and "error" not in d:
            lines.append(f"  {name}: {d['close']:,.4f}  {pct_str(d.get('change_pct'))}")

    lines.append("\n【미국 섹터별 등락 (어떤 섹터가 강했나)】")
    for name, d in us_data.get("sectors", {}).items():
        if d and "error" not in d:
            lines.append(f"  {name}: {pct_str(d.get('change_pct'))}")

    lines.append("\n【한국 증시】")
    if kr_data.get("kospi") and "error" not in kr_data.get("kospi", {}):
        k = kr_data["kospi"]
        lines.append(f"  KOSPI: {k.get('close',0):,.2f}  {pct_str(k.get('change_pct'))}  (시가:{k.get('open',0):,.2f})")
    if kr_data.get("kosdaq") and "error" not in kr_data.get("kosdaq", {}):
        k = kr_data["kosdaq"]
        lines.append(f"  KOSDAQ: {k.get('close',0):,.2f}  {pct_str(k.get('change_pct'))}")

    if kr_data.get("short_selling"):
        lines.append("\n【공매도 현황】")
        for s in kr_data["short_selling"][:5]:
            lines.append(f"  공매도비중 {s.get('short_ratio',0):.2f}%")

    lines.append("\n【암호화폐 시장】")
    for coin_id, d in list(crypto_data.get("coins", {}).items())[:8]:
        lines.append(f"  {d['name']}: ${d['price_usd']:,.2f}  {pct_str(d.get('change_24h'))}  (7일:{pct_str(d.get('change_7d'))})")

    ms = crypto_data.get("market_summary", {})
    if ms:
        mcap = ms.get("total_market_cap_usd", 0)
        lines.append(f"\n  전체 시총: ${mcap/1e12:.2f}조  BTC 점유율: {ms.get('btc_dominance',0):.1f}%  시총변화(24h): {pct_str(ms.get('market_cap_change_24h'))}")

    fg = crypto_data.get("fear_greed", {})
    if fg:
        lines.append(f"\n  공포탐욕지수: {fg.get('value','N/A')}/100 → {fg.get('classification_kr','N/A')}")

    return "\n".join(lines)


def generate_daily_report(us_data, kr_data, crypto_data, media_html=None):
    """Generate long-form detailed investment report with media"""
    print("[AI] 상세 투자 보고서 생성 중...")
    if media_html is None:
        media_html = {}

    today    = datetime.now().strftime("%Y년 %m월 %d일")
    weekday  = ["월","화","수","목","금","토","일"][datetime.now().weekday()]
    market   = format_market_data_for_prompt(us_data, kr_data, crypto_data)

    # 미디어 placeholder들
    main_img   = media_html.get("main_image", "")
    us_img     = media_html.get("us_image", "")
    kr_img     = media_html.get("kr_image", "")
    crypto_img = media_html.get("crypto_image", "")
    bonds_img  = media_html.get("bonds_image", "")
    strat_img  = media_html.get("strategy_image", "")
    chart_sp   = media_html.get("chart_sp500", "")
    chart_nq   = media_html.get("chart_nasdaq", "")
    chart_ks   = media_html.get("chart_kospi", "")
    chart_btc  = media_html.get("chart_bitcoin", "")
    chart_gold = media_html.get("chart_gold", "")
    chart_dxy  = media_html.get("chart_dxy", "")
    chart_fg   = media_html.get("chart_fg", "")
    btc_spark  = media_html.get("btc_sparkline", "")
    yt_links   = media_html.get("youtube_links", "")

    prompt = f"""당신은 '머니노트365' 금융 블로그의 수석 애널리스트이자 금융 교육 전문가입니다.
오늘의 실제 시장 데이터를 바탕으로, 투자 초보자부터 중급자까지 모두 이해할 수 있는
**매우 상세하고 교육적인** 일일 투자 보고서를 작성합니다.

📅 오늘 날짜: {today} ({weekday}요일)

{market}

=== 작성 원칙 ===
1. **길이**: 최소 4,000자 이상 (한국어 기준). 각 섹션을 충분히 설명할 것.
2. **언어**: 초보자도 이해할 수 있도록 금융 용어마다 괄호 안에 쉬운 설명 추가.
   예) "VIX(시장 공포를 나타내는 지수, 높을수록 불안한 시장)" 
3. **해설형 글쓰기**: 숫자를 단순 나열하지 말고, "왜 이런 결과가 나왔는지", "이것이 투자자에게 어떤 의미인지" 반드시 설명.
4. **역사적 맥락**: 과거 유사한 상황 2~3개 언급하고 "당시에 어떤 일이 벌어졌는지" 설명.
5. **투자 포인트**: 매수/매도 직접 권유 금지. "이런 상황에서는 역사적으로 어떤 자산이 강했다" 식의 교육적 분석.
6. **HTML 형식**: 아래 구조를 반드시 지켜서 순수 HTML만 출력 (마크다운 코드블록 없이).

=== HTML 출력 구조 ===
아래 [PLACEHOLDER] 태그들을 그대로 유지하고, 각 섹션의 텍스트 분석만 채워주세요.

<article class="mn365-report">

<div class="report-header">
<p class="report-date">📅 {today} ({weekday}요일) | 머니노트365 일일 투자 보고서</p>
<p class="report-summary">
오늘의 핵심 요약을 3~4문장으로 작성. S&P500, KOSPI, BTC의 주요 움직임과 그 의미를 포함.
</p>
</div>

{main_img}

<div class="key-numbers">
<h3>📊 오늘의 핵심 수치</h3>
<table>
<thead><tr><th>지수/자산</th><th>현재가</th><th>등락률</th><th>한줄 해석</th></tr></thead>
<tbody>
실제 데이터로 행 6~8개 채우기. 한줄 해석 컬럼에 쉬운 설명 포함.
</tbody>
</table>
</div>

<h2>🌍 1. 글로벌 시장 전체 흐름 — 오늘 시장을 움직인 힘</h2>
{us_img}
<p>
[최소 600자] 오늘 글로벌 시장의 전반적인 흐름을 설명하세요.
- 미국 증시가 어떻게 마감했는지 (각 지수별 상세)
- 시장을 움직인 주요 원인 (경제지표 발표, 연준 발언, 지정학적 이슈 등)
- 달러인덱스와 금리가 증시에 미친 영향
- VIX(공포지수) 해석
초보자를 위해 용어마다 설명 추가.
</p>
{chart_sp}
{chart_nq}

<h2>🇰🇷 2. 국내 증시 분석 — KOSPI/KOSDAQ 오늘 어땠나?</h2>
{kr_img}
<p>
[최소 600자] 한국 증시를 상세히 분석하세요.
- KOSPI와 KOSDAQ 각각의 등락과 원인
- 미국 시장과의 연관성 ("미국이 오르면 한국도 오른다"는 통념과 현실)
- 원/달러 환율이 한국 증시에 미치는 영향 (외국인 수급 설명)
- 공매도가 있다면 어떤 종목에 집중됐는지
- 한국 시장만의 특이 요인
</p>
{chart_ks}

<h2>🇺🇸 3. 미국 증시 심층 분석 — 섹터별로 뜯어보자</h2>
<p>
[최소 700자] 미국 증시를 섹터 단위로 분석하세요.
- 오늘 가장 강했던 섹터와 약했던 섹터, 그 이유
- 기술주 vs 전통주 흐름 비교
- 원자재(금, 유가, 구리) 움직임과 증시의 관계
- 달러인덱스 변화가 수출 기업/원자재에 미치는 영향
- 과거 유사 섹터 흐름의 역사적 사례
</p>
{chart_gold}
{chart_dxy}

<h2>💰 4. 암호화폐 시장 — 비트코인은 지금 어디로?</h2>
{crypto_img}
<p>
[최소 500자] 암호화폐 시장을 분석하세요.
- 비트코인과 이더리움 가격 동향 및 원인
- 알트코인 시장 동향 (BTC 도미넌스 해석)
- 공포탐욕지수 해석 (지수가 의미하는 바, 역사적 패턴)
- 전통 금융시장(주식, 금)과 암호화폐의 상관관계
</p>
{chart_btc}
{btc_spark}
{chart_fg}

<h2>🏦 5. 채권 & 금리 — 가장 중요한 시장 신호</h2>
{bonds_img}
<p>
[최소 500자] 채권과 금리를 쉽게 설명하세요.
- 미국채 2년물/10년물 금리 현황
- 장단기 금리차(Yield Curve)가 뜻하는 것 (역전이면 경기침체 신호라는 설명)
- 금리 변화가 주식, 채권, 부동산에 미치는 영향을 비유로 설명
- FOMC 다음 회의 일정과 현재 시장의 금리 기대
</p>

<h2>📉 6. 선물 & 공매도 — 큰손들은 어디에 베팅했나?</h2>
<p>
[최소 400자] 선물과 공매도를 초보자 눈높이로 설명하세요.
- 선물이란 무엇인지 한 줄 설명 후 오늘 선물 시장 분석
- 공매도란 무엇인지 설명 (주가가 내릴 것을 예상해 미리 파는 것)
- 오늘 공매도 현황이 시장에 시사하는 바
- 옵션 만기일 관련 이슈가 있다면 설명
</p>

<h2>📚 7. 오늘의 투자 공부 — 역사에서 배우는 투자 지혜</h2>
{strat_img}
<p>
[최소 600자] 오늘 시장 데이터와 연결된 역사적 사례와 투자 인사이트를 제공하세요.
- 오늘과 유사했던 과거 시장 상황 2~3개 구체적으로 언급 (연도, 당시 지수, 결과)
- 그 상황에서 어떤 자산이 좋은 성과를 냈는지
- 워런 버핏, 피터 린치 등 대가들의 명언 1~2개와 오늘 시장에의 적용
- 분산투자, 리밸런싱 등 현재 상황에 맞는 전략 교육
</p>

<h2>📅 8. 이번 주 & 다음 주 주요 일정</h2>
<ul>
<li>주요 경제지표 발표 일정과 예상 영향</li>
<li>FOMC, 실적 발표, 옵션 만기 등 주요 이벤트</li>
<li>한국 관련 주요 일정</li>
</ul>

{yt_links}

<div class="discussion-box" style="background:#f0f7ff;border-left:4px solid #0066cc;padding:1.5rem;border-radius:8px;margin:2rem 0;">
<h3>💬 오늘의 토론 주제</h3>
<p>오늘 시장 데이터를 바탕으로 독자들과 토론할 질문 2~3개를 제시하세요.
예) "여러분은 현재 금리 상황에서 어떤 자산 비중을 높이고 있나요?"</p>
</div>

<div class="report-footer">
<p>⚠️ 본 보고서는 투자자 교육 목적의 시장 분석 정보이며, 특정 종목 매수·매도 권유가 아닙니다.
모든 투자 결정은 본인의 판단과 책임하에 이루어져야 하며, 투자 손실에 대해 머니노트365는 어떠한 법적 책임도 지지 않습니다.</p>
<p>📊 데이터 출처: Yahoo Finance, CoinGecko, KRX, FRED | 작성: 머니노트365 AI 애널리스트</p>
</div>

</article>

위 구조를 반드시 지키고, [PLACEHOLDER] 설명 텍스트 부분을 실제 분석 내용으로 채워주세요.
순수 HTML만 출력하세요 (마크다운 코드블록 없이).
최소 4000자 이상으로 상세하게 작성하세요.
"""

    try:
        response = _client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        content = response.text
        # Clean markdown fences
        for fence in ["```html", "```"]:
            if content.startswith(fence):
                content = content[len(fence):]
        if content.endswith("```"):
            content = content[:-3]
        print(f"  [OK] 보고서 생성 완료 ({len(content):,}자)")
        return content.strip()
    except Exception as e:
        print(f"  [ERROR] Gemini 오류: {e}")
        return generate_fallback_report(today, weekday, us_data, kr_data, crypto_data, media_html)


def generate_title(us_data, kr_data, crypto_data):
    today    = datetime.now().strftime("%Y.%m.%d")
    weekday  = ["월","화","수","목","금","토","일"][datetime.now().weekday()]
    sp500    = us_data.get("indices", {}).get("S&P500", {})
    kospi    = kr_data.get("kospi", {})
    btc      = crypto_data.get("coins", {}).get("bitcoin", {})
    sp_pct   = float(sp500.get("change_pct", 0) or 0)
    ko_pct   = float(kospi.get("change_pct", 0) or 0)
    btc_pct  = float(btc.get("change_24h", 0) or 0)

    tone = "강세" if sp_pct > 0.5 else ("약세" if sp_pct < -0.5 else "혼조")
    return (
        f"[{today}({weekday})] 머니노트365 일일 투자 보고서 | "
        f"S&P500 {sp_pct:+.2f}% · KOSPI {ko_pct:+.2f}% · BTC {btc_pct:+.2f}% — 글로벌 증시 {tone}"
    )


def generate_excerpt(us_data, kr_data, crypto_data):
    sp500   = us_data.get("indices", {}).get("S&P500", {})
    kospi   = kr_data.get("kospi", {})
    btc     = crypto_data.get("coins", {}).get("bitcoin", {})
    fg      = crypto_data.get("fear_greed", {})
    today   = datetime.now().strftime("%Y년 %m월 %d일")
    sp_pct  = float(sp500.get("change_pct", 0) or 0)
    ko_pct  = float(kospi.get("change_pct", 0) or 0)
    bp      = float(btc.get("price_usd", 0) or 0)
    b_pct   = float(btc.get("change_24h", 0) or 0)

    return (
        f"{today} 머니노트365 일일 투자 보고서. "
        f"S&P500 {sp_pct:+.2f}%, KOSPI {ko_pct:+.2f}%, BTC ${bp:,.0f}({b_pct:+.2f}%). "
        f"공포탐욕지수 {fg.get('value','N/A')}({fg.get('classification_kr','N/A')}). "
        f"글로벌 시황·섹터 분석·역사적 사례·투자 인사이트 상세 해설."
    )


def generate_fallback_report(today, weekday, us_data, kr_data, crypto_data, media_html=None):
    if media_html is None: media_html = {}
    sp = us_data.get("indices", {}).get("S&P500", {})
    ko = kr_data.get("kospi", {})
    bt = crypto_data.get("coins", {}).get("bitcoin", {})
    return f"""<article class="mn365-report">
<div class="report-header">
<p class="report-date">{today} ({weekday}요일) 일일 시장 브리핑</p>
</div>
{media_html.get('main_image','')}
<h2>오늘의 시장 현황</h2>
<table><thead><tr><th>지수</th><th>현재가</th><th>등락률</th></tr></thead>
<tbody>
<tr><td>S&amp;P500</td><td>{sp.get('close',0):,.2f}</td><td>{sp.get('change_pct',0):+.2f}%</td></tr>
<tr><td>KOSPI</td><td>{ko.get('close',0):,.2f}</td><td>{ko.get('change_pct',0):+.2f}%</td></tr>
<tr><td>비트코인</td><td>${bt.get('price_usd',0):,.0f}</td><td>{bt.get('change_24h',0):+.2f}%</td></tr>
</tbody></table>
{media_html.get('chart_sp500','')}
<div class="report-footer"><p>본 보고서는 교육 목적이며 투자 권유가 아닙니다.</p></div>
</article>"""
