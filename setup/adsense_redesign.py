# -*- coding: utf-8 -*-
"""
구글 애드센스 승인 최적화 사이트 리디자인
- 사이트명/설명 변경
- 내비게이션 메뉴 생성
- 프리미엄 CSS 적용
- 필수 페이지 완성
- 카테고리 정리
"""
import requests, base64, os, json
from dotenv import load_dotenv
load_dotenv()

WP_URL = os.getenv("WP_URL")
api    = os.getenv("WP_API_URL")
user   = os.getenv("WP_USERNAME")
pw     = os.getenv("WP_PASSWORD")
tok    = base64.b64encode(f"{user}:{pw}".encode()).decode()
hdrs   = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}


def ok(label, r):
    s = "✅" if r.status_code in (200, 201, 204) else "❌"
    print(f"  {s} {label}: HTTP {r.status_code}")
    return r.status_code in (200, 201, 204)


# ═══════════════════════════════════════════════════
# STEP 1: 사이트 기본 정보 업데이트
# ═══════════════════════════════════════════════════
print("\n[STEP 1] 사이트 기본 정보 업데이트")

r = requests.post(f"{api}/settings", json={
    "title":       "머니노트365",
    "description": "매일 업데이트되는 글로벌 투자 보고서 | 주식·코인·채권·선물옵션 분석",
    "timezone_string": "Asia/Seoul",
    "date_format": "Y년 m월 d일",
    "posts_per_page": 10,
}, headers=hdrs, timeout=10)
ok("사이트 기본 정보", r)


# ═══════════════════════════════════════════════════
# STEP 2: 개인정보처리방침 완성 (애드센스 필수)
# ═══════════════════════════════════════════════════
print("\n[STEP 2] 개인정보처리방침 업데이트")

privacy_content = """
<div class="policy-page">

<p>머니노트365(이하 "사이트")는 이용자의 개인정보를 중요하게 생각하며, 「개인정보 보호법」 및 관계 법령을 준수하고 있습니다. 본 개인정보처리방침은 사이트가 어떤 정보를 수집하고 어떻게 사용하는지 설명합니다.</p>

<h2>1. 수집하는 개인정보 항목</h2>
<p>본 사이트는 댓글 작성, 문의 등의 서비스 제공을 위해 아래와 같은 정보를 수집할 수 있습니다:</p>
<ul>
<li>이름 (닉네임)</li>
<li>이메일 주소</li>
<li>접속 IP 주소, 브라우저 종류, 방문 일시 (자동 수집)</li>
</ul>

<h2>2. 개인정보의 수집 및 이용 목적</h2>
<ul>
<li>댓글 및 문의 답변 처리</li>
<li>서비스 개선 및 통계 분석</li>
<li>스팸 및 악성 접근 방지</li>
</ul>

<h2>3. 쿠키(Cookie) 사용</h2>
<p>본 사이트는 이용자 경험 개선을 위해 쿠키를 사용합니다. 쿠키는 웹브라우저에 저장되는 작은 텍스트 파일이며, 브라우저 설정에서 쿠키 저장을 거부할 수 있습니다.</p>

<h2>4. 구글 애드센스 및 광고</h2>
<p>본 사이트는 Google AdSense를 통해 광고를 게재합니다. Google은 맞춤형 광고 제공을 위해 쿠키를 사용할 수 있습니다. 이에 대한 자세한 내용은 <a href="https://policies.google.com/privacy" target="_blank" rel="nofollow">Google 개인정보처리방침</a>을 참고하시기 바랍니다.</p>
<p>이용자는 <a href="https://www.google.com/settings/ads" target="_blank" rel="nofollow">Google 광고 설정</a>에서 맞춤형 광고를 비활성화할 수 있습니다.</p>

<h2>5. 제3자 링크</h2>
<p>본 사이트에는 외부 사이트 링크가 포함될 수 있으며, 외부 사이트의 개인정보 처리에 대해서는 책임을 지지 않습니다.</p>

<h2>6. 개인정보 보유 및 파기</h2>
<p>수집된 개인정보는 목적 달성 후 지체 없이 파기합니다. 댓글의 경우 이용자 요청 시 삭제됩니다.</p>

<h2>7. 이용자의 권리</h2>
<p>이용자는 언제든지 자신의 개인정보 조회, 수정, 삭제를 요청할 수 있습니다.</p>

<h2>8. 문의처</h2>
<p>개인정보 관련 문의사항은 <a href="/contact/">문의하기</a> 페이지를 이용해 주시기 바랍니다.</p>

<p><strong>시행일: 2026년 8월 18일</strong></p>

</div>
"""

