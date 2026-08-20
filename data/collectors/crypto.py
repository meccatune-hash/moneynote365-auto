# -*- coding: utf-8 -*-
"""
금융 데이터 수집 - 암호화폐 (CoinGecko 무료 API)
"""
import requests
from datetime import datetime


COINGECKO_BASE = "https://api.coingecko.com/api/v3"

TOP_COINS = [
    "bitcoin", "ethereum", "binancecoin", "ripple", "solana",
    "cardano", "dogecoin", "avalanche-2", "polkadot", "chainlink"
]

COIN_NAMES_KR = {
    "bitcoin": "비트코인(BTC)",
    "ethereum": "이더리움(ETH)",
    "binancecoin": "바이낸스코인(BNB)",
    "ripple": "리플(XRP)",
    "solana": "솔라나(SOL)",
    "cardano": "에이다(ADA)",
    "dogecoin": "도지코인(DOGE)",
    "avalanche-2": "아발란체(AVAX)",
    "polkadot": "폴카닷(DOT)",
    "chainlink": "체인링크(LINK)",
}


def collect_crypto():
    """암호화폐 시장 데이터 수집"""
    print("🪙 암호화폐 데이터 수집 중...")
    result = {
        "coins": {},
        "market_summary": {},
        "fear_greed": {},
        "timestamp": datetime.now().isoformat(),
    }

    try:
        # 코인 가격 데이터
        ids = ",".join(TOP_COINS)
        url = f"{COINGECKO_BASE}/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": ids,
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h,7d",
        }
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            for coin in resp.json():
                coin_id = coin["id"]
                result["coins"][coin_id] = {
                    "name": COIN_NAMES_KR.get(coin_id, coin["name"]),
                    "symbol": coin["symbol"].upper(),
                    "price_usd": coin["current_price"],
                    "market_cap": coin["market_cap"],
                    "change_24h": round(coin.get("price_change_percentage_24h") or 0, 2),
                    "change_7d": round(coin.get("price_change_percentage_7d_in_currency") or 0, 2),
                    "volume_24h": coin.get("total_volume", 0),
                    "high_24h": coin.get("high_24h", 0),
                    "low_24h": coin.get("low_24h", 0),
                }
        print("  ✅ 코인 가격 수집 완료")
    except Exception as e:
        print(f"  ⚠️ 코인 수집 오류: {e}")

    try:
        # 글로벌 시장 요약
        resp = requests.get(f"{COINGECKO_BASE}/global", timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            result["market_summary"] = {
                "total_market_cap_usd": data.get("total_market_cap", {}).get("usd", 0),
                "total_volume_usd": data.get("total_volume", {}).get("usd", 0),
                "btc_dominance": round(data.get("market_cap_percentage", {}).get("btc", 0), 2),
                "eth_dominance": round(data.get("market_cap_percentage", {}).get("eth", 0), 2),
                "active_coins": data.get("active_cryptocurrencies", 0),
                "market_cap_change_24h": round(data.get("market_cap_change_percentage_24h_usd", 0), 2),
            }
        print("  ✅ 글로벌 시장 요약 수집 완료")
    except Exception as e:
        print(f"  ⚠️ 글로벌 요약 오류: {e}")

    try:
        # 공포탐욕지수 (Alternative.me)
        resp = requests.get("https://api.alternative.me/fng/", timeout=10)
        if resp.status_code == 200:
            fng = resp.json()["data"][0]
            result["fear_greed"] = {
                "value": int(fng["value"]),
                "classification": fng["value_classification"],
                "timestamp": fng["timestamp"],
            }
            # 한국어 변환
            fng_kr = {
                "Extreme Fear": "극도의 공포",
                "Fear": "공포",
                "Neutral": "중립",
                "Greed": "탐욕",
                "Extreme Greed": "극도의 탐욕",
            }
            result["fear_greed"]["classification_kr"] = fng_kr.get(
                fng["value_classification"], fng["value_classification"]
            )
        print("  ✅ 공포탐욕지수 수집 완료")
    except Exception as e:
        print(f"  ⚠️ 공포탐욕지수 오류: {e}")

    print("  ✅ 암호화폐 전체 수집 완료")
    return result


if __name__ == "__main__":
    data = collect_crypto()
    btc = data["coins"].get("bitcoin", {})
    print(f"\nBTC: ${btc.get('price_usd', 'N/A'):,.0f}  ({btc.get('change_24h', 0):+.2f}%)")
    fg = data["fear_greed"]
    print(f"공포탐욕지수: {fg.get('value', 'N/A')} ({fg.get('classification_kr', 'N/A')})")
