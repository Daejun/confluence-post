#!/usr/bin/env python3
"""Confluence DC storage format 조각 검사기.

사내 Confluence에 넣기 전에 돌린다 (Edit Source 붙여넣기든 MCP 게시든).
ERROR가 하나라도 있으면 넣지 않는다. 종료 코드 1.
"""
import html.entities
import re
import sys
import xml.etree.ElementTree as ET

# probe(2026-08-28)로 렌더링을 직접 확인한 매크로. 그대로 써도 된다.
CONFIRMED = {"code", "expand", "info", "note", "warning", "tip", "panel",
             "toc", "status", "noformat", "anchor", "plantuml", "latex",
             "attachments", "recently-updated"}
# 설치돼 있지만 조건이 붙는 것
CONDITIONAL = {
    "jira": "실제 이슈 키로만 렌더링된다. 없는 키는 오류가 난다",
    "drawio": "설치돼 있으나 에디터에서 그려야 한다. XHTML로 저작할 수 없다",
    # probe 에서는 안 보였지만 실제 페이지 수십 곳에서 최근까지 쓰인다. probe 페이지에
    # 하위 페이지·발췌 대상이 없어 비어 보였을 수 있다.
    "excerpt": "실제 페이지에서 쓰이나 렌더링은 다시 확인해야 한다. 새로 넣지 않고 "
               "기존 페이지에 있던 것만 옮긴다",
    "children": "실제 페이지에서 쓰이나 렌더링은 다시 확인해야 한다. 새로 넣지 않고 "
                "기존 페이지에 있던 것만 옮긴다",
}
# 렌더링이 안 되는 것을 probe로 확인했다
UNAVAILABLE = {
    "mermaid": "미설치", "mermaid-cloud": "미설치", "mathblock": "미설치",
    "gliffy": "미설치",
}
# 사내 PlantUML 서버 버전. reference/plantuml.md 참조.
PLANTUML_VERSION = "1.2024.8"
# 확인된 다이어그램 타입. P4로 확인되면 늘린다.
PUML_ALLOWED = {"uml"}
PUML_KNOWN = {"uml", "mindmap", "wbs", "gantt", "salt", "json", "yaml",
              "ditaa", "dot", "creole", "ebnf", "regex", "chen", "chronology"}
PUML_ERR = [
    (re.compile(r"^\s*!include(url|sub)?\s+[\"']?\s*(https?://|<)", re.I | re.M),
     "!include 로 외부 URL·stdlib 를 끌어온다. 서버가 외부망을 못 쓰면 통째로 실패한다"),
    (re.compile(r"^\s*!(procedure|function|unquoted)\b", re.I | re.M),
     "전처리기 문법. 버전에 민감하다"),
]
PUML_WARN = [
    (re.compile(r"^\s*!theme\b", re.I | re.M),
     "!theme 는 번들 테마에 의존한다. 확인 안 됐다"),
    (re.compile(r"<img:|\bsprite\b", re.I),
     "sprite·외부 이미지 의존"),
    (re.compile(r"^\s*\(\*\)", re.M),
     "옛 activity 문법. start / :단계; / stop 을 쓴다"),
    (re.compile(r"^\s*skinparam\b", re.I | re.M),
     "skinparam 은 이름이 버전에 따라 바뀐다. 서버 기본값에 맡긴다"),
]

# probe로 하이라이팅을 확인한 code language
TESTED_LANGS = {"c", "cpp", "diff", "bash", "shell", "text", "none", "python",
                "py", "java", "js", "javascript", "json", "yaml", "xml", "sql",
                "rust", "go", "perl", "powershell", "makefile", "ruby"}

# Confluence storage format 이 받는 HTML 태그. 이 밖의 이름이 나오면 대개 본문의
# `<` 를 이스케이프하지 않은 것이다 (`<writer> blocked` 같은 로그 인용).
ALLOWED_TAGS = {
    "p", "h1", "h2", "h3", "h4", "h5", "h6", "br", "hr", "a", "span", "div",
    "strong", "em", "b", "i", "u", "s", "del", "ins", "sub", "sup", "code",
    "pre", "tt", "kbd", "samp", "var", "cite", "q", "small", "big",
    "ul", "ol", "li", "dl", "dt", "dd", "blockquote",
    "table", "tbody", "thead", "tfoot", "tr", "th", "td", "caption",
    "colgroup", "col", "img", "time",
}
HEADING = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1\s*>", re.DOTALL | re.I)
CDATA = re.compile(r"<!\[CDATA\[.*?\]\]>", re.DOTALL)
ENTITY = re.compile(r"&(#\d+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]*);")
NS = {"ac": "http://x/ac", "ri": "http://x/ri"}

