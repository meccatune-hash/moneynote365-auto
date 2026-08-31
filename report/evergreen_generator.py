# -*- coding: utf-8 -*-
"""
애드센스 특화 상록 교육 콘텐츠 생성기
- 시장 데이터 불필요 (언제 읽어도 가치 있는 글)
- 각 카테고리에 최적화된 교육/가이드 형식
- 5,000자+ 상세 텍스트
- AdSense 정책 완전 준수
"""
import os, re, requests, base64, time
from datetime import datetime, timezone, timedelta
from google import genai
from dotenv import load_dotenv

load_dotenv()
_client  = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
KST      = timezone(timedelta(hours=9))
SITE_URL = os.getenv("WP_URL", "https://kingbrightsucces.com")

# ── 카테고리별 상록 콘텐츠 주제 목록 ─────────────────────
EVERGREEN_TOPICS = {
    "kr-stock": [
        {
            "title": "KOSPI 완전 정복 가이드 — 코스피 지수 뜻부터 투자 방법까지 초보자 설명",
            "keyword": "코스피 투자 방법 초보자",
            "focus": "KOSPI 지수의 정의, 구성 원리, 역사, 투자 방법, 주의사항을 완전 초보자 기준으로 상세히 설명"
        },
        {
            "title": "국내 주식 투자 시작하기 — 계좌 개설부터 첫 매수까지 단계별 완전 가이드",
            "keyword": "국내 주식 투자 시작 방법",
            "focus": "증권 계좌 개설, MTS/HTS 사용법, 주문 방법, 세금, 배당 등 실전 투자 전 단계 설명"
        },
        {
            "title": "PER, PBR, ROE 완벽 이해 — 국내 주식 기업 분석 핵심 지표 해설",
            "keyword": "PER PBR ROE 뜻 계산법",
            "focus": "PER·PBR·ROE·EPS·배당수익률 등 기업 가치 분석 지표를 실제 국내 기업 사례로 쉽게 설명"
        },
    ],
    "us-stock": [
        {
            "title": "미국 주식 투자 완전 가이드 — S&P500부터 나스닥까지 미국 증시 완벽 이해",
            "keyword": "미국 주식 투자 방법 한국인",
            "focus": "미국 주식 시장 구조, 거래 시간, 환전, 세금(양도세·배당세), 주요 지수 설명, 투자 방법"
        },
        {
            "title": "미국 ETF 완전 정복 — VOO, QQQ, SPY 차이와 장기 투자 전략",
            "keyword": "미국 ETF 추천 VOO QQQ SPY",
            "focus": "S&P500 ETF(VOO·SPY·IVV), 나스닥 ETF(QQQ·QQQM), 배당 ETF 비교, 장기 복리 투자 전략"
        },
        {
            "title": "미국 주식 세금 완전 정리 — 양도소득세, 배당소득세, 환율 처리 방법",
            "keyword": "미국 주식 세금 신고 방법",
            "focus": "미국 주식 양도소득세(연 250만원 공제), 배당 원천징수(15%), 종합소득세, 세금 신고 시기와 방법"
        },
    ],
    "crypto": [
        {
            "title": "비트코인 완전 가이드 — 비트코인 뜻, 작동 원리, 투자 방법 처음부터 끝까지",
            "keyword": "비트코인 뜻 투자 방법 초보자",
            "focus": "비트코인 탄생 역사, 블록체인 원리, 반감기, 거래소 선택, 지갑, 투자 시 주의사항 완전 설명"
        },
        {
            "title": "암호화폐 투자 세금 완전 정리 — 2024년 기준 가상자산 세금 신고 방법",
            "keyword": "암호화폐 세금 신고 방법 2024",
            "focus": "가상자산 양도소득세, 기타소득세, 취득원가 계산법, 해외 거래소 세금, 신고 시기와 방법"
        },
        {
            "title": "이더리움 vs 비트코인 비교 분석 — 용도, 기술, 투자 관점 완전 정리",
            "keyword": "이더리움 비트코인 차이 비교",
            "focus": "비트코인(가치저장)과 이더리움(스마트컨트랙트) 근본적 차이, 기술 구조, 활용처, 투자 관점 비교"
        },
    ],
    "bonds-rates": [
        {
            "title": "채권 투자 완전 가이드 — 채권 뜻, 종류, 수익률 계산, 투자 방법 총정리",
            "keyword": "채권 투자 방법 초보자 가이드",
            "focus": "채권 정의, 국채·회사채·지방채 종류, 만기수익률 계산, 금리와 채권가격 역관계, 투자 방법"
        },
        {
            "title": "금리와 주식시장 관계 완전 분석 — 기준금리 인상·인하가 투자에 미치는 영향",
            "keyword": "금리 인상 주식 영향 분석",
            "focus": "기준금리 개념, 금리와 주식·채권·부동산·환율의 상관관계, 금리 사이클과 투자 전략"
        },
    ],
    "economic-indicators": [
        {
            "title": "경제지표 완전 정복 — CPI, GDP, 고용지표를 투자에 활용하는 방법",
            "keyword": "경제지표 뜻 투자 활용법 CPI GDP",
            "focus": "CPI·PPI·GDP·비농업고용·실업률·소매판매 등 핵심 경제지표 정의, 발표 시기, 투자 해석 방법"
        },
        {
            "title": "인플레이션 완전 이해 — 물가 상승이 내 투자에 미치는 영향과 대처법",
            "keyword": "인플레이션 뜻 투자 대처법",
            "focus": "인플레이션 정의, 종류, 원인, 하이퍼인플레이션 사례, 인플레이션 헤지 자산(금·부동산·TIPS), 투자 전략"
        },
    ],
    "investment-strategy": [
        {
            "title": "포트폴리오 구성 완전 가이드 — 자산배분부터 리밸런싱까지 실전 투자 전략",
            "keyword": "포트폴리오 구성 방법 자산배분",
            "focus": "포트폴리오 이론, 분산투자 원칙, 주식·채권·현금·대안자산 배분, 연령별 포트폴리오, 리밸런싱 방법"
        },
        {
            "title": "가치투자 완전 가이드 — 워런 버핏처럼 저평가 주식 찾는 방법",
            "keyword": "가치투자 방법 저평가 주식 찾기",
            "focus": "가치투자 철학, 내재가치 계산법, 안전마진, 버핏·그레이엄의 투자 원칙, 국내 적용 방법"
        },
        {
            "title": "달러 비용 평균법(DCA) 완전 정복 — 적립식 투자로 시장 타이밍 극복하기",
            "keyword": "달러비용평균법 DCA 적립식 투자",
            "focus": "DCA 개념, 일시투자 vs 분할투자 비교, 실제 수익률 시뮬레이션, 장단점, 최적 실행 방법"
        },
    ],
    "short-selling": [
        {
            "title": "공매도 완전 이해 — 공매도 뜻, 작동 원리, 개인 투자자 영향 분석",
            "keyword": "공매도 뜻 작동 원리 이해",
            "focus": "공매도 정의, 대차거래·대주거래 차이, 숏스퀴즈, 공매도가 주가에 미치는 영향, 한국 공매도 제도"
        },
        {
            "title": "공매도 잔고 분석으로 투자 기회 찾기 — 공매도 데이터 활용 투자 전략",
            "keyword": "공매도 잔고 분석 투자 전략",
            "focus": "공매도 잔고 데이터 보는 법, 공매도 비율 해석, 숏스퀴즈 포착 방법, 실제 사례 분석"
        },
    ],
    "futures-options": [
        {
            "title": "선물 거래 완전 가이드 — 선물이란 무엇인지 기초부터 위험까지 완전 설명",
            "keyword": "선물 거래 뜻 방법 초보자",
            "focus": "선물 계약 개념, 레버리지 원리, 증거금, 롤오버, KOSPI200 선물 거래 방법, 리스크 관리"
        },
        {
            "title": "옵션 거래 완전 정복 — 콜옵션·풋옵션 기초부터 실전 전략까지",
            "keyword": "옵션 거래 콜 풋 뜻 방법",
            "focus": "옵션 기본 개념(콜·풋·행사가·만기), 프리미엄 결정 요인, 델타·감마·세타 설명, 기초 옵션 전략"
        },
    ],
    "global-stock": [
        {
            "title": "글로벌 분산 투자 완전 가이드 — 미국·유럽·신흥국 ETF로 세계에 투자하기",
            "keyword": "글로벌 분산 투자 ETF 방법",
            "focus": "글로벌 분산 투자 필요성, 선진국·신흥국 ETF 비교, 환헤지 여부, 세금, 실전 포트폴리오 구성"
        },
        {
            "title": "일본·유럽·중국 주식 시장 비교 — 각국 증시 특성과 투자 방법 완전 분석",
            "keyword": "일본 유럽 중국 주식 투자 방법",
            "focus": "미국 외 글로벌 주요 증시(일본·독일·영국·중국·인도) 특성, 접근 방법(ETF·직접투자), 리스크"
        },
    ],
    "invest-study": [
        {
            "title": "주식 투자 완전 입문 — 주식이란 무엇인지 처음부터 배우는 주식 기초 교과서",
            "keyword": "주식 투자 입문 기초 배우기",
            "focus": "주식 정의, 주식회사 구조, 주가 결정 원리, 배당, 유상증자, 시가총액, 주가지수 등 완전 기초"
        },
        {
            "title": "재무제표 읽는 법 — 손익계산서·대차대조표·현금흐름표 완전 이해 가이드",
            "keyword": "재무제표 읽는 법 주식 분석",
            "focus": "손익계산서·재무상태표·현금흐름표 구조와 핵심 항목, 실제 기업 재무제표 분석 예시"
        },
        {
            "title": "기술적 분석 완전 정복 — 이동평균선, MACD, RSI로 매매 타이밍 잡는 법",
            "keyword": "기술적 분석 이동평균 MACD RSI",
            "focus": "캔들차트, 이동평균선(5·20·60·120일), MACD, RSI, 볼린저 밴드 등 주요 보조지표 설명과 활용법"
        },
    ],
    "morning-news": [
        {
            "title": "글로벌 뉴스가 한국 주식에 미치는 영향 — 해외 뉴스 투자에 활용하는 방법",
            "keyword": "글로벌 뉴스 주식 영향 분석",
            "focus": "미국 FOMC, 고용지표, 기업 실적, 지정학 뉴스 등이 KOSPI에 미치는 영향과 뉴스 해석 방법"
        },
    ],
}