# 기존 개인정보처리방침 페이지 업데이트
r_pages = requests.get(f"{api}/pages?slug=privacy-policy-2", headers=hdrs, timeout=10)
if r_pages.status_code == 200 and r_pages.json():
    pid = r_pages.json()[0]["id"]
    r = requests.post(f"{api}/pages/{pid}", json={
        "content": privacy_content,
        "status": "publish",
        "title": "개인정보처리방침"
    }, headers=hdrs, timeout=15)
    ok("개인정보처리방침 업데이트", r)


# ═══════════════════════════════════════════════════
# STEP 3: About 페이지 개선
# ═══════════════════════════════════════════════════
print("\n[STEP 3] About 페이지 개선")

about_content = """
<div class="about-page">

<div style="background:linear-gradient(135deg,#0A1628,#1e3a5c);color:white;padding:3rem 2rem;border-radius:16px;text-align:center;margin-bottom:3rem;">
<h1 style="color:#FFD700;font-size:2.5rem;margin:0 0 1rem;">📔 머니노트365</h1>
<p style="font-size:1.2rem;color:#94a3b8;margin:0;">매일 글로벌 투자 정보를 분석하고 공유하는 금융 교육 블로그</p>
</div>

<h2>🎯 사이트 목적</h2>
<p>머니노트365는 주식, 암호화폐, 채권, 선물·옵션 등 다양한 금융 시장을 함께 공부하고 분석하는 공간입니다. 복잡한 금융 정보를 누구나 이해하기 쉽게 해설하고, 역사적 사례와 함께 오늘의 시장을 해석합니다.</p>

<h2>📊 매일 제공하는 정보</h2>
<ul>
<li><strong>일일 글로벌 투자 보고서</strong> — 미국·한국·글로벌 증시, 암호화폐, 채권 종합 분석</li>
<li><strong>실시간 시황 해설</strong> — 주요 지수의 등락 원인과 배경 설명</li>
<li><strong>역사적 사례 분석</strong> — 과거 유사 상황과 현재 비교</li>
<li><strong>투자 전략 인사이트</strong> — 단기·중기·장기 투자 관점 제시</li>
<li><strong>경제 지표 해석</strong> — CPI, 금리, 고용 등 핵심 지표 분석</li>
</ul>

<h2>⚠️ 투자 면책 조항</h2>
<p>본 사이트의 모든 내용은 <strong>교육 목적</strong>으로 제공되며, 특정 종목의 매수·매도를 권유하는 것이 아닙니다. 모든 투자 결정은 독자 본인의 판단과 책임하에 이루어져야 합니다.</p>

<h2>📬 문의하기</h2>
<p>사이트 관련 문의, 제보, 협업 제안은 <a href="/contact/">문의하기 페이지</a>를 이용해 주세요.</p>

</div>
"""

r_about = requests.get(f"{api}/pages?slug=about", headers=hdrs, timeout=10)
if r_about.status_code == 200 and r_about.json():
    pid = r_about.json()[0]["id"]
    r = requests.post(f"{api}/pages/{pid}", json={
        "content": about_content,
        "status": "publish",
        "title": "About — 머니노트365 소개"
    }, headers=hdrs, timeout=15)
    ok("About 페이지", r)


# ═══════════════════════════════════════════════════
# STEP 4: 문의하기 페이지 개선
# ═══════════════════════════════════════════════════
print("\n[STEP 4] 문의하기 페이지 개선")

