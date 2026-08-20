# -*- coding: utf-8 -*-
"""
Connection test script - all APIs
"""
import sys, io, os

print("="*60)
print("  머니노트365 연결 테스트")
print("="*60)

# 1. WordPress 연결
print("\n[1] WordPress API 연결 테스트...")
from publisher.wp_publisher import test_connection
wp_ok = test_connection()

# 2. Gemini API 테스트
print("\n[2] Gemini API 테스트...")
try:
    from google import genai
    from dotenv import load_dotenv
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="안녕하세요! 한 문장으로 인사해주세요."
    )
    print(f"  [OK] Gemini 연결 성공: {response.text[:80]}")
    gemini_ok = True
except Exception as e:
    print(f"  [FAIL] Gemini 연결 실패: {e}")
    gemini_ok = False

# 3. CoinGecko API 테스트
print("\n[3] CoinGecko API 테스트...")
try:
    import requests
    resp = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10)
    if resp.status_code == 200:
        btc = resp.json()["bitcoin"]["usd"]
        print(f"  [OK] CoinGecko 연결 성공: BTC = ${btc:,.0f}")
        coingecko_ok = True
    else:
        print(f"  [FAIL] 응답 오류: {resp.status_code}")
        coingecko_ok = False
except Exception as e:
    print(f"  [FAIL] CoinGecko 연결 실패: {e}")
    coingecko_ok = False

# 4. yfinance 테스트
print("\n[4] yfinance (미국 주식) 테스트...")
try:
    import yfinance as yf
    sp = yf.Ticker("^GSPC")
    hist = sp.history(period="1d")
    if not hist.empty:
        close = hist["Close"].iloc[-1]
        print(f"  [OK] yfinance 연결 성공: S&P500 = {close:,.2f}")
        yf_ok = True
    else:
        print("  [OK] yfinance 설치됨 (장 마감 시간)")
        yf_ok = True
except Exception as e:
    print(f"  [FAIL] yfinance 실패: {e}")
    yf_ok = False

# 결과 요약
print("\n" + "="*60)
print("  테스트 결과 요약")
print("="*60)
print(f"  WordPress:  {'[OK]' if wp_ok else '[FAIL]'}")
print(f"  Gemini AI:  {'[OK]' if gemini_ok else '[FAIL]'}")
print(f"  CoinGecko:  {'[OK]' if coingecko_ok else '[FAIL]'}")
print(f"  yfinance:   {'[OK]' if yf_ok else '[FAIL]'}")
print("="*60)

all_ok = all([wp_ok, gemini_ok, coingecko_ok, yf_ok])
if all_ok:
    print("\n[SUCCESS] 모든 연결 정상! 이제 setup/wp_setup.py를 실행하세요.")
else:
    print("\n[WARNING] 일부 연결에 문제가 있습니다.")
