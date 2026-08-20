# -*- coding: utf-8 -*-
"""
머니노트365 프리미엄 금융 테마 CSS 자동 적용
WordPress Customizer Additional CSS API를 통해 주입
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import base64
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")
WP_API_URL = os.getenv("WP_API_URL")

CUSTOM_CSS = """
/* ============================================================
   머니노트365 — 프리미엄 금융 블로그 커스텀 스타일
   ============================================================ */

@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Montserrat:wght@400;600;700;900&display=swap');

:root {
  --mn-navy:    #0A1628;
  --mn-navy2:   #112240;
  --mn-gold:    #F5B700;
  --mn-gold2:   #E0A800;
  --mn-green:   #00C896;
  --mn-red:     #FF4757;
  --mn-gray:    #8892A4;
  --mn-light:   #F4F6FA;
  --mn-white:   #FFFFFF;
  --mn-border:  #1E3A5F;
  --mn-font:    'Noto Sans KR', sans-serif;
  --mn-num:     'Montserrat', sans-serif;
  --mn-radius:  8px;
  --mn-shadow:  0 4px 24px rgba(0,0,0,0.18);
}

/* 기본 */
body {
  font-family: var(--mn-font) !important;
  background: var(--mn-light) !important;
  color: #1a2540 !important;
  line-height: 1.8 !important;
}

/* ============================================================
   헤더 — 실시간 지수 티커 느낌
   ============================================================ */
.site-header, #masthead, header {
  background: var(--mn-navy) !important;
  border-bottom: 3px solid var(--mn-gold) !important;
  box-shadow: 0 2px 20px rgba(0,0,0,0.4) !important;
}

.site-title a, .site-title, #site-title a {
  color: var(--mn-gold) !important;
  font-family: var(--mn-num) !important;
  font-weight: 900 !important;
  font-size: 1.6rem !important;
  letter-spacing: -0.5px !important;
  text-decoration: none !important;
}

.site-description, #site-description {
  color: var(--mn-gray) !important;
  font-size: 0.8rem !important;
  letter-spacing: 1px !important;
}

/* 네비게이션 */
.main-navigation a, #site-navigation a, nav a {
  color: rgba(255,255,255,0.85) !important;
  font-weight: 500 !important;
  font-size: 0.9rem !important;
  transition: color 0.2s !important;
}
.main-navigation a:hover, nav a:hover {
  color: var(--mn-gold) !important;
}

/* ============================================================
   포스트 카드
   ============================================================ */
.post, article, .entry {
  background: var(--mn-white) !important;
  border-radius: var(--mn-radius) !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
  border: 1px solid #e8edf5 !important;
  margin-bottom: 2rem !important;
  overflow: hidden !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
}
.post:hover, article:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12) !important;
}

/* 포스트 제목 */
.entry-title, h1.entry-title, h2.entry-title {
  font-family: var(--mn-font) !important;
  font-weight: 700 !important;
  color: var(--mn-navy) !important;
  line-height: 1.4 !important;
}
.entry-title a {
  color: var(--mn-navy) !important;
  text-decoration: none !important;
  transition: color 0.2s !important;
}
.entry-title a:hover {
  color: var(--mn-gold2) !important;
}

/* ============================================================
   보고서 본문 스타일
   ============================================================ */
.mn365-report {
  font-family: var(--mn-font);
  max-width: 860px;
  margin: 0 auto;
  padding: 0 1rem;
}

.report-header {
  background: linear-gradient(135deg, var(--mn-navy) 0%, var(--mn-navy2) 100%);
  border-radius: var(--mn-radius);
  padding: 2rem;
  margin-bottom: 2rem;
  border-left: 5px solid var(--mn-gold);
}

.report-date {
  color: var(--mn-gold);
  font-family: var(--mn-num);
  font-weight: 600;
  font-size: 0.9rem;
  letter-spacing: 0.5px;
  margin: 0 0 0.5rem !important;
}

.report-summary {
  color: rgba(255,255,255,0.9);
  font-size: 1.05rem;
  line-height: 1.7;
  margin: 0 !important;
}

/* 본문 h2 */
.mn365-report h2, .entry-content h2 {
  color: var(--mn-navy) !important;
  font-weight: 700 !important;
  font-size: 1.3rem !important;
  border-bottom: 2px solid var(--mn-gold) !important;
  padding-bottom: 0.5rem !important;
  margin: 2rem 0 1rem !important;
}

.mn365-report h3, .entry-content h3 {
  color: var(--mn-navy2) !important;
  font-weight: 600 !important;
  font-size: 1.1rem !important;
  margin: 1.5rem 0 0.5rem !important;
}

/* 시장 데이터 테이블 */
.mn365-report table, .market-table table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-family: var(--mn-num);
  font-size: 0.9rem;
  border-radius: var(--mn-radius);
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.mn365-report table thead, .market-table table thead {
  background: var(--mn-navy);
  color: var(--mn-gold);
}

.mn365-report table th {
  padding: 0.75rem 1rem;
  font-weight: 600;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
  text-align: left;
}

.mn365-report table td {
  padding: 0.6rem 1rem;
  border-bottom: 1px solid #e8edf5;
  color: #2c3e50;
}

.mn365-report table tr:nth-child(even) td {
  background: #f8fafc;
}

.mn365-report table tr:hover td {
  background: #eef2ff;
}

/* 등락 색상 */
.up, .positive { color: var(--mn-green) !important; font-weight: 600; }
.down, .negative { color: var(--mn-red) !important; font-weight: 600; }

