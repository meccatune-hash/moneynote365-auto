# -*- coding: utf-8 -*-
"""
머니노트365 카테고리별 전문 보고서 생성기
매일 09:00 KST 실행
- 요일별 카테고리 로테이션
- 각 카테고리 특성에 맞는 전문 AI 보고서
- 텍스트 전용, 5000자+
"""
import os, re
from datetime import datetime, timezone, timedelta
from google import genai
from dotenv import load_dotenv

load_dotenv()
_client  = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
KST      = timezone(timedelta(hours=9))
SITE_URL = os.getenv("WP_URL", "https://kingbrightsucces.com")
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

# ─── 카테고리별 전문 프롬프트 ───────────────────────────

PROMPTS = {

"kr-stock": """
당신은 국내 주식시장 전문 애널리스트(CFA)입니다.
오늘 날짜: {date_kr}

아래 데이터를 바탕으로 한국 주식시장 심층 분석 보고서를 작성하세요.

시장 데이터:
{market_data}

=== 작성 규칙 ===
HTML 태그만 사용: h2, h3, p, ul, li, ol, table, thead, tbody, tr, th, td, blockquote, strong, em, hr
최소 5,000자 이상 (HTML 태그 제외)

=== 보고서 구조 ===
<h2>오늘의 국내 증시 핵심 정리</h2> - 수치 기반 요약 5개
<h2>KOSPI 심층 분석</h2> - 수급, 기술적 분석, 역사적 비교
<h2>KOSDAQ 심층 분석</h2> - 기술주, 바이오 동향
<h2>오늘의 주목 업종 & 종목</h2> - 상승/하락 업종 이유 분석
<h2>외국인·기관·개인 수급 분석</h2> - 세력별 동향
<h2>환율과 국내 증시 관계</h2> - 원달러 영향 분석
<h2>다음 거래일 전망</h2> - 주목할 이벤트, 기술적 지지/저항
<h2>국내 주식 투자 Q&A</h2> - 5개 Q&A
<h2>투자 용어 해설</h2> - 오늘 등장한 용어 3개
<h2>⚠️ 투자 유의사항</h2>

순수 HTML만 출력 (```없이)
""",

"us-stock": """
당신은 월스트리트 출신 미국 주식 전문 애널리스트입니다.
오늘 날짜: {date_kr}

시장 데이터:
{market_data}

=== 작성 규칙 ===
HTML 태그만 사용: h2, h3, p, ul, li, ol, table, thead, tbody, tr, th, td, blockquote, strong, em, hr
최소 5,000자 이상

=== 보고서 구조 ===
<h2>오늘의 미국 증시 핵심 요약</h2>
<h2>S&P500 심층 분석</h2> - 섹터별 등락, 기술적 분석, 역사적 비교
<h2>나스닥 & 기술주 분석</h2> - 빅테크(애플, 엔비디아, MS, 구글, 아마존, 메타) 동향
<h2>다우존스 & 전통 산업 분석</h2>
<h2>오늘의 주목 섹터</h2> - 강세/약세 섹터와 이유
<h2>연준(Fed) & 금리 동향</h2> - 통화정책과 증시 영향
<h2>실적 시즌 현황</h2> - 주요 기업 실적 발표 분석
<h2>VIX & 시장 심리 분석</h2>
<h2>내일 주목할 이벤트</h2>
<h2>미국 주식 투자 Q&A</h2> - 5개
<h2>투자 용어 해설</h2>
<h2>⚠️ 투자 유의사항</h2>

순수 HTML만 출력
""",

"crypto": """
당신은 블록체인 & 암호화폐 전문 분석가입니다.
오늘 날짜: {date_kr}

시장 데이터:
{market_data}

=== 보고서 구조 ===
<h2>오늘의 암호화폐 시장 핵심 정리</h2>
<h2>비트코인(BTC) 심층 분석</h2> - 가격, 온체인 지표, 기술적 분석
<h2>이더리움(ETH) 분석</h2>
<h2>알트코인 주요 동향</h2>
<h2>공포탐욕지수 해석</h2> - 현재 수치의 역사적 의미
<h2>기관 투자자 동향</h2> - ETF, 고래 움직임
<h2>블록체인 & 규제 뉴스</h2>
<h2>DeFi & NFT 시장 현황</h2>
<h2>암호화폐 투자 Q&A</h2> - 5개
<h2>블록체인 용어 해설</h2>
<h2>⚠️ 투자 유의사항 (암호화폐 특화)</h2>

최소 5,000자. 순수 HTML만 출력
""",

"bonds-rates": """
당신은 채권 & 금리 전문 애널리스트입니다.
오늘 날짜: {date_kr}

시장 데이터:
{market_data}

=== 보고서 구조 ===
<h2>오늘의 채권 & 금리 시장 요약</h2>
<h2>미국 국채 금리 분석</h2> - 2년물, 10년물, 30년물, 장단기 스프레드
<h2>한국 기준금리 & 채권 시장</h2>
<h2>연준(Fed) 통화정책 전망</h2> - 금리 인하/인상 시나리오
<h2>인플레이션 지표 분석</h2> - CPI, PPI, PCE
<h2>글로벌 중앙은행 동향</h2> - ECB, BOJ, BOK
<h2>달러 인덱스 & 외환 시장</h2>
<h2>금(Gold) & 안전자산 동향</h2>
<h2>채권 투자 전략</h2>
<h2>금리 & 채권 Q&A</h2> - 5개
<h2>채권 용어 해설</h2>
<h2>⚠️ 투자 유의사항</h2>

최소 5,000자. 순수 HTML만 출력
""",

"economic-indicators": """
당신은 거시경제 전문 이코노미스트입니다.
오늘 날짜: {date_kr}

시장 데이터:
{market_data}

=== 보고서 구조 ===
<h2>이번 주 주요 경제지표 캘린더</h2> - 발표 예정 지표 정리
<h2>미국 경제 현황 분석</h2> - GDP, 고용, 소비, 제조업
<h2>한국 경제 현황 분석</h2> - 수출, 소비자물가, 산업생산
<h2>인플레이션 & 디플레이션 분석</h2>
<h2>고용 시장 분석</h2> - 비농업 고용, 실업률, JOLTS
<h2>소비자 심리 & 소매판매</h2>
<h2>주택 시장 현황</h2>
<h2>경기 사이클 현 위치 판단</h2>
<h2>경제지표 Q&A</h2> - 5개
<h2>경제 용어 해설</h2>
<h2>⚠️ 투자 유의사항</h2>

최소 5,000자. 순수 HTML만 출력
""",

"investment-strategy": """
당신은 20년 경력의 포트폴리오 매니저 & 투자 전략가입니다.
오늘 날짜: {date_kr}

시장 데이터:
{market_data}

=== 보고서 구조 ===
<h2>오늘의 투자 전략 핵심 포인트</h2>
<h2>현재 시장 국면 진단</h2> - 불마켓/베어마켓/사이드웨이
<h2>섹터 로테이션 전략</h2> - 어느 섹터로 돈이 흐르나
<h2>단기 전략 (1~2주)</h2> - 구체적 액션 플랜
<h2>중기 전략 (1~3개월)</h2>
<h2>장기 전략 (6개월~1년)</h2>
<h2>포트폴리오 리밸런싱 가이드</h2>
<h2>리스크 관리 전략</h2> - 손절, 분할매수, 헤징
<h2>투자 대가의 지혜</h2> - 버핏, 린치, 그레이엄 명언 & 현재 적용
<h2>투자 전략 Q&A</h2> - 5개
<h2>투자 전략 용어 해설</h2>
<h2>⚠️ 투자 유의사항</h2>

최소 5,000자. 순수 HTML만 출력
""",

"short-selling": """
당신은 공매도 & 파생상품 전문 트레이더입니다.
오늘 날짜: {date_kr}

시장 데이터:
{market_data}

=== 보고서 구조 ===
<h2>오늘의 공매도 시장 현황</h2>
<h2>공매도 잔고 TOP 종목 분석</h2> - KOSPI/KOSDAQ 상위 종목
<h2>외국인 공매도 동향</h2>
<h2>공매도 비율과 주가 관계 분석</h2>
<h2>미국 공매도 현황</h2> - Short Interest 높은 종목
<h2>숏스퀴즈 가능성 분석</h2>
<h2>한국 공매도 제도 현황</h2>
<h2>공매도 관련 규제 및 이슈</h2>
<h2>공매도 Q&A</h2> - 5개
<h2>공매도 용어 해설</h2>
<h2>⚠️ 투자 유의사항</h2>

최소 5,000자. 순수 HTML만 출력
""",

"futures-options": """
당신은 선물 & 옵션 전문 트레이더 & 강사입니다.
오늘 날짜: {date_kr}

시장 데이터:
{market_data}

=== 보고서 구조 ===
<h2>오늘의 선물 & 옵션 시장 요약</h2>
<h2>KOSPI200 선물 분석</h2> - 베이시스, 콘탱고/백워데이션
<h2>미국 주가지수 선물</h2> - S&P500, 나스닥, 다우 선물
<h2>원자재 선물 분석</h2> - 금, 오일, 농산물
<h2>옵션 시장 분석</h2> - Put/Call Ratio, IV, 만기일 효과
<h2>주요 선물 포지션 분석</h2> - COT Report 해석
<h2>선물·옵션 투자 전략</h2>
<h2>만기일 캘린더</h2>
<h2>선물 & 옵션 Q&A</h2> - 5개
<h2>선물·옵션 용어 해설</h2>
<h2>⚠️ 투자 유의사항</h2>

최소 5,000자. 순수 HTML만 출력
""",

"global-stock": """
당신은 글로벌 주식 & 이머징마켓 전문 애널리스트입니다.
오늘 날짜: {date_kr}

시장 데이터:
{market_data}

=== 보고서 구조 ===
<h2>오늘의 글로벌 증시 요약</h2>
<h2>유럽 증시 분석</h2> - DAX, FTSE100, CAC40, EURO STOXX
<h2>일본 증시 분석</h2> - 닛케이225, 엔화 동향
<h2>중국 & 홍콩 증시</h2> - 상하이종합, 항셍지수
<h2>이머징마켓 동향</h2> - 인도, 브라질, 베트남 등
<h2>글로벌 섹터 트렌드</h2>
<h2>환율 & 글로벌 자금 흐름</h2>
<h2>지정학적 리스크와 글로벌 증시</h2>
<h2>글로벌 ETF 투자 전략</h2>
<h2>글로벌 주식 Q&A</h2> - 5개
<h2>글로벌 투자 용어 해설</h2>
<h2>⚠️ 투자 유의사항</h2>

최소 5,000자. 순수 HTML만 출력
""",

"invest-study": """
당신은 투자 교육 전문가이자 재무설계사(CFP)입니다.
오늘 날짜: {date_kr}

=== 오늘의 투자 공부 주제 (날짜 기반 로테이션) ===
날짜의 일(day)을 기준으로 주제 선택:
1-7일: 주식 투자 기초 (PER, PBR, ROE 등 기업 분석)
8-14일: 기술적 분석 (이동평균, MACD, RSI 등)
15-21일: 포트폴리오 이론 (분산투자, 자산배분)
22-28일: 거시경제 & 금리 이해
29-31일: 투자 심리 & 행동경제학

오늘 날짜({date_kr})에 맞는 주제로 깊이 있는 교육 콘텐츠 작성.

=== 작성 규칙 ===
- 완전 초보자도 이해할 수 있게 작성
- 실제 사례와 숫자로 설명
- 비유와 예시 풍부하게
- 최소 5,000자

=== 보고서 구조 ===
<h2>오늘 배울 내용 미리보기</h2>
<h2>핵심 개념 1 - 기초 설명</h2>
<h2>핵심 개념 2 - 실제 사례</h2>
<h2>핵심 개념 3 - 실전 적용</h2>
<h2>초보자가 흔히 하는 실수</h2>
<h2>실전 연습 문제</h2>
<h2>오늘 배운 내용 정리 퀴즈</h2>
<h2>추천 학습 순서</h2>
<h2>투자 공부 Q&A</h2> - 5개
<h2>오늘의 용어 총정리</h2>
<h2>다음 시간 예고</h2>

순수 HTML만 출력
""",
}

