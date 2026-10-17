"""운영진 공유용(읽기 전용) 상황판을 만든다.

입력: hub/index.html (작업용 상황판 최신본), dbdump/ (작업용 상황판 저장소 내보내기)
출력: ro/share.html — 저장소 없이 열리는 한 장짜리 페이지
"""
import base64, glob, io, json, os, re, sys, datetime
from fontTools import subset
from fontTools.ttLib import TTFont

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(S, "hub/index.html"), encoding="utf-8").read()

# 0. 발행 골격 떼기 (Artifact 가 다시 씌운다)
m = re.match(r"<!doctype html><html><head>.*?</head><body>\n?", src, re.S)
if m:
    src = src[m.end():]
src = re.sub(r"</body></html>\s*$", "", src)

# 1. 저장소 내용 묶기 — 공유용에 넣을 것만
DUMP = os.path.join(S, "dbdump")
data = {}
for coll in ["hub", "posted", "writereq", "reviews", "agentdoc"]:
    for f in sorted(glob.glob(os.path.join(DUMP, coll, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        body = d.get("data", d) if isinstance(d, dict) and "data" in d and "id" in d else d
        data[coll + "/" + os.path.splitext(os.path.basename(f))[0]] = body
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
stamp_txt = f"{stamp.year}년 {stamp.month}월 {stamp.day}일 {stamp.hour:02d}:{stamp.minute:02d}"

shim = """<script>
/* 읽기 전용 저장소 — 작업용 상황판에서 내보낸 내용을 담고, 쓰기는 모두 거절한다 */
window.RO = (function () {
  var DATA = %s;
  function deny() { return Promise.reject({ code: "not_granted", message: "읽기 전용 화면입니다" }); }
  function snap(path) {
    var has = Object.prototype.hasOwnProperty.call(DATA, path);
    var body = has ? JSON.parse(JSON.stringify(DATA[path])) : undefined;
    return { id: path.split("/").pop(), exists: has, data: function () { return body; }, metadata: { hasPendingWrites: false } };
  }
  function qsnap(coll) {
    var depth = coll.split("/").length;
    var docs = Object.keys(DATA).filter(function (k) {
      return k.indexOf(coll + "/") === 0 && k.split("/").length === depth + 1;
    }).map(snap);
    return { docs: docs, size: docs.length, empty: !docs.length,
      forEach: function (fn) { docs.forEach(fn); },
      docChanges: function () { return docs.map(function (d) { return { type: "added", doc: d }; }); } };
  }
  function doc(path) {
    return { id: path.split("/").pop(), path: path,
      get: function () { return Promise.resolve(snap(path)); },
      onSnapshot: function (next) { setTimeout(function () { next(snap(path)); }, 0); return function () {}; },
      set: deny, update: deny, delete: deny, acquire: deny,
      collection: function (c) { return coll(path + "/" + c); } };
  }
  function coll(path) {
    var q = { path: path,
      doc: function (id) { return doc(path + "/" + (id || "x")); },
      where: function () { return q; }, orderBy: function () { return q; }, limit: function () { return q; },
      get: function () { return Promise.resolve(qsnap(path)); },
      onSnapshot: function (next) { setTimeout(function () { next(qsnap(path)); }, 0); return function () {}; },
      add: deny };
    return q;
  }
  var db = { doc: doc, collection: coll };
  return { use: function (name) { return Promise.resolve(name === "db" ? db : null); } };
})();
</script>
""" % json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

s = src
n = s.count("claude.use(")
s = s.replace("claude.use(", "RO.use(")
s = s.replace('typeof claude !== "undefined" && claude && typeof claude.use === "function"', "true")
assert "claude.use(" not in s

# 2. 글꼴 — 페이지에 쓰인 글자만 남겨 페이지 안에 넣는다
FD = os.path.join(S, "artifact-files/a9f13a27-6d23-4f7f-9514-de754659eb5b")
fonts = [("Paperlogy", "500 650", "1819867758c1c0bb229015dae45c09a5"),
         ("Paperlogy", "651 900", "5b355df6466963721c1d2a3680383609"),
         ("KoPub Dotum", "300 550", "4ee508aee0d962fa5cdc7ff87e1e4a43"),
         ("KoPub Dotum", "551 900", "a053d9b249a97d996219235c2dc64d2f")]
chars = set(s) | set(json.dumps(data, ensure_ascii=False)) | set("0123456789 ·—–-→↗↓▸…「」『』《》()[]%.,:;!?'\"") | set("읽기전용공유용갱신")
text = "".join(sorted(c for c in chars if ord(c) >= 32))
faces = []
for fam, w, fid in fonts:
    font = TTFont(os.path.join(FD, fid + ".ttf"))
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["*"]; opts.name_IDs = []
    sub = subset.Subsetter(opts); sub.populate(text=text); sub.subset(font)
    buf = io.BytesIO(); font.flavor = "woff2"; font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    faces.append('@font-face{font-family:"%s";font-weight:%s;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2")}' % (fam, w, b64))
    print(fam, w, len(buf.getvalue()) // 1024, "KB", file=sys.stderr)
s = re.sub(r'@font-face\{font-family:"(Paperlogy|KoPub Dotum)";[^}]*/_blob/[^}]*\}\n?', "", s)
s = s.replace("/* 강의안과 같은 글꼴 — 파일은 이 상황판의 자산 저장소에 있다 */", "\n".join(faces))
assert "/_blob/" not in s

# 3. 쓰기 손잡이 감추기
ro_css = """<style>
/* ── 읽기 전용 ── */
#cpWrite,#cpFinal,#writeBox,#finalBox,.final,.pick,.compose,.propose,#btnPropose,#btnSend,
.hub-save,.hub-hint{display:none!important}
.hf{pointer-events:none}
.hf:placeholder-shown{visibility:hidden}
select.hub-status{pointer-events:none;background-image:none!important;padding-right:10px!important}
header .ro{font-size:12px;color:var(--head-fg);background:rgba(255,255,255,.12);border-radius:999px;padding:3px 10px}
.ro-foot{margin-top:40px;font-size:12px;color:var(--ink-3)}
.req{background:var(--raise);border:1px solid var(--line);border-left:4px solid var(--leaf);border-radius:4px;
  padding:20px 22px;margin-bottom:30px}
.req h2{margin-bottom:6px}
.req .lead{margin:0 0 16px}
.req-form{display:flex;flex-direction:column;gap:12px}
.req-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.req-f{display:flex;flex-direction:column;gap:5px;font-size:13px;color:var(--ink-2);min-width:0}
.req-f b{font-weight:500;color:var(--stop);font-size:11px;margin-left:4px}
.req-f em{font-style:normal;color:var(--ink-3);font-size:11px;margin-left:4px}
.req-f input,.req-f select,.req-f textarea{font:inherit;font-size:14px;color:var(--ink);background:var(--raise);
  border:1px solid var(--line);border-radius:5px;padding:9px 11px;width:100%;min-width:0}
.req-f textarea{resize:vertical;line-height:1.6}
.req-f input:focus,.req-f select:focus,.req-f textarea:focus{outline:2px solid var(--leaf);outline-offset:0;border-color:var(--leaf)}
.req-act{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.req-msg{font-size:12.5px;color:var(--done)}
.req-msg[data-bad="1"]{color:var(--stop)}
.req-out{margin:0;white-space:pre-wrap;font-family:var(--sans);font-size:13px;line-height:1.6;color:var(--ink);
  background:var(--sunk-2);border:1px dashed var(--line);border-radius:5px;padding:12px 14px;user-select:text}
@media (max-width:620px){.req{padding:16px 15px}}
</style>
"""
s = s.replace("<title>협회 운영 상황판</title>", "<title>제4기 상황판 공유용</title>")
s = s.replace('<span class="who">카페지기, 운영진 공유용</span>',
              '<span class="who">카페지기, 운영진 공유용</span>\n  <span class="ro">읽기 전용 · ' + stamp_txt + ' 기준</span>')
# 기준일은 내보낸 날로 고정
s = s.replace('dt.textContent = "기준일 " + d.getFullYear() + "년 " + (d.getMonth() + 1) + "월 " + d.getDate() + "일";',
              'dt.textContent = "";')
# 저장소 연결 문구 대신 읽기 전용
s = s.replace('mark("error", "저장소에 연결되지 않아 읽기만 됩니다"); return;', "return;")
# hub 입력칸은 끝까지 읽기 전용으로
s = s.replace('      f.readOnly = false; if (f.tagName === "SELECT") { f.disabled = false; }\n', "")
s = s.replace('<!-- HUBJS:END -->', '<!-- HUBJS:END -->\n<p class="wrap ro-foot">이 화면은 작업용 상황판을 ' + stamp_txt + '에 옮겨 담은 읽기 전용 사본입니다. 내용 수정은 카페지기에게 말씀해 주세요.</p>')

# 게시글 작성 요청 칸 (공유용 전용)
R = os.path.join(S, "ro")
anchor = '<div role="tabpanel" id="b-post" aria-labelledby="t-post" hidden>\n'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + open(os.path.join(R, "request_part.html"), encoding="utf-8").read())
s = s.replace('<!-- HUBJS:END -->', '<!-- HUBJS:END -->' + open(os.path.join(R, "request_part.js"), encoding="utf-8").read(), 1)

first = s.index("<script")
s = s[:first] + shim + s[first:]
s = s.replace("<title>제4기 상황판 공유용</title>", "<title>제4기 상황판 공유용</title>\n" + ro_css, 1)

open(os.path.join(S, "ro/share.html"), "w", encoding="utf-8").write(s)
print("claude.use 치환", n, "· 크기", len(s.encode()) // 1024, "KB", file=sys.stderr)
