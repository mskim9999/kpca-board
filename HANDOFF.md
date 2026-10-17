# 인수인계 — 한국췌장암환우협회 제4기 상황판

최종 정리: 2026-10-18 (claude.ai 클라우드 세션에서 작성)
이 문서를 읽은 Claude 는 아래 내용을 전제로 이어서 작업한다.

---

## 1. 무엇이 어디에 있나

| 이름 | 위치 | 누가 보나 | 성격 |
|---|---|---|---|
| **작업용 상황판** (원본) | claude.ai 아티팩트 `https://claude.ai/artifact/Mz9D8cYCQKpJPRNsJeCCEv` (제목 「협회 운영 상황판」) | 카페지기 본인 | 저장소(db)·본문 작성(sample)·댓글·자산이 붙은 실제 작업 화면. 모든 수정은 여기서 시작 |
| **공유용 상황판** | claude.ai 아티팩트 `https://claude.ai/artifact/Q1uxw8Lj9xoZFHypVDCFAD` (제목 「제4기 상황판 공유용」) | 링크가 있는 누구나 | 작업용을 옮겨 담은 읽기 전용 사본. 저장 기능 없음 |
| **운영진 사이트** | `https://mskim9999.github.io/kpca-board/` ← 저장소 `mskim9999/kpca-board` (main 브랜치 루트, GitHub Pages) | 주소를 아는 운영진 | 공유용과 같은 내용 + 「게시글 작성 요청」이 실제로 전송됨. 검색엔진 차단 |
| **요청 받는 곳** | 카페지기 구글 시트 「게시글 작성 요청」의 「요청」 탭 + Apps Script 웹 앱 | 카페지기 | 사이트 요청이 한 줄씩 쌓이고 텔레그램 봇으로 알림 |
| 예전 「제4기 상황판」 | `https://claude.ai/artifact/Lv6xQUfajAZyaHp1jMD7jE` | — | 처음에 따로 만든 시안. 더 이상 쓰지 않음(카페지기 확인 후 삭제 가능) |
| 「협회 운영 원칙」 캔버스 | `https://claude.ai/artifact/VAZSgMUS3Jnd196rDNXUNh` | — | 초기 시안. 쓰지 않음 |

Apps Script 웹 앱 URL (사이트가 요청을 보내는 곳, 공개돼도 됨):
`https://script.google.com/macros/s/AKfycbx26m1loOFnt8zipsRMuMKImRem53WLfRiq3xUZIFUOUfCM64V79EqT52NrxNemxtYxfQ/exec`

> 텔레그램 봇 토큰은 시트의 Apps Script 「스크립트 속성」(`TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`)에만 있다.
> 어떤 파일에도 적지 않고, 카페지기에게 묻지도 않는다.

---

## 2. 작업용 상황판의 구조

탭: 전체 상황판 · 게시글 작성 · 강의안 작성 · 댓글 관리 · 에이전트 관리
(처음 열면 항상 「전체 상황판」. 마지막 탭을 기억하던 기능은 없앴다)

선언된 기능(capabilities): `comments`, `db`, `sample`, `assets` — 다시 게시할 때 `capabilities` 를 넘기지 않으면 그대로 유지된다. 런타임 계약 버전도 건드리지 않는다.

### db 컬렉션 (ArtifactData 로 읽고 쓴다)
| 컬렉션 | 내용 |
|---|---|
| `hub/main` | 제4기 현황 값. `members`, `membersNote`, `collect`, `collectNote`, `meet`, `meetNote`, `post.{status,next}`, `lec.{status,now,note,next}`, `com.{…}`, `yt.{…}`, `book.{…}` |
| `posted` | 게시 완료로 등록한 글 (게시본·게시일) |
| `writereq` | 본문 작성 요청과 결과 |
| `reviews` | 검토 대기 항목의 판단(승인·보류·거부) |
| `agentdoc` (+`/versions`) | 에이전트 지침 문서 |
| `agentchat/<id>/messages` | 에이전트와의 대화 (공유용·사이트에는 싣지 않음) |

게시글 원고 목록은 페이지 안 `<script type="application/json" id="postData">` (111건: 후보·초안·게시), 본문은 `<script class="doc" data-key="…">` 블록들.

