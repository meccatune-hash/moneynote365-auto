# -*- coding: utf-8 -*-
"""
Post 30 직접 업데이트 + 단계별 진단
NinjaFirewall이 정확히 어떤 내용을 차단하는지 확인
"""
import requests, base64, os, json
from dotenv import load_dotenv
load_dotenv()

api  = os.getenv("WP_API_URL")
url  = os.getenv("WP_URL")
user = os.getenv("WP_USERNAME")
pw   = os.getenv("WP_PASSWORD")
tok  = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

def try_update(post_id, content, label):
    r = requests.post(f"{api}/posts/{post_id}", json={
        "content": content,
        "status": "publish",
    }, headers=hdrs, timeout=30)
    ok = r.status_code == 200
    print(f"  [{label}]: HTTP {r.status_code} {'[OK]' if ok else '[FAIL]'}")
    if not ok:
        print(f"    {r.text[:100]}")
    return ok

print("="*55)
print("  NinjaFirewall 진단 - 포스트 30번")
print("="*55)

POST_ID = 30

# 테스트 1: 순수 텍스트
print("\n[Test 1] 순수 텍스트")
try_update(POST_ID, "<p>안녕하세요 테스트입니다.</p>", "순수텍스트")

# 테스트 2: 테이블 포함
print("\n[Test 2] 테이블 포함")
try_update(POST_ID, """
<p>시장 데이터</p>
<table>
<thead><tr><th>지수</th><th>값</th><th>등락</th></tr></thead>
<tbody>
<tr><td>KOSPI</td><td>6,516</td><td>-6.62%</td></tr>
<tr><td>S&amp;P500</td><td>5,500</td><td>-0.69%</td></tr>
</tbody>
</table>
""", "테이블")

# 테스트 3: 이미지 포함
print("\n[Test 3] 이미지 포함")
try_update(POST_ID, """
<p>오늘의 시황</p>
<figure>
<img src="https://source.unsplash.com/800x400/?stock,market" alt="주식시장" style="width:100%">
</figure>
<p>분석 내용입니다.</p>
""", "이미지")

# 테스트 4: 저장된 실제 보고서 크기 확인
print("\n[Test 4] 실제 보고서 데이터 로드 및 크기별 테스트")
try:
    # 마지막 생성된 시장 데이터 로드
    import glob
    files = sorted(glob.glob("logs/data/*.json"))
    if files:
        with open(files[-1], "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"  저장된 데이터 파일: {files[-1]}")
        print(f"  미국 지수: {list(data.get('us',{}).get('indices',{}).keys())}")
        print(f"  KOSPI: {data.get('kr',{}).get('kospi',{}).get('close', 'N/A')}")
except Exception as e:
    print(f"  데이터 로드 실패: {e}")

# 테스트 5: 2000자 짧은 내용
print("\n[Test 5] 2000자 분량")
medium_content = """
<article class="mn365-report">
<div class="report-header" style="background:linear-gradient(135deg,#0A1628,#1a3a5c);color:white;padding:2rem;border-radius:12px;margin-bottom:2rem;">
<h1 style="color:#FFD700;">2026년 08월 19일 머니노트365 일일 투자 보고서</h1>
<p>오늘 글로벌 증시는 전반적으로 약세를 보였습니다. KOSPI는 6,516포인트로 마감했으며, 미국 S&amp;P500은 소폭 하락했습니다.</p>
</div>

<h2>오늘의 핵심 수치</h2>
<table style="width:100%;border-collapse:collapse;">
<thead><tr style="background:#0A1628;color:white;">
<th>지수</th><th>현재가</th><th>등락률</th><th>해석</th>
</tr></thead>
<tbody>
<tr><td>KOSPI</td><td>6,516</td><td style="color:red;">-6.62%</td><td>급락세, 외국인 매도 집중</td></tr>
<tr><td>KOSDAQ</td><td>831</td><td style="color:red;">-3.79%</td><td>기술주 전반 하락</td></tr>
<tr><td>S&amp;P500</td><td>5,500</td><td style="color:red;">-0.69%</td><td>소폭 하락 마감</td></tr>
<tr><td>비트코인</td><td>$64,000</td><td style="color:green;">+0.00%</td><td>보합세 유지</td></tr>
</tbody>
</table>

<h2>글로벌 시장 분석</h2>
<p>오늘 한국 증시는 큰 폭으로 하락했습니다. KOSPI가 -6.62%라는 급락세를 보인 것은 단순한 일시적 조정이 아닌, 
구조적인 리스크가 반영된 것으로 해석됩니다. 외국인 투자자들의 대규모 매도세가 이어지고 있으며, 
원/달러 환율 상승이 추가적인 외국인 자금 이탈을 촉발하고 있습니다.</p>

<p>역사적으로 KOSPI가 하루에 5% 이상 급락한 사례를 보면, 2020년 3월 코로나 팬데믹 초기에 
비슷한 낙폭이 나타났습니다. 당시 KOSPI는 1,400선까지 하락했다가 이후 12개월 만에 3,300선까지 
회복하는 V자 반등을 보였습니다. 물론 과거가 미래를 보장하지는 않지만, 역사적 맥락에서 
현재 상황을 이해하는 것은 중요합니다.</p>

<div class="report-footer" style="background:#f5f5f5;padding:1rem;border-radius:8px;margin-top:2rem;">
<p style="font-size:0.85rem;color:#666;">본 보고서는 교육 목적이며 투자 권유가 아닙니다.</p>
</div>
</article>
"""
result = try_update(POST_ID, medium_content, "2000자 보고서")

if result:
    print("\n[SUCCESS] 2000자 버전 발행 성공!")
    print("  -> 긴 내용(15000자)이 문제. 내용을 분할하거나 크기 줄이기 필요")
else:
    print("\n[FAIL] 2000자도 차단됨 -> 내용과 무관, 다른 설정 문제")
