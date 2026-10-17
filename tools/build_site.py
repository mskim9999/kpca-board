"""공유용 상황판(ro/share.html)을 깃허브 Pages 에 올릴 독립 사이트로 바꾼다.

사용: python3 build_site.py [APPS_URL]
출력: site/index.html, site/robots.txt, site/.nojekyll
"""
import os, re, sys

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(S, "ro")
OUT = os.path.join(S, "site")
os.makedirs(OUT, exist_ok=True)
apps = sys.argv[1] if len(sys.argv) > 1 else ""

s = open(os.path.join(R, "share.html"), encoding="utf-8").read()

# 0. 회원 사례는 사이트에 싣지 않는다 (운영자 2026-10-18, 원장 F-233)
#    작업용 상황판에는 그대로 두고, 공개 저장소로 나가는 이 사본에서만 뺀다.
def cut_between(s, start, end, repl, label):
    i = s.find(start)
    if i < 0:
        print("회원 사례 빼기: 못 찾음 —", label, file=sys.stderr); return s
    j = s.find(end, i + len(start))
    if j < 0:
        print("회원 사례 빼기: 끝을 못 찾음 —", label, file=sys.stderr); return s
    return s[:i] + repl + s[j:]

# 볼트 카드 「통증」 — 제88회 회원 통증 관리 경과
s = cut_between(s, "## 실제 관리에 성공한 사례", "## 진통제에 대한 협회 자료의 우려",
                "## 실제 관리에 성공한 사례\n\n회원 사례라 사이트에는 싣지 않습니다.\n\n---\n\n", "kb 통증")
# 강의안 「췌장암 환우의 통증 관리」 — 7절 본문과 순서표의 한 줄
s = cut_between(s, "### 7. 실제 사례 (5분)", "### 8. 오늘부터 할 것",
                "### 7. 실제 사례 (5분)\n\n회원 사례라 사이트에는 싣지 않습니다.\n\n---\n\n", "lec-pain 7절")
s = re.sub(r"(\| 7 \| 실제 사례 \| )제88회 [^|]*님( \|)", r"\1모임 회원 사례(생략)\2", s)
# 댓글 관리 탭 — 보호자 댓글 요약과 답글 원문
s = re.sub(r'<div class="lane">\s*<h3>영양 · 화학항암 부작용.*?</div>(\s*<div class="lane quiet">)',
           r'<div class="lane"><h3>확정 답글 1건</h3><p>회원 댓글에 단 답글이라 사이트에는 싣지 않습니다.</p></div>\1', s, count=1, flags=re.S)
s = re.sub(r'<script type="text/plain" class="doc" data-key="cmt-folfi".*?</script>\n?', "", s, count=1, flags=re.S)
s = s.replace("2026-09-09 댓글 「폴피리녹스 1차 후 못 드심」", "2026-09-09 회원 댓글 답글")
s = s.replace("되묻기 4개 — 입 헐음·구역질·맛·변", "되묻기 4개")
left = [w for w in ("별아해", "폴피리녹스", "보호자 작성", "입 헐음") if w in s]
assert not left, "회원 사례가 남았다: " + ", ".join(left)

# 1. 요청 칸 — 복사 대신 구글 시트로 보낸다
old_js = open(os.path.join(R, "request_part.js"), encoding="utf-8").read()
assert old_js in s
s = s.replace(old_js, open(os.path.join(R, "request_site.js"), encoding="utf-8").read().replace("__APPS_URL__", apps))
s = s.replace('쓰고 싶은 글감을 적고 <strong>요청문 복사</strong>를 누르신 뒤, 카페지기에게 카톡이나 문자로 붙여 보내 주세요.\n      이 화면은 저장이 되지 않아 여기 적은 내용이 저절로 전달되지는 않습니다.',
              '쓰고 싶은 글감을 적고 <strong>요청 보내기</strong>를 누르시면 카페지기에게 바로 전달됩니다.' if apps else
              '쓰고 싶은 글감을 적고 <strong>요청문 복사</strong>를 누르신 뒤, 카페지기에게 보내 주세요.')
# 프로그램이 채우는 숨은 칸 (스팸 거르기)
s = s.replace('<form class="req-form" id="reqForm" novalidate>',
              '<form class="req-form" id="reqForm" novalidate>\n      <input type="text" id="rqHp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0">')
s = s.replace("작업용 상황판을 ", "카페지기의 작업용 상황판을 ")

# 2. 온전한 문서로 감싼다 — 검색엔진에는 걸리지 않게
m = re.search(r"<title>(.*?)</title>", s)
title = m.group(1) if m else "제4기 상황판"
s = s.replace(m.group(0), "", 1) if m else s
head = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow,noarchive">
<meta name="referrer" content="no-referrer">
<meta name="theme-color" content="#221D35">
<title>한국췌장암환우협회 제4기 상황판</title>
<style>:root{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""
s = head + s + "\n</body>\n</html>\n"
assert "claude.use(" not in s and "/_blob/" not in s

open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(s)
open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
open(os.path.join(OUT, ".nojekyll"), "w").write("")
print("site/index.html", len(s.encode()) // 1024, "KB", "· 요청 전송", "켜짐" if apps else "꺼짐(복사)")