contact_content = """
<div class="contact-page">

<h2>📬 문의하기</h2>
<p>머니노트365에 대한 의견, 질문, 제보, 협업 제안 등 모든 문의를 환영합니다.</p>

<div style="background:#f8fafc;border:1px solid #e0e7ef;border-radius:12px;padding:2rem;margin:2rem 0;">
<h3 style="margin-top:0;">연락 방법</h3>
<ul style="list-style:none;padding:0;">
<li style="padding:0.5rem 0;">📧 <strong>이메일</strong>: moneynote365@gmail.com</li>
<li style="padding:0.5rem 0;">💬 <strong>댓글</strong>: 각 게시글 하단 댓글란을 이용해 주세요</li>
</ul>
</div>

<h3>자주 묻는 질문</h3>

<details style="border:1px solid #e0e7ef;border-radius:8px;padding:1rem;margin:0.5rem 0;">
<summary style="font-weight:bold;cursor:pointer;">보고서는 언제 발행되나요?</summary>
<p style="margin:1rem 0 0;">매일 오후 1시에 전날 미국 시장 마감 데이터와 당일 한국 시장 데이터를 반영한 보고서가 자동 발행됩니다.</p>
</details>

<details style="border:1px solid #e0e7ef;border-radius:8px;padding:1rem;margin:0.5rem 0;">
<summary style="font-weight:bold;cursor:pointer;">투자 추천을 해주시나요?</summary>
<p style="margin:1rem 0 0;">아니요. 본 사이트는 교육 목적의 정보 제공만 하며, 특정 종목 매수·매도를 권유하지 않습니다.</p>
</details>

<details style="border:1px solid #e0e7ef;border-radius:8px;padding:1rem;margin:0.5rem 0;">
<summary style="font-weight:bold;cursor:pointer;">광고/협찬 문의는 어떻게 하나요?</summary>
<p style="margin:1rem 0 0;">위 이메일로 문의해 주시면 검토 후 답변 드립니다.</p>
</details>

</div>
"""

r_contact = requests.get(f"{api}/pages?slug=contact", headers=hdrs, timeout=10)
if r_contact.status_code == 200 and r_contact.json():
    pid = r_contact.json()[0]["id"]
    r = requests.post(f"{api}/pages/{pid}", json={
        "content": contact_content, "status": "publish"
    }, headers=hdrs, timeout=15)
    ok("문의하기 페이지", r)


# ═══════════════════════════════════════════════════
# STEP 5: 프리미엄 CSS 디자인 적용
# ═══════════════════════════════════════════════════
print("\n[STEP 5] 프리미엄 CSS 디자인 적용")