### 전체 상황판 탭 (위에서부터)
1. **제4기 현황** — 카드 4개: 카페 회원 · 게시글 관리(후보·작성·게시 실시간 집계, 누르면 게시글 탭) · 원고 자료 수집 · 다음 길라잡이 모임
2. **제4기 4대 과제** — 순서: 게시글 관리 → 강의안 마련 → 커뮤니티 확대 → 유튜브 채널. 제목 클릭 시 해당 탭 이동(게시글·강의안만, 나머지 둘은 연결할 페이지 없음). 책 발간은 과제에서 뺐고 값은 `hub/main.book` 에 남아 있음
3. 운영 지표 숫자 띠, 지금 하실 일
4. **감춘 영역**(지우지 않고 `hidden`): 검토 대기, 자료의 근거 수준, 에이전트 활동, 모임 재개까지. 전체 상황판 탭 옆 숫자 배지도 감춤

### 탭 옆 배지
- 게시글 작성: `게시 n` (상태가 「게시」인 전체 건수)
- 강의안 작성: 완성 강의안 편수(`#b-lec [data-doc^="lec-4"]` 개수, 현재 6편)

---

## 3. 디자인 결정 (바꾸지 말 것, 바꾸라는 요청이 있을 때만)

- 색: 보라 한 가지 톤, 밝은 화면 하나(다크 모드 없음)
  `--paper #EFEEF4 · --raise #FFF · --ink #221D35 · --leaf #5B3FA0 · --leaf-deep #4A3290 · --leaf-soft #ECE7F6 · --head-bg #221D35`
- 글꼴: 제목류 **Paperlogy**(SB/XB), 본문 **KoPub 돋움**(M/B), 숫자 IBM Plex Mono
  - 작업용: 아티팩트 자산 `/_blob/1819867758c1c0bb229015dae45c09a5`(Paperlogy SB) `/_blob/5b355df6466963721c1d2a3680383609`(XB) `/_blob/4ee508aee0d962fa5cdc7ff87e1e4a43`(KoPub M) `/_blob/a053d9b249a97d996219235c2dc64d2f`(KoPub B)
  - 공유용·사이트: 쓰인 글자만 남겨 woff2 로 페이지에 내장
- 머리 띠: 어두운 띠, 타이틀 「한국췌장암환우협회 제4기 상황판」 KoPub 27px 굵기 400, 옆에 「카페지기, 운영진 공유용」 16px, 오른쪽 기준일. 부제 문구는 지웠음
- 탭 글자: Paperlogy 19px(모바일 16px)
- 게시글 표: 머리줄 가운데 정렬, 기본 기간 「전체 연도」
- 게시글 상태 칩: 게시 완료 `#2563EB`/흰 글씨 · 작성 완료 `#8ECDF5` · 작성 후보 `#E2F2FD` (파랑→연하늘 그라데이션)
- 「← 목록으로」(`#pBack`): 붉은색 `#D0312D`, 15px, 굵게
- 숫자 띠(`.strip`): 숫자·설명 모두 가운데 정렬, 설명 12.5px
- 모바일: 단어 단위 줄바꿈(`word-break: keep-all`), 현황 카드 2×2, 4대 과제 1열

### 게시글 작성 탭 순서 (공유용·사이트)
작성한 글과 후보(숫자 띠 포함) → **게시글 작성 요청** → 담당 · 카페글작성 에이전트 → 작성 경로 → 안내

### 문구 규칙
- 미게시 글의 맺음은 「한국췌장암환우협회 카페지기 및 운영진 일동」 (2026-10-18 post-diet 한 편을 고침)
- 단어를 나열할 때 가운뎃점 대신 쉼표 (망고샛별 카페글 규칙)

---

## 4. 공유용·사이트 갱신하는 법

카페지기가 「공유용 갱신해줘」「사이트 갱신해줘」라고 하면:

1. 작업용 상황판 최신본을 받는다: `Artifact read url=…Mz9D8cYCQKpJPRNsJeCCEv path=index.html` → `hub/index.html`
2. db 를 받는다: `ArtifactData list` 로 `hub`, `posted`, `writereq`, `reviews`, `agentdoc` 를 `out_dir=dbdump` 로
3. 글꼴 4개를 받는다: `Artifact read path=<위 자산 id>` → `artifact-files/a9f13a27-6d23-4f7f-9514-de754659eb5b/<id>.ttf`
   (스크립트가 기대하는 폴더 배치: 작업 폴더 아래 `hub/`, `dbdump/`, `artifact-files/…/`, `ro/`(도구들), `site/`)
