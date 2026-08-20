# -*- coding: utf-8 -*-
"""
Image & Media Fetcher
- Unsplash: section header images
- TradingView: live chart embeds
- YouTube: Korean finance videos
- CoinGecko: crypto chart embeds
"""
import sys, io, os, requests, shutil

from dotenv import load_dotenv
load_dotenv()

UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

# ── Unsplash 검색 키워드 매핑 ─────────────────────────────
SECTION_KEYWORDS = {
    "main":        "stock market trading finance",
    "us_market":   "wall street new york stock exchange",
    "kr_market":   "seoul korea finance business",
    "crypto":      "bitcoin cryptocurrency blockchain",
    "bonds":       "federal reserve interest rate bond",
    "commodity":   "gold oil commodity trading",
    "strategy":    "investment portfolio financial planning",
}

# ── TradingView 차트 임베드 HTML ─────────────────────────
TRADINGVIEW_CHARTS = {
    "sp500": """
<div class="chart-container" style="background:#f8fafc;border:1px solid #e0e7ef;border-radius:8px;padding:1rem;margin:1rem 0;">
<h4 style="margin:0 0 0.5rem;color:#0A1628;">S&P500 실시간 차트</h4>
<a href="https://www.tradingview.com/chart/?symbol=SP%3ASPX" target="_blank" rel="nofollow" style="display:block;">
<img src="https://s3.tradingview.com/snapshots/s/SPX_D.png" alt="S&P500 차트" style="width:100%;border-radius:6px;" onerror="this.style.display='none'">
<p style="text-align:center;color:#0066cc;font-size:0.9rem;">📈 TradingView에서 S&P500 실시간 차트 보기 →</p>
</a>
</div>""",

    "nasdaq": """
<div class="chart-container" style="background:#f8fafc;border:1px solid #e0e7ef;border-radius:8px;padding:1rem;margin:1rem 0;">
<h4 style="margin:0 0 0.5rem;color:#0A1628;">나스닥 실시간 차트</h4>
<a href="https://www.tradingview.com/chart/?symbol=NASDAQ%3ANDX" target="_blank" rel="nofollow" style="display:block;">
<p style="text-align:center;color:#0066cc;font-size:0.9rem;">📈 TradingView에서 나스닥 실시간 차트 보기 →</p>
</a>
</div>""",

    "kospi": """
<div class="chart-container" style="background:#f8fafc;border:1px solid #e0e7ef;border-radius:8px;padding:1rem;margin:1rem 0;">
<h4 style="margin:0 0 0.5rem;color:#0A1628;">KOSPI 실시간 차트</h4>
<a href="https://www.tradingview.com/chart/?symbol=KRX%3AKOSPI" target="_blank" rel="nofollow" style="display:block;">
<p style="text-align:center;color:#0066cc;font-size:0.9rem;">📈 TradingView에서 KOSPI 실시간 차트 보기 →</p>
</a>
</div>""",

    "bitcoin": """
<div class="chart-container" style="background:#f8fafc;border:1px solid #e0e7ef;border-radius:8px;padding:1rem;margin:1rem 0;">
<h4 style="margin:0 0 0.5rem;color:#0A1628;">비트코인(BTC/USD) 실시간 차트</h4>
<a href="https://www.tradingview.com/chart/?symbol=BITSTAMP%3ABTCUSD" target="_blank" rel="nofollow" style="display:block;">
<p style="text-align:center;color:#0066cc;font-size:0.9rem;">📈 TradingView에서 BTC 실시간 차트 보기 →</p>
</a>
</div>""",

    "gold": """
<div class="chart-container" style="background:#f8fafc;border:1px solid #e0e7ef;border-radius:8px;padding:1rem;margin:1rem 0;">
<h4 style="margin:0 0 0.5rem;color:#0A1628;">금(Gold) 선물 차트</h4>
<a href="https://www.tradingview.com/chart/?symbol=COMEX%3AGC1%21" target="_blank" rel="nofollow" style="display:block;">
<p style="text-align:center;color:#0066cc;font-size:0.9rem;">📈 TradingView에서 금 실시간 차트 보기 →</p>
</a>
</div>""",

    "dxy": """
<div class="chart-container" style="background:#f8fafc;border:1px solid #e0e7ef;border-radius:8px;padding:1rem;margin:1rem 0;">
<h4 style="margin:0 0 0.5rem;color:#0A1628;">달러인덱스(DXY) 차트</h4>
<a href="https://www.tradingview.com/chart/?symbol=TVC%3ADXY" target="_blank" rel="nofollow" style="display:block;">
<p style="text-align:center;color:#0066cc;font-size:0.9rem;">📈 TradingView에서 달러인덱스 차트 보기 →</p>
</a>
</div>""",

    "fear_greed": """
<div class="chart-container" style="background:#f8fafc;border:1px solid #e0e7ef;border-radius:8px;padding:1rem;margin:1rem 0;text-align:center;">
<h4 style="margin:0 0 0.5rem;color:#0A1628;">암호화폐 공포&amp;탐욕 지수</h4>
<a href="https://alternative.me/crypto/fear-and-greed-index/" target="_blank" rel="nofollow">
<img src="https://alternative.me/crypto/fear-and-greed-index.png" alt="공포탐욕지수" style="max-width:400px;width:100%;border-radius:8px;">
</a>
</div>""",
}

