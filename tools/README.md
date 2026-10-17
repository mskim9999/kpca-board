# 사이트 갱신 도구

작업용 상황판(claude.ai 아티팩트 Mz9D8cYCQKpJPRNsJeCCEv)에서 사이트를 다시 만드는 순서.

1. 작업용 상황판 페이지를 `hub/index.html` 로, 저장소 내용을 `dbdump/<컬렉션>/<문서>.json` 으로 내려받는다
   (컬렉션: hub, posted, writereq, reviews, agentdoc). 글꼴 파일 4개는 `artifact-files/…/` 에 둔다.
2. `python3 tools/build_ro.py` → `ro/share.html` (읽기 전용 사본, 글꼴 내장)
3. `python3 tools/build_site.py <Apps Script 웹 앱 URL>` → `site/index.html`
4. `site/index.html` 을 저장소 루트 `index.html` 로 복사해 커밋·푸시.

요청 받기: `요청받기_AppsScript.gs` (카페지기 구글 시트에 설치, 텔레그램 토큰은 스크립트 속성에만 둔다).
