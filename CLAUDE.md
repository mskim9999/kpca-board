# 운영진 사이트 (kpca-board)

한국췌장암환우협회 작업용 상황판(claude.ai 아티팩트 `Mz9D8cYCQKpJPRNsJeCCEv`)을 옮겨 담은 정적 사이트다.
자세한 구조와 내력은 `HANDOFF.md`.

## 갱신

**사이트는 작업용 상황판을 따라 자동으로 바뀌지 않는다.** 「사이트 갱신해줘」라고 하면:

1. 작업용 상황판 최신본 → `hub/index.html`, db(`hub`·`posted`·`writereq`·`reviews`·`agentdoc`) → `dbdump/`,
   글꼴 자산 4개 → `artifact-files/a9f13a27-6d23-4f7f-9514-de754659eb5b/<id>.ttf` (작업 폴더에서, 저장소 밖)
2. `tools/*` 를 작업 폴더 `ro/` 로 복사 → `python ro/build_ro.py` → `python ro/build_site.py <Apps Script 웹 앱 URL>`
3. `site/index.html` 을 저장소 루트 `index.html` 로 복사 → 커밋 → push. 1~2분 뒤 반영

공유용 아티팩트(`Q1ux…`)는 2026-10-18 지웠다. `build_ro.py` 는 사이트의 재료(`ro/share.html`)를 만들 뿐 따로 게시하지 않는다.

## 사이트에 싣지 않는 것 (운영자 결정 2026-10-18)

이 저장소는 **공개**다. 원본과 커밋 이력을 누구나 볼 수 있다.

- **회원 사례** — 회원 이름(닉네임)과 투병 경과, 보호자 댓글의 내용. 작업용 상황판에는 그대로 두고
  `tools/build_site.py` 의 「0. 회원 사례는 사이트에 싣지 않는다」에서 뺀다. 새 사례가 상황판에 들어오면 거기에 규칙을 더한다.
- 만든 뒤 `별아해`·`폴피리녹스`·`보호자 작성`·`입 헐음`·`14,000` 이 0번인지 센다(스크립트가 남으면 멈춘다).
- 비밀번호·토큰·개인 연락처는 커밋하지 않는다. `robots.txt`·`noindex` 를 유지한다.
- 예전 커밋에는 빼기 전 내용이 남아 있다. 이력 정리(force push)는 카페지기 확인 없이 하지 않는다.
