# -*- coding: utf-8 -*-
"""
WordPress 쿠키 + Nonce 인증으로 Application Password 생성
일반 ID/비밀번호로 로그인 → 세션 쿠키 획득 → App Password 생성
"""
import sys

import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")
WP_API_URL = os.getenv("WP_API_URL")

session = requests.Session()


def wp_login():
    """WordPress 관리자 로그인 → 세션 쿠키 획득"""
    login_url = f"{WP_URL}/wp-login.php"
    payload = {
        "log": WP_USERNAME,
        "pwd": WP_PASSWORD,
        "wp-submit": "Log+In",
        "redirect_to": f"{WP_URL}/wp-admin/",
        "testcookie": "1",
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": login_url,
    }
    # 쿠키 설정
    session.cookies.set("wordpress_test_cookie", "WP+Cookie+check")
    resp = session.post(login_url, data=payload, headers=headers, allow_redirects=True, timeout=15)
    
    if "wp-admin" in resp.url or "dashboard" in resp.text.lower() or any("wordpress_logged_in" in c.name for c in session.cookies):
        print("[OK] WordPress 로그인 성공!")
        return True
    else:
        print(f"[FAIL] 로그인 실패. URL: {resp.url}")
        print(f"  쿠키: {[c.name for c in session.cookies]}")
        return False


def get_nonce():
    """REST API 용 nonce 가져오기"""
    nonce_url = f"{WP_URL}/wp-admin/admin-ajax.php"
    resp = session.post(nonce_url, data={"action": "rest-nonce"}, timeout=10)
    if resp.status_code == 200 and resp.text.strip():
        nonce = resp.text.strip()
        print(f"[OK] Nonce 획득: {nonce[:10]}...")
        return nonce
    
    # 대안: wp-admin 페이지에서 직접 추출
    admin_resp = session.get(f"{WP_URL}/wp-admin/", timeout=10)
    import re
    match = re.search(r'"nonce":"([a-f0-9]+)"', admin_resp.text)
    if match:
        nonce = match.group(1)
        print(f"[OK] Nonce 추출 성공: {nonce[:10]}...")
        return nonce
    
    print("[WARN] Nonce 획득 실패")
    return None


def create_application_password(nonce):
    """Application Password 생성"""
    headers = {
        "X-WP-Nonce": nonce,
        "Content-Type": "application/json",
    }
    data = {"name": "MN365-AutoBot"}
    resp = session.post(
        f"{WP_API_URL}/users/me/application-passwords",
        json=data,
        headers=headers,
        timeout=10,
    )
    if resp.status_code == 201:
        result = resp.json()
        app_password = result.get("password", "")
        print(f"[OK] Application Password 생성 성공!")
        print(f"     Password: {app_password}")
        return app_password
    else:
        print(f"[FAIL] App Password 생성 실패: {resp.status_code} - {resp.text[:200]}")
        return None


def test_app_password(app_password):
    """생성된 App Password로 쓰기 테스트"""
    import base64
    credentials = f"{WP_USERNAME}:{app_password}"
    token = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }
    # 테스트 카테고리 생성
    resp = requests.post(
        f"{WP_API_URL}/categories",
        json={"name": "TEST-MN365", "slug": "test-mn365-temp"},
        headers=headers,
        timeout=10,
    )
    if resp.status_code == 201:
        cat_id = resp.json()["id"]
        print(f"[OK] App Password 쓰기 권한 확인 완료! (테스트 카테고리 ID: {cat_id})")
        # 테스트 카테고리 삭제
        requests.delete(f"{WP_API_URL}/categories/{cat_id}?force=true", headers=headers, timeout=10)
        return True
    else:
        print(f"[FAIL] 쓰기 테스트 실패: {resp.status_code} - {resp.text[:150]}")
        return False


def save_app_password_to_env(app_password):
    """.env 파일에 App Password 저장"""
    with open(".env", "r", encoding="utf-8") as f:
        content = f.read()
    
    # WP_PASSWORD 교체
    new_content = content.replace(
        f"WP_PASSWORD={WP_PASSWORD}",
        f"WP_PASSWORD={app_password}\nWP_APP_PASSWORD={app_password}"
    )
    with open(".env", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("[OK] .env 파일에 App Password 저장 완료")


if __name__ == "__main__":
    print("="*60)
    print("  WordPress Application Password 자동 생성")
    print("="*60)
    
    if not wp_login():
        print("\n[ERROR] 로그인 실패. 아이디/비밀번호를 확인하세요.")
        sys.exit(1)
    
    nonce = get_nonce()
    if not nonce:
        print("\n[WARN] Nonce 없이 진행 시도...")
    
    app_pw = create_application_password(nonce)
    if app_pw:
        if test_app_password(app_pw):
            save_app_password_to_env(app_pw)
            print("\n[SUCCESS] Application Password 설정 완료!")
            print("  이제 python -X utf8 setup/wp_setup.py 를 다시 실행하세요.")
        else:
            print("\n[WARN] App Password가 생성됐지만 쓰기 테스트 실패")
    else:
        print("\n[ERROR] App Password 생성 실패")
        print("  수동으로 생성하려면:")
        print(f"  1. {WP_URL}/wp-admin/profile.php 접속")
        print("  2. 맨 아래 'Application Passwords' 섹션")
        print("  3. 이름: MN365-AutoBot 입력 후 생성")
        print("  4. 생성된 비밀번호를 .env의 WP_PASSWORD에 입력")
