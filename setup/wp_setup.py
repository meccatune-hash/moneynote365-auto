# -*- coding: utf-8 -*-
"""
WordPress 사이트 초기 세팅 - 머니노트365
카테고리, 태그, 필수 페이지, 커스텀 CSS 자동 구성
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from publisher.wp_publisher import (
    test_connection, get_or_create_category, get_or_create_tag, create_page
)

# ============================================================
# 카테고리 정의
# ============================================================
CATEGORIES = [
    {"name": "📋 일일 투자 보고서", "slug": "daily-report", "desc": "매일 아침 발행되는 글로벌 시장 분석 및 투자 보고서"},
    {"name": "🇰🇷 국내 주식", "slug": "kr-stock", "desc": "KOSPI, KOSDAQ 시황 분석 및 종목 분석"},
    {"name": "🇺🇸 미국 주식", "slug": "us-stock", "desc": "S&P500, 나스닥, 다우존스 등 미국 증시 분석"},
    {"name": "🌏 글로벌 주식", "slug": "global-stock", "desc": "유럽, 아시아, 신흥국 글로벌 시장 동향"},
    {"name": "🪙 암호화폐", "slug": "crypto", "desc": "비트코인, 이더리움, 알트코인 시장 분석"},
    {"name": "🏦 채권 & 금리", "slug": "bonds-rates", "desc": "미국채, 한국채권, 기준금리, 장단기 금리차 분석"},
    {"name": "📉 공매도 현황", "slug": "short-selling", "desc": "국내외 공매도 현황 및 분석"},
    {"name": "📊 선물 & 옵션", "slug": "futures-options", "desc": "주가지수 선물, 옵션, 파생상품 분석"},
    {"name": "📈 경제 지표", "slug": "economic-indicators", "desc": "GDP, CPI, 실업률, FOMC 등 주요 경제지표 분석"},
    {"name": "💡 투자 전략", "slug": "investment-strategy", "desc": "포트폴리오 구성, 투자 전략, 리스크 관리"},
    {"name": "📚 투자 공부방", "slug": "invest-study", "desc": "주식, 코인, 경제 기초 개념 학습 공간"},
]

# ============================================================
# 태그 정의
# ============================================================
TAGS = [
    # 국내 지수
    {"name": "KOSPI", "slug": "kospi"},
    {"name": "KOSDAQ", "slug": "kosdaq"},
    {"name": "코스피", "slug": "kospi-kr"},
    # 미국 지수
    {"name": "S&P500", "slug": "sp500"},
    {"name": "나스닥", "slug": "nasdaq"},
    {"name": "다우존스", "slug": "dow-jones"},
    {"name": "VIX", "slug": "vix"},
    {"name": "러셀2000", "slug": "russell2000"},
    # 암호화폐
    {"name": "비트코인", "slug": "bitcoin"},
    {"name": "이더리움", "slug": "ethereum"},
    {"name": "알트코인", "slug": "altcoin"},
    {"name": "공포탐욕지수", "slug": "fear-greed"},
    # 금리/채권
    {"name": "기준금리", "slug": "base-rate"},
    {"name": "FOMC", "slug": "fomc"},
    {"name": "미국채", "slug": "us-treasury"},
    {"name": "장단기금리차", "slug": "yield-curve"},
    # 원자재
    {"name": "금값", "slug": "gold"},
    {"name": "WTI유가", "slug": "wti-oil"},
    {"name": "달러인덱스", "slug": "dxy"},
    # 기술적 분석
    {"name": "RSI", "slug": "rsi"},
    {"name": "이평선", "slug": "moving-average"},
    {"name": "볼린저밴드", "slug": "bollinger-bands"},
    # 경제 지표
    {"name": "CPI", "slug": "cpi"},
    {"name": "GDP", "slug": "gdp"},
    {"name": "실업률", "slug": "unemployment"},
    {"name": "버핏지수", "slug": "buffett-indicator"},
    # 파생상품
    {"name": "공매도", "slug": "short-selling-tag"},
    {"name": "옵션만기", "slug": "options-expiry"},
    {"name": "선물", "slug": "futures"},
    # 투자 전략
    {"name": "분산투자", "slug": "diversification"},
    {"name": "포트폴리오", "slug": "portfolio"},
    {"name": "리스크관리", "slug": "risk-management"},
]


# ============================================================
# 필수 페이지 콘텐츠
# ============================================================
ABOUT_CONTENT = """
<div class="about-page">
<h2>머니노트365에 오신 것을 환영합니다</h2>
<p>머니노트365는 <strong>주식, 코인, 채권, 공매도, 선물옵션</strong> 등 금융 전반을 함께 공부하고 의견을 나누는 공간입니다.</p>

<h3>🎯 우리의 미션</h3>
<p>매일 아침, 국내외 금융 시장의 핵심 데이터를 분석하여 <strong>일일 투자 보고서</strong>를 제공합니다. 복잡한 시장을 쉽게 이해하고, 함께 투자 인사이트를 나누는 것이 목표입니다.</p>

<h3>📊 매일 제공하는 정보</h3>
<ul>
<li>🇺🇸 미국 증시 (S&P500, 나스닥, 다우존스) 분석</li>
<li>🇰🇷 국내 증시 (KOSPI, KOSDAQ) 동향</li>
<li>🪙 암호화폐 시장 현황</li>
<li>🏦 채권 및 금리 동향</li>
<li>📉 공매도 현황 분석</li>
<li>📊 선물 및 옵션 시장</li>
<li>🌍 글로벌 경제 지표</li>
</ul>

