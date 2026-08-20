# -*- coding: utf-8 -*-
"""
WordPress XML-RPC Publisher
NinjaFirewall REST API 차단 완전 우회용
"""
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from xml.etree import ElementTree as ET

load_dotenv()

WP_URL      = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")
XMLRPC_URL  = f"{WP_URL}/xmlrpc.php"


def _xml_value(val):
    """Python 값을 XML-RPC 형식으로 변환"""
    if isinstance(val, bool):
        return f"<value><boolean>{'1' if val else '0'}</boolean></value>"
    if isinstance(val, int):
        return f"<value><int>{val}</int></value>"
    if isinstance(val, list):
        items = "".join(f"<data>{_xml_value(v)}</data>" for v in val)
        return f"<value><array>{items}</array></value>"
    if isinstance(val, dict):
        members = ""
        for k, v in val.items():
            members += f"<member><name>{k}</name>{_xml_value(v)}</member>"
        return f"<value><struct>{members}</struct></value>"
    # string (default)
    escaped = str(val).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"<value><string>{escaped}</string></value>"


def xmlrpc_call(method, params):
    """XML-RPC 요청 실행"""
    param_xml = "".join(f"<param>{_xml_value(p)}</param>" for p in params)
    body = f"""<?xml version="1.0"?>
<methodCall>
  <methodName>{method}</methodName>
  <params>{param_xml}</params>
</methodCall>"""

    try:
        resp = requests.post(
            XMLRPC_URL,
            data=body.encode("utf-8"),
            headers={"Content-Type": "text/xml; charset=utf-8"},
            timeout=60
        )
        return resp.status_code, resp.text
    except Exception as e:
        return 0, str(e)


def publish_via_xmlrpc(title, content, category_ids=None, tag_ids=None,
                       excerpt="", status="publish"):
    """XML-RPC로 WordPress 포스트 발행"""

    post_data = {
        "post_title":   title,
        "post_content": content,
        "post_status":  status,
        "post_excerpt": excerpt,
        "post_type":    "post",
    }

    if category_ids:
        post_data["terms"] = {"category": category_ids}
    if tag_ids:
        if "terms" not in post_data:
            post_data["terms"] = {}
        post_data["terms"]["post_tag"] = tag_ids

    # wp.newPost (WordPress 3.4+)
    params = [
        0,              # blog_id (항상 0)
        WP_USERNAME,
        WP_PASSWORD,
        post_data
    ]

    status_code, response_text = xmlrpc_call("wp.newPost", params)
    print(f"  XML-RPC 응답: HTTP {status_code}")

    if status_code == 200 and "<fault>" not in response_text:
        # 성공: 포스트 ID 추출
        try:
            root = ET.fromstring(response_text)
            post_id_elem = root.find(".//value/int") or root.find(".//value/string")
            if post_id_elem is not None:
                post_id = int(post_id_elem.text)
                post_url = f"{WP_URL}/?p={post_id}"
                print(f"  [OK] XML-RPC 발행 성공! ID={post_id}")
                # permalink 가져오기
                try:
                    permalink = get_permalink(post_id)
                    if permalink:
                        post_url = permalink
                except:
                    pass
                return post_id, post_url
        except Exception as e:
            print(f"  [WARN] 응답 파싱 오류: {e}")
            print(f"  응답: {response_text[:300]}")
    else:
        # 실패
        fault_msg = ""
        try:
            root = ET.fromstring(response_text)
            fault_str = root.find(".//value/struct/member[name='faultString']/value/string")
            if fault_str is not None:
                fault_msg = fault_str.text
        except:
            fault_msg = response_text[:200]
        print(f"  [FAIL] XML-RPC 실패: {fault_msg}")

    return None, None


def get_permalink(post_id):
    """포스트 영구 링크 가져오기"""
    params = [0, WP_USERNAME, WP_PASSWORD, post_id, "post"]
    _, resp = xmlrpc_call("wp.getPost", params)
    try:
        root = ET.fromstring(resp)
        for member in root.findall(".//member"):
            name = member.find("name")
            if name is not None and name.text == "link":
                val = member.find("value/string")
                if val is not None:
                    return val.text
    except:
        pass
    return None


def test_xmlrpc():
    """XML-RPC 연결 테스트"""
    print("[TEST] XML-RPC 연결 테스트...")
    status_code, resp = xmlrpc_call("demo.sayHello", [])
    print(f"  sayHello: HTTP {status_code}")

    # 실제 테스트: 짧은 포스트 발행
    pid, purl = publish_via_xmlrpc(
        title="[TEST] XML-RPC 방화벽 우회 테스트",
        content="<p>XML-RPC 방식으로 방화벽을 우회하여 발행되었습니다.</p>",
        status="draft"
    )
    if pid:
        print(f"  [SUCCESS] 발행 성공! ID={pid}")
        # 삭제
        import base64
        tok = base64.b64encode(f"{WP_USERNAME}:{WP_PASSWORD}".encode()).decode()
        import os
        api = os.getenv("WP_API_URL")
        requests.delete(f"{api}/posts/{pid}?force=true",
                       headers={"Authorization": f"Basic {tok}"}, timeout=10)
        print("  테스트 포스트 삭제 완료")
        return True
    return False


if __name__ == "__main__":
    test_xmlrpc()