errors, warns = [], []
probe_mode = "--probe" in sys.argv[1:]
# 이어 붙일 페이지가 본문을 h1 부터 쓰는 관례일 때. SKILL.md 6단계.
h1_mode = "--h1" in sys.argv[1:]


def err(msg):
    errors.append(msg)


def warn(msg):
    warns.append(msg)


def lineno(text, pos):
    return text.count("\n", 0, pos) + 1


def check_text(raw):
    """CDATA 밖 구간의 이스케이프를 본다."""
    pos = 0
    for m in CDATA.finditer(raw):
        yield from scan_plain(raw, pos, m.start())
        pos = m.end()
    yield from scan_plain(raw, pos, len(raw))


def scan_plain(raw, start, end):
    seg = raw[start:end]
    for m in re.finditer(r"&", seg):
        at = start + m.start()
        e = ENTITY.match(raw, at)
        if not e:
            yield ("E", lineno(raw, at),
                   "이스케이프 안 된 `&`. `&amp;` 로 바꾼다")
            continue
        name = e.group(1)
        if not name.startswith("#") and name not in ("amp", "lt", "gt", "quot", "apos") \
                and name + ";" not in html.entities.html5:
            yield ("E", lineno(raw, at), f"알 수 없는 엔티티 `&{name};`")
    escaped = ("이스케이프 안 된 `<`. `&lt;` 로 바꾼다 "
               "(문단만이 아니라 <code> 안의 글자도 CDATA 밖이다)")
    for m in re.finditer(r"<(?![A-Za-z/!?])", seg):
        yield ("E", lineno(raw, start + m.start()), escaped)
    # `<hanqi@vivo.com>` 처럼 글자로 시작하지만 태그 이름이 될 수 없는 것
    for m in re.finditer(r"<([A-Za-z][^\s/>]*)", seg):
        if re.search(r"[^A-Za-z0-9._:-]", m.group(1)):
            yield ("E", lineno(raw, start + m.start()), escaped)
    for m in re.finditer(r"\]\]>", seg):
        yield ("E", lineno(raw, start + m.start()),
               "본문에 `]]>` 가 있다. CDATA가 여기서 끊긴다 — code 매크로를 둘로 나눈다")