<h3>⚠️ 투자 유의사항</h3>
<p>본 사이트에서 제공하는 모든 정보는 <strong>교육 목적의 정보 제공</strong>이며, 투자 권유나 종목 추천이 아닙니다. 모든 투자 결정은 본인의 판단과 책임하에 이루어져야 하며, 투자 손실에 대한 책임은 투자자 본인에게 있습니다.</p>
</div>
"""

PRIVACY_CONTENT = """
<div class="privacy-page">
<h2>개인정보처리방침</h2>
<p><strong>최종 업데이트: 2025년 1월 1일</strong></p>

<h3>1. 개인정보의 수집 및 이용 목적</h3>
<p>머니노트365(이하 "본 사이트")는 댓글 서비스, 뉴스레터 구독 등의 서비스 제공을 위해 최소한의 개인정보를 수집합니다.</p>

<h3>2. 수집하는 개인정보 항목</h3>
<ul>
<li>댓글 작성 시: 닉네임, 이메일 주소 (선택)</li>
<li>뉴스레터 구독 시: 이메일 주소</li>
</ul>

<h3>3. 개인정보의 보유 및 이용기간</h3>
<p>수집된 개인정보는 서비스 제공 목적이 달성된 후 즉시 파기됩니다.</p>

<h3>4. 쿠키(Cookie) 정책</h3>
<p>본 사이트는 사용자 경험 향상을 위해 쿠키를 사용하며, Google Analytics 및 Google AdSense 서비스를 통해 방문자 분석 및 광고 서비스를 제공합니다. 사용자는 브라우저 설정을 통해 쿠키 사용을 거부할 수 있습니다.</p>

<h3>5. Google AdSense</h3>
<p>본 사이트는 Google AdSense를 통해 광고를 게재합니다. Google은 쿠키를 사용하여 사용자의 관심사에 기반한 광고를 제공할 수 있습니다. 자세한 내용은 <a href="https://policies.google.com/privacy" target="_blank" rel="nofollow">Google 개인정보처리방침</a>을 참고하세요.</p>

<h3>6. 개인정보 보호 책임자</h3>
<p>개인정보 관련 문의사항은 문의하기 페이지를 통해 연락해 주세요.</p>
</div>
"""

CONTACT_CONTENT = """
<div class="contact-page">
<h2>문의하기</h2>
<p>머니노트365에 대한 의견, 제안, 문의사항이 있으시면 아래 댓글이나 이메일로 연락해 주세요.</p>
<p>📧 투자 정보 공유, 오류 신고, 콘텐츠 제안 모두 환영합니다!</p>
<p>모든 문의는 영업일 기준 2~3일 이내 답변드립니다.</p>
<h3>💬 함께 만들어가는 공간</h3>
<p>각 포스트의 댓글을 통해 시장 의견을 나눠주세요. 여러분의 인사이트가 모여 더 좋은 분석을 만들어냅니다.</p>
</div>
"""

DISCLAIMER_CONTENT = """
<div class="disclaimer-page">
<h2>면책 조항 (Disclaimer)</h2>
<p>머니노트365에서 제공하는 모든 콘텐츠는 <strong>일반적인 정보 제공 및 교육 목적</strong>으로만 사용됩니다.</p>

<h3>⚠️ 투자 위험 고지</h3>
<ul>
<li>본 사이트의 모든 정보는 투자 권유, 종목 추천, 금융 상담이 아닙니다.</li>
<li>주식, 암호화폐, 선물옵션 등 모든 투자에는 원금 손실의 위험이 있습니다.</li>
<li>과거의 수익률이 미래의 수익을 보장하지 않습니다.</li>
<li>투자 결정은 반드시 본인의 판단과 책임하에 이루어져야 합니다.</li>
<li>본 사이트는 투자 손실에 대해 어떠한 책임도 지지 않습니다.</li>
</ul>

<h3>📊 정보의 정확성</h3>
<p>본 사이트에서 제공하는 시장 데이터는 공개된 API를 통해 자동으로 수집되며, 실시간 데이터와 차이가 있을 수 있습니다. 중요한 투자 결정 시에는 반드시 공식 거래소나 금융기관의 데이터를 확인하시기 바랍니다.</p>
</div>
"""


def setup_wordpress():
    """WordPress 전체 초기 세팅"""
    print("\n" + "="*60)
    print("  머니노트365 WordPress 초기 세팅 시작")
    print("="*60)

    # 연결 테스트
    if not test_connection():
        print("❌ WordPress 연결 실패. .env 설정을 확인하세요.")
        return False

    # 카테고리 생성
    print("\n📂 카테고리 생성 중...")
    cat_ids = {}
    for cat in CATEGORIES:
        cid = get_or_create_category(cat["name"], cat["slug"], cat["desc"])
        if cid:
            cat_ids[cat["slug"]] = cid

    # 태그 생성
    print("\n🏷️  태그 생성 중...")
    tag_ids = {}
    for tag in TAGS:
        tid = get_or_create_tag(tag["name"], tag["slug"])
        if tid:
            tag_ids[tag["slug"]] = tid

    # 필수 페이지 생성
    print("\n📄 필수 페이지 생성 중...")
    pages = [
        ("About — 머니노트365 소개", ABOUT_CONTENT, "about"),
        ("개인정보처리방침", PRIVACY_CONTENT, "privacy-policy"),
        ("문의하기", CONTACT_CONTENT, "contact"),
        ("면책 조항", DISCLAIMER_CONTENT, "disclaimer"),
    ]
    for title, content, slug in pages:
        create_page(title, content, slug)

    print("\n" + "="*60)
    print("  ✅ WordPress 초기 세팅 완료!")
    print(f"  카테고리: {len(cat_ids)}개 생성")
    print(f"  태그: {len(tag_ids)}개 생성")
    print(f"  페이지: {len(pages)}개 생성")
    print("="*60)

    return cat_ids, tag_ids


if __name__ == "__main__":
    setup_wordpress()