# 요일별 카테고리 스케줄
WEEKLY_SCHEDULE = {
    0: ["kr-stock",     "invest-study"],      # 월
    1: ["us-stock",     "futures-options"],   # 화
    2: ["crypto",       "global-stock"],      # 수
    3: ["bonds-rates",  "economic-indicators"], # 목
    4: ["investment-strategy", "short-selling"], # 금
    5: ["kr-stock",     "crypto"],            # 토
    6: ["us-stock",     "global-stock"],      # 일
}


def _call_gemini(prompt: str) -> str:
    models = ["gemini-3.6-flash", "gemini-2.5-pro", "gemini-2.5-flash"]
    for model in models:
        try:
            resp = _client.models.generate_content(model=model, contents=prompt)
            text = resp.text.strip()
            text = re.sub(r'^```html?\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*```\s*$', '', text)
            if len(text) > 500:
                print(f"    [모델: {model}] 생성 성공 ({len(text):,}자)")
                return text.strip()
        except Exception as e:
            print(f"    [{model}] 오류: {str(e)[:80]}")
    return "<p>보고서 생성 오류</p>"


def _make_footer(cat_slug: str) -> str:
    cat_links = {
        "kr-stock":            "국내 주식",
        "us-stock":            "미국 주식",
        "crypto":              "암호화폐",
        "bonds-rates":         "채권 & 금리",
        "economic-indicators": "경제 지표",
        "investment-strategy": "투자 전략",
        "short-selling":       "공매도 현황",
        "futures-options":     "선물 & 옵션",
        "global-stock":        "글로벌 주식",
        "invest-study":        "투자 공부방",
    }
    links = " | ".join(
        f'<a href="{SITE_URL}/category/{slug}/">{name}</a>'
        for slug, name in cat_links.items()
        if slug != cat_slug
    )
    now = datetime.now(KST)
    return f"""
<hr>
<p><strong>📅 발행일:</strong> {now.strftime('%Y년 %m월 %d일 %H:%M')} KST &nbsp;|&nbsp;
<strong>데이터 출처:</strong> Yahoo Finance, CoinGecko, 한국거래소</p>
<p><strong>🔗 다른 카테고리:</strong> {links}</p>
<hr>
<p><strong>※ 면책 조항:</strong> 본 보고서는 교육 목적의 정보 제공이며, 특정 종목의 매수·매도를 권유하지 않습니다. 
모든 투자 결정과 손익은 투자자 본인의 책임입니다. 과거 수익률이 미래를 보장하지 않습니다.</p>
"""


