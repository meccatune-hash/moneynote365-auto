# -*- coding: utf-8 -*-
"""
WordPress FSE 메인 홈(home & index) 템플릿 개편 스크립트
1. 상단 카테고리 퀵 내비게이션 바 (정치, 연예, 스포츠, 모닝뉴스, 주식 등 직관적 버튼)
2. 실시간 최신 핫이슈 종합 (3열 카드 그리드)
3. 🏛️ 정치 핫이슈 섹션 (3열 카드 그리드 + 더보기)
4. 🎬 연예·엔터테인먼트 섹션 (3열 카드 그리드 + 더보기)
5. ⚽ 스포츠 뉴스 섹션 (3열 카드 그리드 + 더보기)
6. 📈 금융·투자 & 일일 보고서 섹션 (3열 카드 그리드 + 더보기)
7. 본문 전체 출력 제거 (wp:post-content -> 요약문 wp:post-excerpt로 변경하여 한줄로 늘어지는 문제 해결)
8. WP Super Cache 자동 캐시 플러시
"""
import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

WP_API_URL = os.getenv("WP_API_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")

tok = base64.b64encode(f"{WP_USERNAME}:{WP_PASSWORD}".encode()).decode()
hdrs = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}

HOME_TEMPLATE_CONTENT = """<!-- wp:template-part {"slug":"header","theme":"twentytwentyfive"} /-->

<!-- wp:group {"tagName":"main","style":{"spacing":{"margin":{"top":"0","bottom":"var:preset|spacing|60"},"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|50"}}},"layout":{"type":"constrained"}} -->
<main class="wp-block-group" style="margin-top:0;margin-bottom:var(--wp--preset--spacing--60);padding-top:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--50)">

	<!-- 상단 카테고리 퀵 내비게이션 바 -->
	<!-- wp:html -->
	<div style="display:flex; flex-wrap:wrap; gap:10px; margin:1rem 0 2.5rem; padding:1.25rem; background:#ffffff; border-radius:12px; border:1px solid #e2e8f0; box-shadow:0 4px 14px rgba(10,22,40,0.05); justify-content:center;">
		<a href="https://kingbrightsucces.com/" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; border-radius:20px; background:#0A1628; color:#ffffff; font-weight:700; font-size:0.9rem; text-decoration:none;">🏠 전체 홈</a>
		<a href="https://kingbrightsucces.com/category/politics/" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; border-radius:20px; background:#f1f5f9; color:#1e293b; font-weight:600; font-size:0.9rem; text-decoration:none;">🏛️ 정치 이슈</a>
		<a href="https://kingbrightsucces.com/category/entertainment/" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; border-radius:20px; background:#f1f5f9; color:#1e293b; font-weight:600; font-size:0.9rem; text-decoration:none;">🎬 연예·엔터</a>
		<a href="https://kingbrightsucces.com/category/sports/" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; border-radius:20px; background:#f1f5f9; color:#1e293b; font-weight:600; font-size:0.9rem; text-decoration:none;">⚽ 스포츠 뉴스</a>
		<a href="https://kingbrightsucces.com/category/morning-news/" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; border-radius:20px; background:#f1f5f9; color:#1e293b; font-weight:600; font-size:0.9rem; text-decoration:none;">🌅 글로벌 모닝뉴스</a>
		<a href="https://kingbrightsucces.com/category/daily-report/" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; border-radius:20px; background:#f1f5f9; color:#1e293b; font-weight:600; font-size:0.9rem; text-decoration:none;">📋 일일 투자보고서</a>
		<a href="https://kingbrightsucces.com/category/kr-stock/" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; border-radius:20px; background:#f1f5f9; color:#1e293b; font-weight:600; font-size:0.9rem; text-decoration:none;">🇰🇷 국내 주식</a>
		<a href="https://kingbrightsucces.com/category/us-stock/" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; border-radius:20px; background:#f1f5f9; color:#1e293b; font-weight:600; font-size:0.9rem; text-decoration:none;">🇺🇸 미국 주식</a>
		<a href="https://kingbrightsucces.com/category/crypto/" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; border-radius:20px; background:#f1f5f9; color:#1e293b; font-weight:600; font-size:0.9rem; text-decoration:none;">🪙 암호화폐</a>
	</div>
	<!-- /wp:html -->

	<!-- 섹션 1: 실시간 최신 핫이슈 종합 (6개 카드 3열 그리드) -->
	<!-- wp:group {"align":"wide","style":{"spacing":{"margin":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|20"}}},"layout":{"type":"flex","justifyContent":"space-between","flexWrap":"nowrap"}} -->
	<div class="wp-block-group alignwide" style="margin-top:var(--wp--preset--spacing--30);margin-bottom:var(--wp--preset--spacing--20)">
		<!-- wp:heading {"level":2,"style":{"typography":{"fontStyle":"normal","fontWeight":"800"}}} -->
		<h2 class="wp-block-heading" style="font-style:normal;font-weight:800">🔥 실시간 종합 최신 핫이슈</h2>
		<!-- /wp:heading -->
	</div>
	<!-- /wp:group -->

	<!-- wp:query {"query":{"perPage":6,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false,"taxQuery":null,"parents":[]},"align":"wide","layout":{"type":"default"}} -->
	<div class="wp-block-query alignwide">
		<!-- wp:post-template {"layout":{"type":"grid","columnCount":3}} -->
			<!-- wp:group {"style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30","left":"var:preset|spacing|30","right":"var:preset|spacing|30"}},"border":{"radius":"12px","width":"1px","style":"solid","color":"#e2e8f0"}},"backgroundColor":"base","layout":{"type":"constrained"}} -->
			<div class="wp-block-group has-base-background-color has-background has-border-color" style="border-color:#e2e8f0;border-width:1px;border-style:solid;border-radius:12px;padding-top:var(--wp--preset--spacing--30);padding-right:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30);padding-left:var(--wp--preset--spacing--30);box-shadow:0 2px 10px rgba(0,0,0,0.04)">
				<!-- wp:post-terms {"term":"category","style":{"typography":{"fontSize":"0.78rem","fontWeight":"700"}}} /-->
				<!-- wp:post-title {"isLink":true,"style":{"typography":{"fontSize":"1.1rem","lineHeight":"1.45"}}} /-->
				<!-- wp:post-excerpt {"showMoreOnNewLine":false,"excerptLength":20,"style":{"typography":{"fontSize":"0.88rem"}},"textColor":"contrast-3"} /-->
				<!-- wp:post-date {"isLink":true,"style":{"typography":{"fontSize":"0.8rem"}},"textColor":"contrast-3"} /-->
			</div>
			<!-- /wp:group -->
		<!-- /wp:post-template -->
	</div>
	<!-- /wp:query -->

	<!-- 섹션 2: 🏛️ 정치 핫이슈 -->
	<!-- wp:group {"align":"wide","style":{"spacing":{"margin":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|20"}}},"layout":{"type":"flex","justifyContent":"space-between","flexWrap":"nowrap"}} -->
	<div class="wp-block-group alignwide" style="margin-top:var(--wp--preset--spacing--60);margin-bottom:var(--wp--preset--spacing--20);border-top:2px solid #0A1628;padding-top:1.5rem">
		<!-- wp:heading {"level":2,"style":{"typography":{"fontStyle":"normal","fontWeight":"800"}}} -->
		<h2 class="wp-block-heading" style="font-style:normal;font-weight:800">🏛️ 정치 핫이슈</h2>
		<!-- /wp:heading -->
		<!-- wp:paragraph -->
		<p><a href="https://kingbrightsucces.com/category/politics/" style="font-weight:700;color:#2563eb;text-decoration:none">정치 뉴스 더보기 →</a></p>
		<!-- /wp:paragraph -->
	</div>
	<!-- /wp:group -->

	<!-- wp:query {"query":{"perPage":3,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","inherit":false,"taxQuery":{"category":[184]}},"align":"wide","layout":{"type":"default"}} -->
	<div class="wp-block-query alignwide">
		<!-- wp:post-template {"layout":{"type":"grid","columnCount":3}} -->
			<!-- wp:group {"style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30","left":"var:preset|spacing|30","right":"var:preset|spacing|30"}},"border":{"radius":"12px","width":"1px","style":"solid","color":"#e2e8f0"}},"backgroundColor":"base","layout":{"type":"constrained"}} -->
			<div class="wp-block-group has-base-background-color has-background has-border-color" style="border-color:#e2e8f0;border-width:1px;border-style:solid;border-radius:12px;padding-top:var(--wp--preset--spacing--30);padding-right:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30);padding-left:var(--wp--preset--spacing--30);box-shadow:0 2px 10px rgba(0,0,0,0.04)">
				<!-- wp:post-terms {"term":"category","style":{"typography":{"fontSize":"0.78rem","fontWeight":"700"}}} /-->
				<!-- wp:post-title {"isLink":true,"style":{"typography":{"fontSize":"1.1rem","lineHeight":"1.45"}}} /-->
				<!-- wp:post-excerpt {"showMoreOnNewLine":false,"excerptLength":20,"style":{"typography":{"fontSize":"0.88rem"}},"textColor":"contrast-3"} /-->
				<!-- wp:post-date {"isLink":true,"style":{"typography":{"fontSize":"0.8rem"}},"textColor":"contrast-3"} /-->
			</div>
			<!-- /wp:group -->
		<!-- /wp:post-template -->
	</div>
	<!-- /wp:query -->

	<!-- 섹션 3: 🎬 연예·엔터테인먼트 -->
	<!-- wp:group {"align":"wide","style":{"spacing":{"margin":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|20"}}},"layout":{"type":"flex","justifyContent":"space-between","flexWrap":"nowrap"}} -->
	<div class="wp-block-group alignwide" style="margin-top:var(--wp--preset--spacing--60);margin-bottom:var(--wp--preset--spacing--20);border-top:2px solid #0A1628;padding-top:1.5rem">
		<!-- wp:heading {"level":2,"style":{"typography":{"fontStyle":"normal","fontWeight":"800"}}} -->
		<h2 class="wp-block-heading" style="font-style:normal;font-weight:800">🎬 연예·엔터테인먼트</h2>
		<!-- /wp:heading -->
		<!-- wp:paragraph -->
		<p><a href="https://kingbrightsucces.com/category/entertainment/" style="font-weight:700;color:#2563eb;text-decoration:none">연예 뉴스 더보기 →</a></p>
		<!-- /wp:paragraph -->
	</div>
	<!-- /wp:group -->

	<!-- wp:query {"query":{"perPage":3,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","inherit":false,"taxQuery":{"category":[163]}},"align":"wide","layout":{"type":"default"}} -->
	<div class="wp-block-query alignwide">
		<!-- wp:post-template {"layout":{"type":"grid","columnCount":3}} -->
			<!-- wp:group {"style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30","left":"var:preset|spacing|30","right":"var:preset|spacing|30"}},"border":{"radius":"12px","width":"1px","style":"solid","color":"#e2e8f0"}},"backgroundColor":"base","layout":{"type":"constrained"}} -->
			<div class="wp-block-group has-base-background-color has-background has-border-color" style="border-color:#e2e8f0;border-width:1px;border-style:solid;border-radius:12px;padding-top:var(--wp--preset--spacing--30);padding-right:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30);padding-left:var(--wp--preset--spacing--30);box-shadow:0 2px 10px rgba(0,0,0,0.04)">
				<!-- wp:post-terms {"term":"category","style":{"typography":{"fontSize":"0.78rem","fontWeight":"700"}}} /-->
				<!-- wp:post-title {"isLink":true,"style":{"typography":{"fontSize":"1.1rem","lineHeight":"1.45"}}} /-->
				<!-- wp:post-excerpt {"showMoreOnNewLine":false,"excerptLength":20,"style":{"typography":{"fontSize":"0.88rem"}},"textColor":"contrast-3"} /-->
				<!-- wp:post-date {"isLink":true,"style":{"typography":{"fontSize":"0.8rem"}},"textColor":"contrast-3"} /-->
			</div>
			<!-- /wp:group -->
		<!-- /wp:post-template -->
	</div>
	<!-- /wp:query -->

	<!-- 섹션 4: ⚽ 스포츠 뉴스 -->
	<!-- wp:group {"align":"wide","style":{"spacing":{"margin":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|20"}}},"layout":{"type":"flex","justifyContent":"space-between","flexWrap":"nowrap"}} -->
	<div class="wp-block-group alignwide" style="margin-top:var(--wp--preset--spacing--60);margin-bottom:var(--wp--preset--spacing--20);border-top:2px solid #0A1628;padding-top:1.5rem">
		<!-- wp:heading {"level":2,"style":{"typography":{"fontStyle":"normal","fontWeight":"800"}}} -->
		<h2 class="wp-block-heading" style="font-style:normal;font-weight:800">⚽ 스포츠 뉴스</h2>
		<!-- /wp:heading -->
		<!-- wp:paragraph -->
		<p><a href="https://kingbrightsucces.com/category/sports/" style="font-weight:700;color:#2563eb;text-decoration:none">스포츠 뉴스 더보기 →</a></p>
		<!-- /wp:paragraph -->
	</div>
	<!-- /wp:group -->

	<!-- wp:query {"query":{"perPage":3,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","inherit":false,"taxQuery":{"category":[164]}},"align":"wide","layout":{"type":"default"}} -->
	<div class="wp-block-query alignwide">
		<!-- wp:post-template {"layout":{"type":"grid","columnCount":3}} -->
			<!-- wp:group {"style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30","left":"var:preset|spacing|30","right":"var:preset|spacing|30"}},"border":{"radius":"12px","width":"1px","style":"solid","color":"#e2e8f0"}},"backgroundColor":"base","layout":{"type":"constrained"}} -->
			<div class="wp-block-group has-base-background-color has-background has-border-color" style="border-color:#e2e8f0;border-width:1px;border-style:solid;border-radius:12px;padding-top:var(--wp--preset--spacing--30);padding-right:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30);padding-left:var(--wp--preset--spacing--30);box-shadow:0 2px 10px rgba(0,0,0,0.04)">
				<!-- wp:post-terms {"term":"category","style":{"typography":{"fontSize":"0.78rem","fontWeight":"700"}}} /-->
				<!-- wp:post-title {"isLink":true,"style":{"typography":{"fontSize":"1.1rem","lineHeight":"1.45"}}} /-->
				<!-- wp:post-excerpt {"showMoreOnNewLine":false,"excerptLength":20,"style":{"typography":{"fontSize":"0.88rem"}},"textColor":"contrast-3"} /-->
				<!-- wp:post-date {"isLink":true,"style":{"typography":{"fontSize":"0.8rem"}},"textColor":"contrast-3"} /-->
			</div>
			<!-- /wp:group -->
		<!-- /wp:post-template -->
	</div>
	<!-- /wp:query -->

	<!-- 섹션 5: 📈 금융 시장 & 일일 투자 보고서 -->
	<!-- wp:group {"align":"wide","style":{"spacing":{"margin":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|20"}}},"layout":{"type":"flex","justifyContent":"space-between","flexWrap":"nowrap"}} -->
	<div class="wp-block-group alignwide" style="margin-top:var(--wp--preset--spacing--60);margin-bottom:var(--wp--preset--spacing--20);border-top:2px solid #0A1628;padding-top:1.5rem">
		<!-- wp:heading {"level":2,"style":{"typography":{"fontStyle":"normal","fontWeight":"800"}}} -->
		<h2 class="wp-block-heading" style="font-style:normal;font-weight:800">📈 금융 시장 & 일일 투자 보고서</h2>
		<!-- /wp:heading -->
		<!-- wp:paragraph -->
		<p><a href="https://kingbrightsucces.com/category/daily-report/" style="font-weight:700;color:#2563eb;text-decoration:none">투자 보고서 더보기 →</a></p>
		<!-- /wp:paragraph -->
	</div>
	<!-- /wp:group -->

	<!-- wp:query {"query":{"perPage":3,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","inherit":false,"taxQuery":{"category":[22,100]}},"align":"wide","layout":{"type":"default"}} -->
	<div class="wp-block-query alignwide">
		<!-- wp:post-template {"layout":{"type":"grid","columnCount":3}} -->
			<!-- wp:group {"style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30","left":"var:preset|spacing|30","right":"var:preset|spacing|30"}},"border":{"radius":"12px","width":"1px","style":"solid","color":"#e2e8f0"}},"backgroundColor":"base","layout":{"type":"constrained"}} -->
			<div class="wp-block-group has-base-background-color has-background has-border-color" style="border-color:#e2e8f0;border-width:1px;border-style:solid;border-radius:12px;padding-top:var(--wp--preset--spacing--30);padding-right:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30);padding-left:var(--wp--preset--spacing--30);box-shadow:0 2px 10px rgba(0,0,0,0.04)">
				<!-- wp:post-terms {"term":"category","style":{"typography":{"fontSize":"0.78rem","fontWeight":"700"}}} /-->
				<!-- wp:post-title {"isLink":true,"style":{"typography":{"fontSize":"1.1rem","lineHeight":"1.45"}}} /-->
				<!-- wp:post-excerpt {"showMoreOnNewLine":false,"excerptLength":20,"style":{"typography":{"fontSize":"0.88rem"}},"textColor":"contrast-3"} /-->
				<!-- wp:post-date {"isLink":true,"style":{"typography":{"fontSize":"0.8rem"}},"textColor":"contrast-3"} /-->
			</div>
			<!-- /wp:group -->
		<!-- /wp:post-template -->
	</div>
	<!-- /wp:query -->

</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer","theme":"twentytwentyfive"} /-->"""

print("1. Updating twentytwentyfive//home template...")
r_home = requests.post(f"{WP_API_URL}/templates/twentytwentyfive//home", json={"content": HOME_TEMPLATE_CONTENT}, headers=hdrs)
print("Home template update status:", r_home.status_code)

print("2. Updating twentytwentyfive//index template...")
r_index = requests.post(f"{WP_API_URL}/templates/twentytwentyfive//index", json={"content": HOME_TEMPLATE_CONTENT}, headers=hdrs)
print("Index template update status:", r_index.status_code)

print("3. Flushing WP Super Cache...")
requests.post(f"{WP_API_URL}/plugins/wp-super-cache/wp-cache", json={"status": "inactive"}, headers=hdrs)
r_flush = requests.post(f"{WP_API_URL}/plugins/wp-super-cache/wp-cache", json={"status": "active"}, headers=hdrs)
print("Cache reactivated status:", r_flush.status_code)