def neutralize(raw):
    """XML 파서가 모르는 HTML 엔티티를 CDATA 밖에서만 치운다."""
    out, pos = [], 0
    for m in CDATA.finditer(raw):
        out.append(ENTITY.sub(_sub, raw[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(ENTITY.sub(_sub, raw[pos:]))
    return "".join(out)


def _sub(m):
    name = m.group(1)
    if name.startswith("#") or name in ("amp", "lt", "gt", "quot", "apos"):
        return m.group(0)
    return "￼"


def check_headings(raw):
    """제목 단계로 절 구분을 본다.

    여기서 보는 것은 출력물 안에서 닫힌 규칙뿐이다. 원문의 절이 빠지지 않았는지,
    이어 붙일 페이지의 관례를 따랐는지는 정적으로 볼 수 없다 — SKILL.md 6단계에서
    사람이 대조한다.
    """
    masked = CDATA.sub(lambda m: " " * len(m.group(0)), raw)
    heads = [(int(m.group(1)),
              re.sub(r"<[^>]+>", "", m.group(2)).strip(),
              lineno(raw, m.start()))
             for m in HEADING.finditer(masked)]
    top = 1 if h1_mode else 2
    if not heads:
        if raw.count("\n") + 1 >= 60:
            warn(f"제목이 하나도 없다 ({raw.count(chr(10)) + 1}줄). h{top} 로 절을 나눈다")
        return
    prev = None
    for lvl, text, ln in heads:
        if lvl == 1 and not h1_mode:
            warn(f"{ln}줄: <h1> 은 페이지 제목이 가져간다. 본문은 h2 부터 쓴다 "
                 f"(이어 붙일 페이지가 h1 부터 쓰면 --h1)")
        if lvl == 6:
            warn(f"{ln}줄: <h6> 는 probe로 확인하지 않았다 (h2~h5만 확인)")
        if not text:
            warn(f"{ln}줄: <h{lvl}> 이 비어 있다")
        if prev is None:
            if lvl > top and not probe_mode:
                warn(f"{ln}줄: 첫 제목이 <h{lvl}> 이다. 본문은 h{top} 부터 시작한다")
        elif lvl > prev + 1:
            warn(f"{ln}줄: <h{prev}> 다음이 <h{lvl}> 이다. 단계를 건너뛰면 "
                 f"toc와 절 구분이 어긋난다")
        prev = lvl


def check_cdata_head(el, name):
    """`<![CDATA[` 다음 줄부터 코드를 시작하면 렌더링에 빈 줄이 하나 생긴다.

    코드 자체의 들여쓰기(탭·공백)는 내용이므로 건드리지 않는다. 첫 글자가 개행일
    때만 본다.
    """
    b = el.find(f"{{{NS['ac']}}}plain-text-body")
    body = (b.text or "") if b is not None else ""
    if not body:
        return
    if body.lstrip(" \t")[:1] == "\n":
        first = body.strip().splitlines()[0][:30] if body.strip() else ""
        warn(f"{name} 매크로: `<![CDATA[` 다음 줄에서 내용이 시작한다 — 코드 위에 "
             f"빈 줄이 생긴다. `<![CDATA[` 바로 뒤에 붙인다"
             + (f" (`{first}`)" if first else ""))


def check_plantuml(src):
    """PlantUML 본문을 1.2024.8 에서 안전한 부분집합으로 좁힌다."""
    if src != src.lstrip():
        err("plantuml: `@startuml` 앞에 공백이 있다. "
            "`<![CDATA[` 바로 뒤에 붙인다 — 들여쓰면 첫 줄을 못 읽는다")
    lines = [l for l in src.splitlines() if l.strip()]
    if not lines:
        err("plantuml: 본문이 비어 있다")
        return
    m = re.match(r"@start(\w+)", lines[0].strip())
    if not m:
        err("plantuml: 첫 줄이 `@start...` 가 아니다")
        return
    kind = m.group(1).lower()
    e = re.match(r"@end(\w+)", lines[-1].strip())
    if not e or e.group(1).lower() != kind:
        err(f"plantuml: 마지막 줄이 `@end{kind}` 가 아니다")
    if kind not in PUML_ALLOWED:
        msg = (f"plantuml: `@start{kind}` 는 사내 서버에서 확인되지 않았다 "
               f"(P4 미확인). `@startuml` 로 표현한다")
        warn(msg) if kind in PUML_KNOWN else err(msg)
    for rx, why in PUML_ERR:
        if rx.search(src):
            (warn if probe_mode else err)(f"plantuml: {why}")
    for rx, why in PUML_WARN:
        if rx.search(src):
            warn(f"plantuml: {why}")
    if re.search(r"[^\x00-\x7f]", src):
        warn("plantuml: 한글·비ASCII 라벨이 있다. 서버 폰트에 달렸고 폰트가 없으면 "
             "네모로 나온다 (P4 V07 미확인). 확인 전에는 영문 라벨을 쓴다")


def main(path):
    raw = open(path, encoding="utf-8").read()
    print(f"{path}: {raw.count(chr(10)) + 1}줄, {len(raw)}자")

    for kind, ln, msg in check_text(raw):
        (err if kind == "E" else warn)(f"{ln}줄: {msg}")

    check_headings(raw)

    for bad, why in [("<!DOCTYPE", "조각에 DOCTYPE을 쓰지 않는다"),
                     ("<html", "조각에 <html>을 쓰지 않는다"),
                     ("<body", "조각에 <body>를 쓰지 않는다"),
                     ("<style", "<style>은 무시된다")]:
        m = re.search(re.escape(bad), raw, re.IGNORECASE)
        if m:
            err(f"{lineno(raw, m.start())}줄: {why}")
    m = re.search(r"<thead\b", raw, re.IGNORECASE)
    if m:
        warn(f"{lineno(raw, m.start())}줄: <thead> 는 저장은 되지만 이 스킬은 <tbody> 안 "
             f"<tr><th> 로 통일한다. 기존 페이지에 있던 표면 그대로 둔다")

    wrapped = ('<root xmlns:ac="http://x/ac" xmlns:ri="http://x/ri">'
               + neutralize(raw) + "</root>")
    try:
        root = ET.fromstring(wrapped)
    except ET.ParseError as e:
        ln = max(1, e.position[0] - 1)
        err(f"{ln}줄: XML이 깨졌다 — {e.msg.split(':')[0]}. 태그 짝과 이스케이프를 본다")
        report()
        return

    parent = {c: p for p in root.iter() for c in p}
    images = []
    for el in root.iter():
        tag = el.tag
        if el is not root and "}" not in tag and tag not in ALLOWED_TAGS:
            err(f"알 수 없는 태그 `<{tag}>`. Confluence가 받는 태그가 아니다 — "
                f"본문의 `<` 를 `&lt;` 로 이스케이프했는지 본다")
        if tag == f"{{{NS['ac']}}}structured-macro":
            name = el.get(f"{{{NS['ac']}}}name", "")
            if name in CONFIRMED:
                pass
            elif name in CONDITIONAL:
                warn(f"매크로 `{name}`: {CONDITIONAL[name]}")
            elif name in UNAVAILABLE and not probe_mode:
                err(f"매크로 `{name}`: {UNAVAILABLE[name]} (probe로 확인). 쓰지 않는다")
            elif probe_mode:
                warn(f"매크로 `{name}`: 미확인 (probe 모드라 통과)")
            else:
                err(f"매크로 `{name}`: 확인되지 않은 매크로다. 쓰지 않는다")
            if name == "plantuml":
                b = el.find(f"{{{NS['ac']}}}plain-text-body")
                check_plantuml(b.text or "" if b is not None else "")
                if parent[el].tag != "p" and not probe_mode:
                    warn("plantuml 매크로가 <p> 밖에 있다. inline 으로 그려져 위아래 "
                         "텍스트에 붙는다 — <p> 로 감싼다")
            if name == "code":
                lang = el.find(f"{{{NS['ac']}}}parameter[@{{{NS['ac']}}}name='language']")
                if lang is not None and (lang.text or "") not in TESTED_LANGS:
                    warn(f"code language=`{lang.text}`: probe로 확인하지 않은 언어다. "
                         f"확실치 않으면 text")
            if name in ("code", "noformat"):
                check_cdata_head(el, name)
        if tag in ("ul", "ol") and parent.get(el) is not None \
                and parent[el].tag in ("ul", "ol"):
            err("중첩 목록이 <li> 밖에 있다. 부모 <li> 안으로 넣는다")
        if tag == f"{{{NS['ri']}}}attachment":
            images.append(el.get(f"{{{NS['ri']}}}filename", "?"))
        if tag == "img" and "/download/attachments/" in el.get("src", ""):
            err(f"<img src=\"{el.get('src')[:60]}…\"> 는 MCP 가 첨부 이미지를 바꿔 보여준 "
                f"형태다. <ac:image><ri:attachment ri:filename=\"…\"/></ac:image> 로 되돌린다")

    if root.text and root.text.strip():
        warn("최상위에 <p> 밖 맨 텍스트가 있다")
    if images:
        print("첨부 필요: " + ", ".join(sorted(set(images))))
    report()


def report():
    for m in warns:
        print("WARN  " + m)
    for m in errors:
        print("ERROR " + m)
    if errors:
        print(f"\n{len(errors)}건 — 고치기 전에는 Confluence에 넣지 않는다")
        sys.exit(1)
    print("\nOK" + (f" (WARN {len(warns)}건)" if warns else ""))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a not in ("--probe", "--h1")]
    if len(args) != 1:
        sys.exit("usage: check.py [--probe] [--h1] <file.xhtml>")
    main(args[0])
