# -*- coding: utf-8 -*-
"""
Korean Market Data - yfinance only (pykrx Python 3.14 incompatible)
"""
import yfinance as yf
from datetime import datetime


KR_INDICES = {
    "kospi":  {"symbol": "^KS11", "name": "KOSPI"},
    "kosdaq": {"symbol": "^KQ11", "name": "KOSDAQ"},
}

KR_TOP_STOCKS_YF = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "현대차": "005380.KS",
    "POSCO홀딩스": "005490.KS",
    "셀트리온": "068270.KS",
    "KB금융": "105560.KS",
    "신한지주": "055550.KS",
    "카카오": "035720.KS",
}


def get_index_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        if hist.empty:
            return {"error": "no data"}
        latest = hist.iloc[-1]
        prev   = hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]
        change = latest["Close"] - prev["Close"]
        pct    = (change / prev["Close"]) * 100 if prev["Close"] != 0 else 0
        return {
            "close":      round(float(latest["Close"]), 2),
            "open":       round(float(latest["Open"]), 2),
            "high":       round(float(latest["High"]), 2),
            "low":        round(float(latest["Low"]), 2),
            "volume":     int(latest.get("Volume", 0)),
            "change":     round(float(change), 2),
            "change_pct": round(float(pct), 2),
            "date":       hist.index[-1].strftime("%Y-%m-%d"),
            "source":     "yfinance",
        }
    except Exception as e:
        return {"error": str(e)}


def collect_kr_market():
    """Korean market data via yfinance"""
    print("[KR] 한국 시장 데이터 수집 중...")
    result = {
        "kospi":         {},
        "kosdaq":        {},
        "top_stocks":    [],
        "short_selling": [],
        "timestamp":     datetime.now().isoformat(),
    }

    for key, info in KR_INDICES.items():
        d = get_index_data(info["symbol"])
        result[key] = d
        if "error" not in d:
            print(f"  [OK] {info['name']}: {d['close']:,.2f}  ({d['change_pct']:+.2f}%)")
        else:
            print(f"  [WARN] {info['name']} 수집 실패: {d['error']}")

    # 주요 종목
    print("  [INFO] 주요 종목 수집 중...")
    for name, sym in list(KR_TOP_STOCKS_YF.items())[:5]:
        try:
            t = yf.Ticker(sym)
            h = t.history(period="2d")
            if not h.empty:
                c = h.iloc[-1]["Close"]
                p = h.iloc[-2]["Close"] if len(h) > 1 else c
                pct = (c - p) / p * 100
                result["top_stocks"].append({
                    "name": name, "symbol": sym,
                    "close": round(float(c), 0),
                    "change_pct": round(float(pct), 2),
                })
        except:
            pass

    print(f"  [OK] 한국 시장 수집 완료 (종목 {len(result['top_stocks'])}개)")
    return result


if __name__ == "__main__":
    data = collect_kr_market()
    print(f"\nKOSPI : {data['kospi'].get('close', 'N/A')} ({data['kospi'].get('change_pct', 0):+.2f}%)")
    print(f"KOSDAQ: {data['kosdaq'].get('close', 'N/A')} ({data['kosdaq'].get('change_pct', 0):+.2f}%)")
    for s in data["top_stocks"]:
        print(f"  {s['name']}: {s['close']:,.0f}원 ({s['change_pct']:+.2f}%)")