def _call_gemini(prompt: str) -> str:
    models = ["gemini-3.6-flash", "gemini-2.5-pro"]
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
    return "<p>콘텐츠 생성 오류</p>"


EVERGREEN_PROMPT = """
당신은 국내 최고 수준의 금융·투자 전문 작가이자 교육자입니다.

아래 주제로 구글 애드센스 승인에 최적화된 상록 교육 콘텐츠를 작성하세요.

제목: {title}
핵심 키워드: {keyword}
글의 초점: {focus}

=== 절대 준수 규칙 ===
1. 순수 HTML만 사용: h2, h3, p, ul, li, ol, table, thead, tbody, tr, th, td, blockquote, strong, em, hr
2. div, span, style, script, img, iframe 절대 금지
3. 최소 6,000자 이상 (HTML 태그 제외 순수 텍스트)
4. 완전히 독창적인 교육 콘텐츠 (저작권 없음)
5. 초보자도 이해 가능한 쉬운 설명
6. 실제 예시와 숫자로 설명
7. 특정 종목 매수/매도 권유 절대 금지

=== 콘텐츠 구조 (반드시 이 순서로) ===

<h2>이 글에서 배울 내용</h2>
핵심 포인트 5~7개 불릿으로 정리

<h2>[소제목 1] — 기초 개념 완전 이해</h2>
개념 설명 600자+, 비유와 예시 포함

<h2>[소제목 2] — 원리와 작동 방식</h2>
600자+, 도표 또는 단계별 설명

<h2>[소제목 3] — 핵심 용어 정리</h2>
관련 용어 5~8개를 표(table)로 정리

<h2>[소제목 4] — 실전 투자 적용법</h2>
실제 어떻게 활용하는지 600자+

<h2>[소제목 5] — 초보자가 흔히 하는 실수</h2>
실수 5개 + 각 해결책

<h2>[소제목 6] — 자주 묻는 질문 (FAQ)</h2>
Q&A 형식으로 6개 질문과 상세 답변

<h2>[소제목 7] — 핵심 요약 및 결론</h2>
이 글의 핵심을 3~5개 문장으로

<h2>⚠️ 투자 유의사항</h2>
면책조항 (교육 목적, 투자 권유 아님)

출력: 순수 HTML만 출력 (``` 없이)
"""


