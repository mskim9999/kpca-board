
<script>
/* 게시글 작성 요청 — 카페지기의 구글 시트로 보낸다 (Apps Script 웹 앱) */
(function () {
  var APPS_URL = "__APPS_URL__";
  var f = document.getElementById("reqForm");
  if (!f) return;
  var $ = function (id) { return document.getElementById(id); };
  var out = $("rqOut"), msg = $("rqMsg"), btn = $("rqCopy");
  var ready = /^https:\/\/script\.google\.com\//.test(APPS_URL);
  btn.textContent = ready ? "요청 보내기" : "요청문 복사";
  function say(t, bad) { msg.textContent = t; msg.setAttribute("data-bad", bad ? "1" : "0"); }

  function vals() {
    return { who: $("rqWho").value.trim(), title: $("rqTitle").value.trim(), kind: $("rqKind").value,
      board: $("rqBoard").value, body: $("rqBody").value.trim(), ref: $("rqRef").value.trim(),
      website: ($("rqHp") || {}).value || "" };
  }
  function text(v) {
    var d = new Date();
    var l = ["[게시글 작성 요청] " + d.getFullYear() + "년 " + (d.getMonth() + 1) + "월 " + d.getDate() + "일"];
    if (v.who) l.push("요청: " + v.who);
    l.push("주제: " + v.title);
    if (v.kind) l.push("분야: " + v.kind);
    if (v.board) l.push("게시판: " + v.board);
    l.push("", "담을 내용:", v.body);
    if (v.ref) l.push("", "참고: " + v.ref);
    return l.join("\n");
  }
  function copyFallback(t) {
    out.textContent = t; out.hidden = false;
    var r = document.createRange(); r.selectNodeContents(out);
    var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
  }
  f.addEventListener("submit", function (e) {
    e.preventDefault();
    var v = vals();
    if (!v.title) { say("글 주제를 적어 주세요.", true); $("rqTitle").focus(); return; }
    if (!v.body) { say("담았으면 하는 내용을 적어 주세요.", true); $("rqBody").focus(); return; }
    if (!ready) {
      var t = text(v);
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(t).then(function () { say("복사했습니다. 카페지기에게 보내 주세요.", false); },
          function () { copyFallback(t); say("아래 글을 길게 눌러 복사해 주세요.", true); });
      } else { copyFallback(t); say("아래 글을 길게 눌러 복사해 주세요.", true); }
      return;
    }
    btn.disabled = true; say("보내는 중입니다…", false);
    var body = new URLSearchParams(v);
    fetch(APPS_URL, { method: "POST", mode: "no-cors", body: body }).then(function () {
      f.reset(); out.hidden = true; out.textContent = "";
      say("카페지기에게 보냈습니다. 고맙습니다.", false);
    }, function () {
      var t = text(v); copyFallback(t);
      say("보내지 못했습니다. 인터넷 연결을 확인하시거나, 아래 글을 복사해 카페지기에게 직접 보내 주세요.", true);
    }).then(function () { btn.disabled = false; });
  });
  $("rqClear").addEventListener("click", function () {
    f.reset(); out.hidden = true; out.textContent = ""; say("", false);
  });
})();
</script>
