# -*- coding: utf-8 -*-
"""
금융 데이터 수집 - 미국 주식 (yfinance)
"""
import yfinance as yf
from datetime import datetime, timedelta


US_INDICES = {
    "S&P500": "^GSPC",
    "나스닥": "^IXIC",
    "다우존스": "^DJI",
    "러셀2000": "^RUT",
    "VIX(공포지수)": "^VIX",
}

SECTOR_ETFS = {
    "기술(XLK)": "XLK",
    "헬스케어(XLV)": "XLV",
    "금융(XLF)": "XLF",
    "에너지(XLE)": "XLE",
    "소비재(XLY)": "XLY",
    "유틸리티(XLU)": "XLU",
    "산업재(XLI)": "XLI",
}

COMMODITIES = {
    "금(Gold)": "GC=F",
    "은(Silver)": "SI=F",
    "WTI유가": "CL=F",
    "천연가스": "NG=F",
    "구리": "HG=F",
}

FUTURES = {
    "S&P500 선물": "ES=F",
    "나스닥 선물": "NQ=F",
    "다우 선물": "YM=F",
}

FOREX = {
    "달러인덱스": "DX-Y.NYB",
    "USD/KRW": "KRW=X",
    "USD/JPY": "JPY=X",
    "EUR/USD": "EURUSD=X",
}


def get_ticker_data(symbol, period="2d"):
    """단일 티커 데이터 수집"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return None
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]
        change = latest["Close"] - prev["Close"]
        pct = (change / prev["Close"]) * 100 if prev["Close"] != 0 else 0
        return {
            "symbol": symbol,
            "close": round(latest["Close"], 2),
            "open": round(latest["Open"], 2),
            "high": round(latest["High"], 2),
            "low": round(latest["Low"], 2),
            "volume": int(latest.get("Volume", 0)),
            "change": round(change, 2),
            "change_pct": round(pct, 2),
            "date": hist.index[-1].strftime("%Y-%m-%d"),
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def collect_us_market():
    """미국 시장 전체 데이터 수집"""
    print("📈 미국 시장 데이터 수집 중...")
    result = {
        "indices": {},
        "sectors": {},
        "commodities": {},
        "futures": {},
        "forex": {},
        "timestamp": datetime.now().isoformat(),
    }

    for name, sym in US_INDICES.items():
        result["indices"][name] = get_ticker_data(sym)

    for name, sym in SECTOR_ETFS.items():
        result["sectors"][name] = get_ticker_data(sym)

    for name, sym in COMMODITIES.items():
        result["commodities"][name] = get_ticker_data(sym)

    for name, sym in FUTURES.items():
        result["futures"][name] = get_ticker_data(sym)

    for name, sym in FOREX.items():
        result["forex"][name] = get_ticker_data(sym)

    print("  ✅ 미국 시장 데이터 수집 완료")
    return result


def format_change(val, pct):
    """등락 포맷"""
    arrow = "▲" if val >= 0 else "▼"
    sign = "+" if val >= 0 else ""
    return f"{arrow} {sign}{val:,.2f} ({sign}{pct:.2f}%)"


if __name__ == "__main__":
    data = collect_us_market()
    print("\n--- 미국 주요 지수 ---")
    for name, d in data["indices"].items():
        if d and "error" not in d:
            print(f"  {name}: {d['close']:,.2f}  {format_change(d['change'], d['change_pct'])}")
