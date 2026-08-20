# -*- coding: utf-8 -*-
"""
GitHub 자동 설정 스크립트
- 저장소 자동 생성
- 코드 자동 업로드  
- GitHub Actions Secrets 자동 등록
"""
import sys, os, json, subprocess, base64
import requests
from dotenv import load_dotenv
load_dotenv()

# ─── 여기에 GitHub 정보 입력 ───────────────────────────────
GITHUB_TOKEN    = os.getenv("GITHUB_TOKEN", "")   # ghp_로 시작하는 토큰
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")  # GitHub 아이디
REPO_NAME       = "moneynote365-auto"
# ──────────────────────────────────────────────────────────

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT_EXE     = r"C:\Program Files\Git\bin\git.exe"
GH_API      = "https://api.github.com"
HEADERS     = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
}


def run_git(*args, cwd=None):
    result = subprocess.run(
        [GIT_EXE] + list(args),
        cwd=cwd or PROJECT_DIR,
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def create_repo():
    """GitHub Private 저장소 생성"""
    print(f"[1] 저장소 '{REPO_NAME}' 생성 중...")
    r = requests.post(f"{GH_API}/user/repos", json={
        "name": REPO_NAME,
        "private": True,
        "description": "머니노트365 자동 투자 보고서 시스템",
        "auto_init": False,
    }, headers=HEADERS, timeout=15)

    if r.status_code == 201:
        repo_url = r.json()["clone_url"]
        print(f"  [OK] 저장소 생성 완료: {r.json()['html_url']}")
        return repo_url
    elif r.status_code == 422:
        # 이미 존재
        print(f"  [INFO] 저장소 이미 존재 — 기존 저장소 사용")
        r2 = requests.get(f"{GH_API}/repos/{GITHUB_USERNAME}/{REPO_NAME}", headers=HEADERS)
        return r2.json()["clone_url"]
    else:
        print(f"  [FAIL] 저장소 생성 실패: {r.status_code} {r.text[:100]}")
        return None


def setup_git_and_push(repo_url):
    """Git 초기화 및 코드 업로드"""
    print(f"\n[2] 코드 업로드 중...")

    # Git 설정
    run_git("config", "user.email", "moneynote365@auto.bot")
    run_git("config", "user.name", "MN365-Bot")

    # Git 초기화
    if not os.path.exists(os.path.join(PROJECT_DIR, ".git")):
        run_git("init", "-b", "main")
        print("  [OK] Git 초기화 완료")

    # remote 추가 (토큰 포함한 URL로)
    auth_url = repo_url.replace("https://", f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@")
    run_git("remote", "remove", "origin")  # 기존 삭제
    run_git("remote", "add", "origin", auth_url)

    # 파일 추가 및 커밋
    run_git("add", ".")
    code, out, err = run_git("commit", "-m", "feat: 머니노트365 자동 투자 보고서 시스템")
    if code == 0 or "nothing to commit" in out:
        print("  [OK] 커밋 완료")
    else:
        print(f"  커밋: {out} {err}")

    # 업로드
    code, out, err = run_git("push", "-u", "origin", "main", "--force")
    if code == 0:
        print(f"  [OK] 코드 업로드 완료!")
    else:
        # main → master 시도
        code2, out2, err2 = run_git("push", "-u", "origin", "HEAD:main", "--force")
        if code2 == 0:
            print(f"  [OK] 코드 업로드 완료!")
        else:
            print(f"  [FAIL] 업로드 실패: {err} / {err2}")
            return False
    return True


def register_secrets():
    """GitHub Actions Secrets 자동 등록"""
    print(f"\n[3] GitHub Actions Secrets 등록 중...")

    # 저장소 공개키 가져오기 (secrets 암호화용)
    r = requests.get(
        f"{GH_API}/repos/{GITHUB_USERNAME}/{REPO_NAME}/actions/secrets/public-key",
        headers=HEADERS, timeout=10
    )
    if r.status_code != 200:
        print(f"  [WARN] 공개키 조회 실패 ({r.status_code}) - Secrets는 수동 등록 필요")
        return

    key_data = r.json()
    key_id   = key_data["key_id"]
    pub_key  = key_data["key"]

    # PyNaCl 없이 base64로 간단히 처리 (보안 낮지만 private repo라 괜찮음)
    try:
        from nacl import encoding, public

        def encrypt_secret(pub_key_b64, secret_value):
            pub_key_bytes = base64.b64decode(pub_key_b64)
            sealed_box = public.SealedBox(public.PublicKey(pub_key_bytes))
            encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
            return base64.b64encode(encrypted).decode("utf-8")

        nacl_available = True
    except ImportError:
        nacl_available = False

    secrets = {
        "WP_URL":        os.getenv("WP_URL", ""),
        "WP_USERNAME":   os.getenv("WP_USERNAME", ""),
        "WP_PASSWORD":   os.getenv("WP_PASSWORD", ""),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
    }

    if nacl_available:
        for name, value in secrets.items():
            if not value:
                continue
            encrypted = encrypt_secret(pub_key, value)
            r2 = requests.put(
                f"{GH_API}/repos/{GITHUB_USERNAME}/{REPO_NAME}/actions/secrets/{name}",
                json={"encrypted_value": encrypted, "key_id": key_id},
                headers=HEADERS, timeout=10
            )
            status = "[OK]" if r2.status_code in (201, 204) else f"[FAIL {r2.status_code}]"
            print(f"  {status} Secret: {name}")
    else:
        # PyNaCl 미설치 - 수동 등록 URL 안내
        print("  [INFO] 자동 Secrets 등록을 위해 PyNaCl 설치 필요")
        print(f"  아래 URL에서 수동 등록:")
        print(f"  https://github.com/{GITHUB_USERNAME}/{REPO_NAME}/settings/secrets/actions")
        for name, val in secrets.items():
            print(f"    {name}: {val[:10]}...")


if __name__ == "__main__":
    print("="*55)
    print("  머니노트365 → GitHub 자동 업로드")
    print("="*55)

    if not GITHUB_TOKEN or not GITHUB_USERNAME:
        print("\n[오류] .env 파일에 GITHUB_TOKEN과 GITHUB_USERNAME을 추가하세요!")
        print("  GITHUB_TOKEN=ghp_xxxxxxxxxxxx")
        print("  GITHUB_USERNAME=내GitHub아이디")
        sys.exit(1)

    # 연결 확인
    r = requests.get(f"{GH_API}/user", headers=HEADERS, timeout=10)
    if r.status_code != 200:
        print(f"\n[오류] GitHub 토큰이 유효하지 않습니다. ({r.status_code})")
        sys.exit(1)
    print(f"\n[OK] GitHub 계정 확인: {r.json()['login']}")

    # 실행
    repo_url = create_repo()
    if repo_url:
        ok = setup_git_and_push(repo_url)
        if ok:
            register_secrets()
            print(f"\n{'='*55}")
            print(f"  완료! 아래 URL에서 확인하세요:")
            print(f"  https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
            print(f"  https://github.com/{GITHUB_USERNAME}/{REPO_NAME}/actions")
            print(f"{'='*55}")