4. `pip install fonttools brotli` 후 `python3 ro/build_ro.py` → `ro/share.html`
   - 공유용 아티팩트에 게시: `Artifact publish file_path=ro/share.html url=https://claude.ai/artifact/Q1uxw8Lj9xoZFHypVDCFAD` (capabilities 없음)
5. `python3 ro/build_site.py <Apps Script 웹 앱 URL>` → `site/index.html`
6. `site/index.html` 을 이 저장소 루트 `index.html` 로 복사 → 커밋 → `git push origin main`
   - 커밋 작성자: `Claude <noreply@anthropic.com>`
   - 1~2분 뒤 사이트 반영. 안 보이면 Ctrl+Shift+R

도구 원본은 이 저장소 `tools/` 에 있다 (`build_ro.py`, `build_site.py`, `request_part.*`, `request_site.js`, `요청받기_AppsScript.gs`). 작업할 때는 `ro/` 로 복사해서 쓴다.

### 작업용 상황판을 고칠 때
- 반드시 최신본을 먼저 읽고(`Artifact read`) 그 위에서 고친다. 다른 세션이 고쳤을 수 있다.
- 고친 뒤 같은 url 로 게시(`capabilities`·`contract` 는 넘기지 않음) → 이어서 공유용·사이트도 갱신.
- 터미널과 클라우드 두 곳에서 **동시에** 고치지 않는다. 나중 게시가 앞의 것을 덮는다.

---

## 5. 운영진 요청 처리

- 사이트 「요청 보내기」 → Apps Script `doPost` → 시트 「요청」 탭에 `받은 시각 · 요청하는 분 · 글 주제 · 갈래 · 게시판 · 담을 내용 · 참고 자료 · 처리(새 요청)` 한 줄 + 텔레그램 알림
- 같은 제목·내용이 10분 안에 다시 오면 한 번만 받는다. 숨은 칸(`website`)이 채워진 요청은 버린다.
- 카페지기가 「요청 들어온 것 확인해줘」라고 하면: 구글 드라이브 커넥터로 시트를 읽고 → 「새 요청」 줄을 작업용 상황판의 글감 후보로 옮기는 안을 보여 준 뒤 → 승인받고 반영 → 시트의 「처리」 칸을 바꿔 달라고 안내(또는 커넥터로 직접).
- 텔레그램이 안 오면: Apps Script 「실행」 기록 확인, `connectTelegram` 재실행.

---

## 6. 지켜야 할 것

- 협회 철학과 의료 안전 원칙(프로젝트 지침)을 따른다. 처방약·항암 임의 중단을 권하지 않는다.
- `browser_profile`, `state.json` 은 로그인 정보 — 공유·업로드 금지.
- 다음카페 수집 `output` 폴더에는 환우 건강정보가 섞여 있다 — 개인 PC 에만 보관, 사이트·공유용에 원문을 싣지 않는다.
- 책에 실을 글은 작성자 동의를 받은 분부터. 돌아가신 분은 유족 확인.
- 다음카페 수집 시 요청 간격(`delay_sec`) 1초 이상.
- 사이트는 공개 저장소다. 비밀번호·토큰·개인 연락처를 커밋하지 않는다. 검색엔진 차단(`robots.txt`, `noindex`)을 유지한다.
- 댓글 관리 탭에는 카페 보호자 사례 요약(폴피리녹스 1차 후 식사 문제)이 들어 있다. 공개 범위가 넓어지면 카페지기에게 확인.

---

## 7. 남은 일 / 열린 선택

- 4대 과제의 「커뮤니티 확대」「유튜브 채널」 제목 링크 대상 미정 (카페 주소·유튜브 주소·새 탭 중 결정 대기)
- 유튜브 채널 과제 값 비어 있음 (카페지기가 입력)
- 예전 「제4기 상황판」(Lv6x…)·「협회 운영 원칙」(VAZS…) 아티팩트 삭제 여부 — 카페지기 확인 후에만
- 다이어트 주사제 초안 첫머리 인사(「카페지기 망고샛별입니다」)는 그대로 둠 — 바꿀지 미정