/* 보고서 풋터 */
.report-footer {
  background: #f4f6fa;
  border: 1px solid #e0e7ef;
  border-radius: var(--mn-radius);
  padding: 1rem 1.5rem;
  margin-top: 2rem;
  font-size: 0.82rem;
  color: var(--mn-gray);
  font-style: italic;
}

/* ============================================================
   사이드바 & 위젯
   ============================================================ */
.widget, aside .widget {
  background: var(--mn-white) !important;
  border-radius: var(--mn-radius) !important;
  padding: 1.5rem !important;
  margin-bottom: 1.5rem !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
  border: 1px solid #e8edf5 !important;
}

.widget-title, .widgettitle {
  color: var(--mn-navy) !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
  border-bottom: 2px solid var(--mn-gold) !important;
  padding-bottom: 0.5rem !important;
  margin-bottom: 1rem !important;
}

/* ============================================================
   카테고리 & 태그
   ============================================================ */
.cat-links a, .tags-links a, a[rel="tag"], .entry-meta a {
  background: var(--mn-navy) !important;
  color: var(--mn-gold) !important;
  padding: 2px 10px !important;
  border-radius: 20px !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  text-decoration: none !important;
  display: inline-block !important;
  margin: 2px !important;
  transition: all 0.2s !important;
}
.cat-links a:hover, .tags-links a:hover, a[rel="tag"]:hover {
  background: var(--mn-gold) !important;
  color: var(--mn-navy) !important;
}

/* ============================================================
   푸터
   ============================================================ */
.site-footer, #colophon, footer {
  background: var(--mn-navy) !important;
  color: var(--mn-gray) !important;
  border-top: 2px solid var(--mn-gold) !important;
  padding: 2rem 0 !important;
}
.site-footer a { color: var(--mn-gold) !important; }
.site-info { color: var(--mn-gray) !important; font-size: 0.85rem !important; }

/* ============================================================
   버튼
   ============================================================ */
.button, button, input[type="submit"], .wp-block-button__link {
  background: var(--mn-gold) !important;
  color: var(--mn-navy) !important;
  border: none !important;
  border-radius: var(--mn-radius) !important;
  font-weight: 700 !important;
  padding: 0.6rem 1.5rem !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
}
.button:hover, button:hover, input[type="submit"]:hover {
  background: var(--mn-gold2) !important;
  transform: translateY(-1px) !important;
}

/* ============================================================
   페이지네이션
   ============================================================ */
.page-numbers, .nav-links a {
  background: var(--mn-white) !important;
  color: var(--mn-navy) !important;
  border: 1px solid #e0e7ef !important;
  border-radius: var(--mn-radius) !important;
  padding: 0.4rem 0.9rem !important;
  text-decoration: none !important;
  transition: all 0.2s !important;
}
.current.page-numbers {
  background: var(--mn-navy) !important;
  color: var(--mn-gold) !important;
}

/* ============================================================
   반응형
   ============================================================ */
@media (max-width: 768px) {
  .mn365-report { padding: 0 0.5rem; }
  .report-header { padding: 1.2rem; }
  .mn365-report table { font-size: 0.78rem; }
  .mn365-report table th, .mn365-report table td { padding: 0.5rem 0.6rem; }
  .site-title a { font-size: 1.2rem !important; }
}
"""


def apply_custom_css():
    """WordPress에 커스텀 CSS 적용 (wp_head 액션 훅 방식)"""
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{WP_USERNAME}:{WP_PASSWORD}'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    # WordPress Customizer API (theme mods)로 CSS 주입 시도
    # 방법 1: wp/v2/settings 엔드포인트
    try:
        resp = requests.get(f"{WP_API_URL}/settings", headers=headers, timeout=10)
        if resp.status_code == 200:
            settings = resp.json()
            # custom_css 설정이 있으면 업데이트
            update = requests.post(
                f"{WP_API_URL}/settings",
                json={"custom_css": CUSTOM_CSS},
                headers=headers,
                timeout=10
            )
            if update.status_code == 200:
                print("✅ 커스텀 CSS 적용 성공 (Settings API)")
                return True
    except Exception as e:
        print(f"  Settings API 시도 실패: {e}")

    # 방법 2: Custom CSS 전용 포스트 타입으로 저장
    try:
        resp = requests.post(
            f"{WP_URL}/wp-json/wp/v2/posts",
            json={
                "title": "mn365-custom-css",
                "content": f"<style>{CUSTOM_CSS}</style>",
                "status": "private",
                "slug": "mn365-style"
            },
            headers=headers,
            timeout=10
        )
        print("  CSS를 비공개 포스트로 저장했습니다.")
        print("  ⚠️  WordPress 관리자 → 외모 → 추가 CSS에 직접 붙여넣기를 권장합니다.")
        return True
    except Exception as e:
        print(f"  CSS 저장 실패: {e}")

    return False


def print_manual_css_guide():
    """수동 CSS 설치 가이드 출력"""
    print("\n" + "="*60)
    print("📋 수동 CSS 적용 방법")
    print("="*60)
    print(f"1. {WP_URL}/wp-admin 로그인")
    print("2. 왼쪽 메뉴: 외모 (Appearance) → 테마 편집기")
    print("   또는: 외모 → 사용자 정의하기 → 추가 CSS")
    print("3. 아래 CSS를 전체 복사하여 붙여넣기")
    print("4. '공개' 또는 '저장' 버튼 클릭")
    print("="*60)
    print("\n아래 CSS를 복사하세요:\n")
    print(CUSTOM_CSS[:500] + "\n... (전체 CSS는 setup/theme_setup.py 파일 참조)")


if __name__ == "__main__":
    result = apply_custom_css()
    if not result:
        print_manual_css_guide()