premium_css = """
/* ═══════════════════════════════════════
   머니노트365 - 애드센스 최적화 프리미엄 CSS
   ═══════════════════════════════════════ */

:root {
  --navy:   #0A1628;
  --blue:   #1a3a6c;
  --gold:   #D4AF37;
  --light:  #F8FAFC;
  --border: #E0E7EF;
  --text:   #1a202c;
  --muted:  #64748b;
  --red:    #dc2626;
  --green:  #16a34a;
}

/* 기본 타이포그래피 */
body {
  font-family: 'Pretendard', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif !important;
  color: var(--text) !important;
  background: #f4f6f9 !important;
  line-height: 1.8 !important;
}

/* 헤더 */
.wp-site-blocks > header,
header.wp-block-template-part,
.site-header {
  background: var(--navy) !important;
  border-bottom: 3px solid var(--gold) !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3) !important;
  padding: 0 !important;
}

/* 사이트 제목 */
.wp-block-site-title a,
.site-title a,
h1.site-title {
  color: #ffffff !important;
  font-weight: 800 !important;
  font-size: 1.5rem !important;
  text-decoration: none !important;
  letter-spacing: -0.5px !important;
}
.wp-block-site-title a:hover { color: var(--gold) !important; }

/* 사이트 설명 */
.wp-block-site-tagline,
.site-description {
  color: #94a3b8 !important;
  font-size: 0.85rem !important;
}

/* 내비게이션 메뉴 */
.wp-block-navigation,
nav.main-navigation {
  background: var(--navy) !important;
}
.wp-block-navigation a,
.main-navigation a {
  color: #cbd5e1 !important;
  font-size: 0.9rem !important;
  font-weight: 500 !important;
  padding: 0.5rem 0.75rem !important;
  border-radius: 6px !important;
  transition: all 0.2s !important;
}
.wp-block-navigation a:hover,
.main-navigation a:hover {
  color: var(--gold) !important;
  background: rgba(212,175,55,0.1) !important;
}

/* 메인 컨텐츠 영역 */
.wp-site-blocks main,
main#main,
.site-content {
  background: transparent !important;
  max-width: 1200px !important;
  margin: 0 auto !important;
  padding: 1.5rem 1rem !important;
}

/* 포스트 카드 */
article.post,
article.type-post,
.wp-block-post {
  background: #ffffff !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 6px rgba(0,0,0,0.08) !important;
  margin-bottom: 1.5rem !important;
  overflow: hidden !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
  border: 1px solid var(--border) !important;
}
article.post:hover,
.wp-block-post:hover {
  transform: translateY(-3px) !important;
  box-shadow: 0 6px 20px rgba(0,0,0,0.12) !important;
}

/* 포스트 제목 */
.entry-title a,
h2.wp-block-post-title a,
h3.wp-block-post-title a {
  color: var(--navy) !important;
  font-weight: 700 !important;
  font-size: 1.15rem !important;
  text-decoration: none !important;
  line-height: 1.4 !important;
}
.entry-title a:hover,
h2.wp-block-post-title a:hover {
  color: var(--blue) !important;
}

/* 포스트 메타 (날짜, 카테고리) */
.entry-meta,
.wp-block-post-date,
.posted-on {
  color: var(--muted) !important;
  font-size: 0.82rem !important;
}

/* 본문 콘텐츠 */
.entry-content,
.wp-block-post-content {
  font-size: 1rem !important;
  line-height: 1.9 !important;
  color: #374151 !important;
  padding: 1.5rem 2rem !important;
}

/* 본문 h2, h3 */
.entry-content h2 {
  font-size: 1.4rem !important;
  font-weight: 700 !important;
  color: var(--navy) !important;
  border-left: 4px solid var(--gold) !important;
  padding-left: 0.75rem !important;
  margin: 2.5rem 0 1rem !important;
}
.entry-content h3 {
  font-size: 1.15rem !important;
  font-weight: 600 !important;
  color: var(--blue) !important;
  margin: 2rem 0 0.75rem !important;
}

/* 테이블 */
.entry-content table {
  width: 100% !important;
  border-collapse: collapse !important;
  margin: 1.5rem 0 !important;
  font-size: 0.92rem !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
  border-radius: 8px !important;
  overflow: hidden !important;
}
.entry-content th {
  background: var(--navy) !important;
  color: white !important;
  padding: 0.75rem 1rem !important;
  text-align: left !important;
  font-weight: 600 !important;
}
.entry-content td {
  padding: 0.65rem 1rem !important;
  border-bottom: 1px solid var(--border) !important;
}
.entry-content tr:nth-child(even) td { background: #f8fafc !important; }
.entry-content tr:hover td { background: #eff6ff !important; }

/* 인용 블록 */
.entry-content blockquote {
  border-left: 4px solid var(--gold) !important;
  background: #fafbfc !important;
  padding: 1rem 1.5rem !important;
  margin: 1.5rem 0 !important;
  border-radius: 0 8px 8px 0 !important;
  font-style: italic !important;
  color: #4b5563 !important;
}

/* 이미지 */
.entry-content img {
  border-radius: 10px !important;
  max-width: 100% !important;
  height: auto !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}

/* 차트 컨테이너 */
.chart-container {
  background: #f8fafc !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 1.25rem !important;
  margin: 1.25rem 0 !important;
}
.chart-container a {
  color: #1d4ed8 !important;
  font-weight: 500 !important;
}

/* 리스트 */
.entry-content ul li {
  padding: 0.25rem 0 !important;
  position: relative !important;
}
.entry-content ul {
  padding-left: 1.5rem !important;
}

/* 카테고리 배지 */
.cat-links a,
.wp-block-post-terms a {
  display: inline-block !important;
  background: var(--navy) !important;
  color: white !important;
  font-size: 0.75rem !important;
  padding: 0.2rem 0.6rem !important;
  border-radius: 20px !important;
  margin: 0.1rem !important;
  text-decoration: none !important;
  font-weight: 600 !important;
}
.cat-links a:hover { background: var(--blue) !important; }

/* 읽기 더보기 버튼 */
.more-link,
.wp-block-read-more a,
a.more-link {
  display: inline-block !important;
  background: var(--navy) !important;
  color: white !important;
  padding: 0.5rem 1.25rem !important;
  border-radius: 6px !important;
  font-size: 0.875rem !important;
  font-weight: 600 !important;
  text-decoration: none !important;
  margin-top: 0.75rem !important;
  transition: background 0.2s !important;
}
.more-link:hover,
a.more-link:hover { background: var(--blue) !important; }

/* 사이드바 위젯 */
aside.widget-area,
.sidebar {
  background: transparent !important;
}
.widget {
  background: white !important;
  border-radius: 12px !important;
  padding: 1.25rem !important;
  margin-bottom: 1.25rem !important;
  border: 1px solid var(--border) !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}
.widget-title,
.widgettitle {
  font-size: 1rem !important;
  font-weight: 700 !important;
  color: var(--navy) !important;
  border-bottom: 2px solid var(--gold) !important;
  padding-bottom: 0.5rem !important;
  margin-bottom: 1rem !important;
}

/* 페이지네이션 */
.pagination,
.nav-links {
  display: flex !important;
  justify-content: center !important;
  gap: 0.5rem !important;
  margin: 2rem 0 !important;
}
.page-numbers {
  padding: 0.5rem 0.875rem !important;
  border-radius: 6px !important;
  border: 1px solid var(--border) !important;
  color: var(--navy) !important;
  font-weight: 500 !important;
  text-decoration: none !important;
}
.page-numbers.current,
.page-numbers:hover {
  background: var(--navy) !important;
  color: white !important;
  border-color: var(--navy) !important;
}

/* 푸터 */
.wp-site-blocks > footer,
footer.site-footer,
.site-footer {
  background: var(--navy) !important;
  color: #94a3b8 !important;
  text-align: center !important;
  padding: 2rem 1rem !important;
  margin-top: 3rem !important;
  border-top: 3px solid var(--gold) !important;
}
.site-footer a { color: var(--gold) !important; text-decoration: none !important; }
.site-footer a:hover { color: white !important; }

/* 보고서 헤더 특별 스타일 */
.mn365-report .report-header,
article .report-header {
  border-radius: 12px !important;
  overflow: hidden !important;
}

/* 애드센스 광고 영역 (자동 최적화) */
.adsbygoogle {
  display: block !important;
  margin: 1.5rem auto !important;
}

/* 반응형 */
@media (max-width: 768px) {
  .entry-content { padding: 1rem !important; }
  .entry-content h2 { font-size: 1.2rem !important; }
  .entry-content table { font-size: 0.82rem !important; }
  .entry-content th, .entry-content td { padding: 0.5rem !important; }
}

/* 포스트 목록 그리드 */
.wp-block-query .wp-block-post-template,
.posts-container {
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)) !important;
  gap: 1.25rem !important;
}

/* 페이지 타이틀 */
.page-header,
.archive-header {
  background: white !important;
  border-radius: 12px !important;
  padding: 1.5rem 2rem !important;
  margin-bottom: 1.5rem !important;
  border-left: 5px solid var(--gold) !important;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
}
.page-title, .archive-title {
  color: var(--navy) !important;
  font-size: 1.5rem !important;
  font-weight: 700 !important;
  margin: 0 !important;
}

/* 단일 포스트 */
.single .entry-content {
  max-width: 820px !important;
  margin: 0 auto !important;
}
"""