# ── 한국 금융 유튜브 채널 추천 영상 ──────────────────────
YOUTUBE_FINANCE_KR = [
    {
        "title": "주식 시장 분석 - 한국경제TV",
        "channel": "한국경제TV",
        "search": "한국경제TV 증시",
        "embed_id": "PLsearch",  # placeholder
    },
]

YOUTUBE_EMBEDS = {
    "market_intro": """
<div class="youtube-container">
<h4>오늘의 시장 해설 영상 추천</h4>
<p>아래 채널에서 오늘의 시장 해설을 확인하세요:</p>
<ul>
<li><a href="https://www.youtube.com/@한국경제TV" target="_blank" rel="nofollow">📺 한국경제TV - 시황 분석</a></li>
<li><a href="https://www.youtube.com/@머니투데이TV" target="_blank" rel="nofollow">📺 머니투데이TV - 투자 전략</a></li>
<li><a href="https://www.youtube.com/@CNBCKorea" target="_blank" rel="nofollow">📺 CNBC Korea - 글로벌 시장</a></li>
</ul>
</div>""",
}

# ── CoinGecko 차트 ────────────────────────────────────────
COINGECKO_CHART = """
<div class="chart-container">
<h4>비트코인 가격 추이 (30일)</h4>
<a href="https://www.coingecko.com/en/coins/bitcoin" target="_blank">
<img src="https://www.coingecko.com/coins/1/sparkline.svg" alt="BTC 30일 차트" style="width:100%;max-width:600px;border-radius:8px;">
</a>
</div>"""


def get_unsplash_image(keyword, width=1200, height=630):
    """Unsplash에서 이미지 URL 가져오기 (API 키 없어도 random URL 사용 가능)"""
    if UNSPLASH_KEY:
        try:
            resp = requests.get(
                "https://api.unsplash.com/photos/random",
                params={"query": keyword, "orientation": "landscape", "w": width},
                headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "url": data["urls"]["regular"],
                    "thumb": data["urls"]["thumb"],
                    "alt": data.get("alt_description", keyword),
                    "credit": data["user"]["name"],
                    "credit_url": data["user"]["links"]["html"],
                }
        except Exception as e:
            pass

    # API 키 없을 때: Unsplash Source URL (무료, 키 불필요)
    safe_keyword = keyword.replace(" ", ",")
    return {
        "url": f"https://source.unsplash.com/{width}x{height}/?{safe_keyword}",
        "thumb": f"https://source.unsplash.com/400x200/?{safe_keyword}",
        "alt": keyword,
        "credit": "Unsplash",
        "credit_url": "https://unsplash.com",
    }


def download_image(url, save_path):
    """이미지 다운로드"""
    try:
        resp = requests.get(url, timeout=15, stream=True)
        if resp.status_code == 200:
            with open(save_path, 'wb') as f:
                shutil.copyfileobj(resp.raw, f)
            return True
    except Exception as e:
        print(f"  [WARN] 이미지 다운로드 실패: {e}")
    return False


def get_market_image_html(section="main"):
    """섹션별 이미지 HTML 태그 생성"""
    keyword = SECTION_KEYWORDS.get(section, "finance investment")
    img = get_unsplash_image(keyword)
    return f"""
<figure class="report-image">
<img src="{img['url']}" alt="{img['alt']}" style="width:100%;border-radius:8px;margin:1rem 0;" loading="lazy">
<figcaption style="text-align:center;font-size:0.8rem;color:#888;">
  Photo by <a href="{img['credit_url']}" target="_blank">{img['credit']}</a> on Unsplash
</figcaption>
</figure>"""


def get_tradingview_chart(chart_key):
    """TradingView 차트 HTML 반환"""
    return TRADINGVIEW_CHARTS.get(chart_key, "")


def get_all_media_html():
    """보고서에 삽입할 전체 미디어 HTML 패키지 반환"""
    return {
        "main_image":    get_market_image_html("main"),
        "us_image":      get_market_image_html("us_market"),
        "kr_image":      get_market_image_html("kr_market"),
        "crypto_image":  get_market_image_html("crypto"),
        "bonds_image":   get_market_image_html("bonds"),
        "strategy_image": get_market_image_html("strategy"),
        "chart_sp500":   get_tradingview_chart("sp500"),
        "chart_nasdaq":  get_tradingview_chart("nasdaq"),
        "chart_kospi":   get_tradingview_chart("kospi"),
        "chart_bitcoin": get_tradingview_chart("bitcoin"),
        "chart_gold":    get_tradingview_chart("gold"),
        "chart_dxy":     get_tradingview_chart("dxy"),
        "chart_fg":      get_tradingview_chart("fear_greed"),
        "btc_sparkline": COINGECKO_CHART,
        "youtube_links": YOUTUBE_EMBEDS["market_intro"],
    }


if __name__ == "__main__":
    print("[TEST] 미디어 수집 테스트...")
    media = get_all_media_html()
    print(f"  main_image URL: {media['main_image'][:80]}...")
    print(f"  chart_sp500 len: {len(media['chart_sp500'])} chars")
    print(f"  [OK] 미디어 패키지 준비 완료 ({len(media)}개 항목)")