def generate_category_post(cat_slug: str, market_data_str: str) -> dict:
    """카테고리별 전문 보고서 생성. dict 반환: title, content, excerpt"""
    now     = datetime.now(KST)
    wd      = WEEKDAYS[now.weekday()]
    date_kr = now.strftime(f"%Y년 %m월 %d일({wd})")
    ds      = now.strftime("%Y.%m.%d")

    CAT_NAMES = {
        "kr-stock":            ("🇰🇷 국내 주식",          "국내증시 KOSPI KOSDAQ 한국주식"),
        "us-stock":            ("🇺🇸 미국 주식",          "미국증시 S&P500 나스닥 월스트리트"),
        "crypto":              ("🪙 암호화폐",             "비트코인 이더리움 암호화폐 코인"),
        "bonds-rates":         ("🏦 채권 & 금리",          "채권 금리 연준 중앙은행 인플레이션"),
        "economic-indicators": ("📈 경제 지표",            "GDP 고용 CPI 경제지표 거시경제"),
        "investment-strategy": ("💡 투자 전략",            "포트폴리오 투자전략 자산배분 리밸런싱"),
        "short-selling":       ("📉 공매도 현황",          "공매도 숏셀링 공매도잔고 숏스퀴즈"),
        "futures-options":     ("📊 선물 & 옵션",          "선물 옵션 파생상품 KOSPI200선물"),
        "global-stock":        ("🌏 글로벌 주식",          "유럽증시 일본증시 이머징마켓 글로벌"),
        "invest-study":        ("📚 투자 공부방",          "주식기초 투자교육 재무분석 초보투자"),
    }

    cat_name, keywords = CAT_NAMES.get(cat_slug, ("투자 분석", "투자 분석"))
    prompt_template    = PROMPTS.get(cat_slug, PROMPTS["investment-strategy"])

    print(f"  [{cat_name}] 보고서 생성 중...")
    body    = _call_gemini(prompt_template.format(
        date_kr=date_kr,
        market_data=market_data_str,
    ))
    footer  = _make_footer(cat_slug)
    content = f"{body}\n{footer}"

    title   = f"[{ds}({wd})] {cat_name} 분석 보고서 | {date_kr} 시장 심층 분석 — 머니노트365"
    excerpt = (
        f"{date_kr} {cat_name} 전문 분석 보고서. "
        f"{keywords}. "
        f"머니노트365 AI 애널리스트가 제공하는 상세 투자 보고서."
    )

    return {"title": title, "content": content, "excerpt": excerpt,
            "cat_slug": cat_slug}
