
<script>
/* 게시글 작성 요청 — 요청문을 만들어 복사한다. 저장하지 않는다 */
(function () {
  var f = document.getElementById("reqForm");
  if (!f) return;
  var $ = function (id) { return document.getElementById(id); };
  var out = $("rqOut"), msg = $("rqMsg");
  function say(t, bad) { msg.textContent = t; msg.setAttribute("data-bad", bad ? "1" : "0"); }
  try { var w = localStorage.getItem("rqWho"); if (w) $("rqWho").value = w; } catch (e) {}

  function compose() {
    var d = new Date();
    var lines = ["[게시글 작성 요청] " + d.getFullYear() + "년 " + (d.getMonth() + 1) + "월 " + d.getDate() + "일"];
    if ($("rqWho").value.trim()) lines.push("요청: " + $("rqWho").value.trim());
    lines.push("주제: " + $("rqTitle").value.trim());
    if ($("rqKind").value) lines.push("분야: " + $("rqKind").value);
    if ($("rqBoard").value) lines.push("게시판: " + $("rqBoard").value);
    lines.push("", "담을 내용:", $("rqBody").value.trim());
    if ($("rqRef").value.trim()) lines.push("", "참고: " + $("rqRef").value.trim());
    return lines.join("\n");
  }
  function selectOut() {
    var r = document.createRange(); r.selectNodeContents(out);
    var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
  }
  f.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!$("rqTitle").value.trim()) { say("글 주제를 적어 주세요.", true); $("rqTitle").focus(); return; }
    if (!$("rqBody").value.trim()) { say("담았으면 하는 내용을 적어 주세요.", true); $("rqBody").focus(); return; }
    try { localStorage.setItem("rqWho", $("rqWho").value.trim()); } catch (e2) {}
    var t = compose();
    out.textContent = t; out.hidden = false;
    var done = function () { say("복사했습니다. 카페지기에게 카톡이나 문자로 붙여 보내 주세요.", false); };
    var fail = function () { selectOut(); say("자동 복사가 막혔습니다. 아래 글이 선택되어 있으니 길게 눌러 복사해 주세요.", true); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(done, fail);
    } else { fail(); }
  });
  $("rqClear").addEventListener("click", function () {
    ["rqTitle", "rqBody", "rqRef"].forEach(function (id) { $(id).value = ""; });
    $("rqKind").value = ""; $("rqBoard").value = "";
    out.hidden = true; out.textContent = ""; say("", false);
  });
})();
</script>