def generate_evergreen_post(cat_slug: str, topic: dict) -> dict:
    now     = datetime.now(KST)
    prompt  = EVERGREEN_PROMPT.format(**topic)

    print(f"    주제: {topic['title'][:50]}...")
    body = _call_gemini(prompt)

    cat_links = " | ".join([
        f'<a href="{SITE_URL}/category/kr-stock/">국내 주식</a>',
        f'<a href="{SITE_URL}/category/us-stock/">미국 주식</a>',
        f'<a href="{SITE_URL}/category/crypto/">암호화폐</a>',
        f'<a href="{SITE_URL}/category/investment-strategy/">투자 전략</a>',
        f'<a href="{SITE_URL}/category/invest-study/">투자 공부방</a>',
    ])

    footer = f"""
<hr>
<p><strong>관련 카테고리:</strong> {cat_links}</p>
<p><strong>📅 최종 업데이트:</strong> {now.strftime('%Y년 %m월')} | <strong>출처:</strong> 머니노트365 투자 교육 팀</p>
<hr>
<p><strong>※ 면책 조항:</strong> 본 콘텐츠는 투자 교육 목적으로 작성되었으며, 특정 종목의 매수·매도를 권유하지 않습니다.
모든 투자 결정과 손익은 투자자 본인의 책임입니다.</p>
"""
    content = body + footer
    excerpt = (
        f"{topic['keyword']} 완전 가이드. "
        f"머니노트365가 제공하는 {topic['title'][:30]} 교육 콘텐츠. "
        f"초보 투자자를 위한 상세 설명."
    )

    return {
        "title":   topic["title"],
        "content": content,
        "excerpt": excerpt,
        "cat_slug": cat_slug,
    }