r = requests.post(f"{api}/settings", json={
    "custom_css": premium_css,
}, headers=hdrs, timeout=15)
ok("프리미엄 CSS 적용", r)

# ═══════════════════════════════════════════════════
# STEP 6: 카테고리 이름 정리 (이모지 제거 옵션)
# ═══════════════════════════════════════════════════
print("\n[STEP 6] 카테고리 설명 추가")

cat_descriptions = {
    "daily-report":         "매일 업데이트되는 글로벌 주식·코인·채권 종합 투자 보고서",
    "kr-stock":             "KOSPI, KOSDAQ 국내 주식 시장 분석 및 주요 종목 동향",
    "us-stock":             "S&P500, 나스닥, 다우존스 등 미국 증시 분석",
    "global-stock":         "유럽, 아시아, 신흥국 등 글로벌 증시 동향 분석",
    "crypto":               "비트코인(BTC), 이더리움(ETH) 등 암호화폐 시장 분석",
    "bonds-rates":          "미국·한국 국채 금리, FOMC 금리 결정 분석",
    "investment-strategy":  "단기·중기·장기 투자 전략 및 포트폴리오 구성 방법",
    "economic-indicators":  "CPI 소비자물가, 고용지표, GDP 등 주요 경제지표 해설",
    "short-selling":        "국내·해외 공매도 현황 및 주요 종목 공매도 비율 분석",
    "futures-options":      "선물, 옵션, 파생상품 시장 동향 및 기초 개념 설명",
    "invest-study":         "투자 기초 개념, 용어 설명, 초보자를 위한 금융 교육",
}

r_cats = requests.get(f"{api}/categories?per_page=30", headers=hdrs, timeout=10)
for cat in r_cats.json():
    slug = cat["slug"]
    if slug in cat_descriptions:
        r = requests.post(f"{api}/categories/{cat['id']}", json={
            "description": cat_descriptions[slug]
        }, headers=hdrs, timeout=10)
        if r.status_code == 200:
            print(f"  ✅ {cat['name']} 설명 추가")


print("\n" + "="*55)
print("  ✅ 애드센스 최적화 리디자인 완료!")
print("="*55)
print(f"\n사이트 확인: {WP_URL}")
