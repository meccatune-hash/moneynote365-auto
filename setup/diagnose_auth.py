# -*- coding: utf-8 -*-
"""
WordPress 로그인 디버그 + Application Password 수동 생성 안내
"""
import sys

import requests
import os
import re
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")
WP_API_URL = os.getenv("WP_API_URL")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})


def wp_login():
    login_url = f"{WP_URL}/wp-login.php"
    
    # Step 1: 로그인 페이지 접속해서 쿠키 받기
    r1 = session.get(login_url, timeout=15)
    print(f"  로그인 페이지 GET: {r1.status_code}")
    
    payload = {
        "log": WP_USERNAME,
        "pwd": WP_PASSWORD,
        "wp-submit": "Log In",
        "redirect_to": "/wp-admin/",
        "testcookie": "1",
    }
    
    r2 = session.post(login_url, data=payload, allow_redirects=True, timeout=20)
    print(f"  로그인 POST: {r2.status_code}, 최종 URL: {r2.url}")
    
    # 쿠키 확인
    logged_in_cookies = [c.name for c in session.cookies if "logged_in" in c.name]
    print(f"  로그인 쿠키: {logged_in_cookies}")
    
    # wp-admin 접근 확인
    r3 = session.get(f"{WP_URL}/wp-admin/", timeout=15)
    is_admin = "wp-admin" in r3.url and r3.status_code == 200
    print(f"  wp-admin 접근: {r3.status_code}, 성공={is_admin}")
    
    return is_admin, r3


def get_nonce_from_admin(admin_resp):
    """관리자 페이지에서 REST API nonce 추출"""
    patterns = [
        r'"nonce"\s*:\s*"([a-f0-9]+)"',
        r'wpApiSettings.*?"nonce"\s*:\s*"([a-f0-9]+)"',
        r'rest_nonce["\s]*:\s*["\']([a-f0-9]+)',
    ]
    for p in patterns:
        m = re.search(p, admin_resp.text)
        if m:
            return m.group(1)
    
    # 직접 nonce 요청
    r = session.post(f"{WP_URL}/wp-admin/admin-ajax.php", 
                     data={"action": "rest-nonce"}, timeout=10)
    if r.status_code == 200 and len(r.text) > 5:
        return r.text.strip()
    
    return None


def try_create_via_nonce(nonce):
    headers = {"X-WP-Nonce": nonce, "Content-Type": "application/json"}
    r = session.post(
        f"{WP_API_URL}/users/me/application-passwords",
        json={"name": "MN365-AutoBot"},
        headers=headers,
        timeout=10
    )
    print(f"  App Password 생성 시도: {r.status_code}")
    if r.status_code == 201:
        return r.json().get("password")
    print(f"  응답: {r.text[:200]}")
    return None


def verify_user_role():
    """현재 사용자 권한 확인"""
    import base64
    token = base64.b64encode(f"{WP_USERNAME}:{WP_PASSWORD}".encode()).decode()
    r = requests.get(
        f"{WP_API_URL}/users/me",
        headers={"Authorization": f"Basic {token}"},
        timeout=10
    )
    print(f"\n  사용자 정보 조회: {r.status_code}")
    if r.status_code == 200:
        user = r.json()
        print(f"  이름: {user.get('name')}")
        print(f"  역할: {user.get('roles', [])}")
        print(f"  능력: {list(user.get('capabilities', {}).keys())[:5]}")
    else:
        print(f"  응답: {r.text[:150]}")


if __name__ == "__main__":
    print("="*60)
    print("  WordPress 인증 진단")
    print("="*60)
    
    # 현재 권한 확인
    print("\n[사용자 권한 확인]")
    verify_user_role()
    
    # 로그인 시도
    print("\n[쿠키 로그인 시도]")
    logged_in, admin_resp = wp_login()
    
    if logged_in:
        print("\n  [OK] 로그인 성공!")
        nonce = get_nonce_from_admin(admin_resp)
        print(f"  Nonce: {nonce}")
        if nonce:
            pw = try_create_via_nonce(nonce)
            if pw:
                print(f"\n  [SUCCESS] App Password: {pw}")
                # .env 업데이트
                with open(".env", "r") as f:
                    env = f.read()
                env = env.replace(f"WP_PASSWORD={WP_PASSWORD}", f"WP_PASSWORD={pw}")
                with open(".env", "w") as f:
                    f.write(env)
                print("  .env 업데이트 완료. wp_setup.py를 다시 실행하세요.")
    else:
        print("\n  [FAIL] 자동 로그인 불가 - 수동으로 Application Password 생성 필요")
        print("\n" + "="*60)
        print("  ** 수동 Application Password 생성 방법 **")
        print("="*60)
        print(f"\n  1. 브라우저에서 아래 URL로 이동:")
        print(f"     {WP_URL}/wp-admin/profile.php")
        print(f"\n  2. 페이지 맨 아래 'Application Passwords' 섹션 찾기")
        print(f"\n  3. New Application Password Name: MN365-AutoBot")
        print(f"     'Add New Application Password' 클릭")
        print(f"\n  4. 생성된 비밀번호 복사 후 여기에 붙여넣기")
        print(f"\n  5. 또는 아래 방법으로 REST API에 쓰기 권한 부여:")
        print(f"     - 플러그인 설치: 'Application Passwords' by WordPress.org")
        print(f"     - 또는 'JSON Basic Authentication' 플러그인")
