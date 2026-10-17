/**
 * 한국췌장암환우협회 제4기 상황판 — 게시글 작성 요청 받기
 *
 * 하는 일
 *  - 상황판 사이트의 「요청 보내기」가 보낸 내용을 이 시트의 「요청」 탭에 한 줄씩 적는다.
 *  - 요청이 들어올 때마다 카페지기 전용 텔레그램 봇으로 알린다.
 *
 * ── 설치 (한 번만) ─────────────────────────────────────────────
 *  A. 텔레그램 봇 만들기
 *     1) 텔레그램에서 @BotFather 를 찾아 /newbot 을 보내고, 이름과 아이디(…_bot 으로 끝남)를 정한다.
 *     2) BotFather 가 주는 토큰(123456789:ABC… 모양)을 복사해 둔다. ※ 토큰은 남에게 보이지 말 것.
 *     3) 방금 만든 봇을 열고 「시작」(/start)을 누른 뒤 아무 말이나 한 번 보낸다.
 *
 *  B. 시트와 스크립트
 *     1) 구글 시트를 새로 만들고 이름을 「게시글 작성 요청」으로 둔다.
 *     2) 메뉴 확장 프로그램 → Apps Script 를 열고, 있던 내용을 지운 뒤 이 파일 전체를 붙여 넣고 저장한다.
 *     3) 왼쪽 톱니바퀴(프로젝트 설정) → 맨 아래 「스크립트 속성」 → 속성 추가
 *          이름 TELEGRAM_TOKEN   값 (A-2 에서 받은 토큰)
 *        저장한다.
 *     4) 위쪽 함수 고르는 칸에서 「connectTelegram」을 고르고 ▶실행. 권한 허용 창이 뜨면 본인 계정으로 허용
 *        (「확인되지 않은 앱」 경고는 고급 → 이동. 본인이 만든 스크립트라 그렇다).
 *        텔레그램으로 「연결되었습니다」 메시지가 오면 성공.
 *     5) 오른쪽 위 「배포 → 새 배포」 → 톱니바퀴에서 「웹 앱」
 *          다음 사용자 인증 정보로 실행: 나 / 액세스 권한이 있는 사용자: 모든 사용자
 *        「배포」 후 나오는 웹 앱 URL(https://script.google.com/macros/s/…/exec)을 Claude 에게 보낸다.
 *        (이 URL 은 알려도 된다. 토큰은 알리지 않는다.)
 */

var SHEET_NAME = "요청";
var HEAD = ["받은 시각", "요청하는 분", "글 주제", "분야", "게시판", "담을 내용", "참고 자료", "처리"];
var MAX = { who: 60, title: 200, kind: 40, board: 60, body: 4000, ref: 500 };
var PROPS = PropertiesService.getScriptProperties();

/* 사이트에서 요청이 들어오는 곳 */
function doPost(e) {
  var p = (e && e.parameter) || {};
  if (p.website) return reply_("ok");          // 사람이 아닌 프로그램이 채우는 숨은 칸
  var v = {};
  Object.keys(MAX).forEach(function (k) { v[k] = String(p[k] || "").trim().slice(0, MAX[k]); });
  if (!v.title || !v.body) return reply_("missing");

  // 같은 내용이 짧은 시간에 여러 번 오면 한 번만 받는다
  var cache = CacheService.getScriptCache();
  var key = "r" + Utilities.base64EncodeWebSafe(Utilities.computeDigest(
    Utilities.DigestAlgorithm.MD5, v.title + "|" + v.body, Utilities.Charset.UTF_8));
  if (cache.get(key)) return reply_("dup");
  cache.put(key, "1", 600);

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    sheet_().appendRow([new Date(), v.who, v.title, v.kind, v.board, v.body, v.ref, "새 요청"]);
  } finally {
    lock.releaseLock();
  }

  try {
    telegram_([
      "📝 게시글 작성 요청",
      "",
      "주제: " + v.title,
      "요청: " + (v.who || "(적지 않음)"),
      "분야: " + (v.kind || "-") + "  ·  게시판: " + (v.board || "카페지기에게 맡김"),
      "",
      v.body.length > 1500 ? v.body.slice(0, 1500) + "…(시트에서 전체 보기)" : v.body,
      v.ref ? "\n참고: " + v.ref : "",
      "",
      "시트: " + SpreadsheetApp.getActiveSpreadsheet().getUrl()
    ].join("\n"));
  } catch (err) {
    // 알림이 실패해도 요청은 시트에 남아 있다
    console.error(err);
  }
  return reply_("ok");
}

function doGet() { return reply_("alive"); }

/* 설치 4단계에서 한 번 실행 — 봇과 대화한 사람(카페지기)의 대화방을 찾아 저장한다 */
function connectTelegram() {
  var token = PROPS.getProperty("TELEGRAM_TOKEN");
  if (!token) throw new Error("스크립트 속성에 TELEGRAM_TOKEN 을 먼저 넣어 주세요.");
  var res = JSON.parse(UrlFetchApp.fetch("https://api.telegram.org/bot" + token + "/getUpdates").getContentText());
  var ups = (res.result || []).filter(function (u) { return u.message && u.message.chat; });
  if (!ups.length) throw new Error("봇에게 아무 말이나 한 번 보낸 뒤 다시 실행해 주세요.");
  var chat = ups[ups.length - 1].message.chat;
  PROPS.setProperty("TELEGRAM_CHAT_ID", String(chat.id));
  telegram_("연결되었습니다. 앞으로 협회 상황판의 게시글 작성 요청이 여기로 옵니다.");
  sheet_();
  console.log("저장한 대화방: " + chat.id + " (" + (chat.first_name || chat.title || "") + ")");
}

function telegram_(text) {
  var token = PROPS.getProperty("TELEGRAM_TOKEN"), chat = PROPS.getProperty("TELEGRAM_CHAT_ID");
  if (!token || !chat) throw new Error("텔레그램이 아직 연결되지 않았습니다 (connectTelegram 실행).");
  UrlFetchApp.fetch("https://api.telegram.org/bot" + token + "/sendMessage", {
    method: "post",
    payload: { chat_id: chat, text: text, disable_web_page_preview: "true" }
  });
}

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEAD);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEAD.length).setFontWeight("bold");
  }
  return sh;
}

function reply_(s) {
  return ContentService.createTextOutput(s).setMimeType(ContentService.MimeType.TEXT);
}
