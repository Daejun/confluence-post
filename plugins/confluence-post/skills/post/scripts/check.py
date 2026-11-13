#!/usr/bin/env python3
"""Confluence DC storage format 조각 검사기.

사내 Confluence에 넣기 전에 돌린다 (Edit Source 붙여넣기든 MCP 게시든).
ERROR가 하나라도 있으면 넣지 않는다. 종료 코드 1.
"""
import html.entities
import re
import sys
import xml.etree.ElementTree as ET

# probe(2026-08-28, 2026-10-02)로 렌더링을 직접 확인한 매크로. 그대로 써도 된다.
CONFIRMED = {"code", "expand", "info", "note", "warning", "tip", "panel",
             "toc", "status", "noformat", "anchor", "plantuml", "latex",
             "attachments", "excerpt", "children",
             "pagetree", "include", "details", "section", "column", "chart"}
# 설치돼 있지만 조건이 붙는 것
CONDITIONAL = {
    "jira": "실제 이슈 키로만 렌더링된다. 없는 키는 오류가 난다",
    "drawio": "설치돼 있으나 에디터에서 그려야 한다. XHTML로 저작할 수 없다",
    "html": "렌더링은 된다(2026-11-12 확인). 사내 매뉴얼이 외부 리소스·과한 CSS 를 비권장하므로 "
            "HTML 입력 경로(--html-input, reference/html-input.md)에서만 새로 넣는다. "
            "그 밖에는 기존 페이지에 있던 것만 둔다",
}
# 조회형. 페이지를 볼 때마다 검색을 돌린다. 범위를 정하지 않으면 기본값을 따르는데,
# 매크로마다 달라 인스턴스 전체가 될 수 있다.
# 범위 없이 여럿 넣은 시험 페이지(P6)가 열리지 않았다 — 원인을 따로 떼어 확인하지는 않았다.
# 사용자가 요청했을 때만, 아래 파라미터 중 하나로 범위를 줘서 쓴다. 파라미터 이름은
# Atlassian·벤더 문서 기준이고 이 인스턴스에서 렌더링으로 확인하지는 않았다.
# 빈 집합은 범위를 줄 수 없는 것이다(space 전체 색인).
QUERY = {
    "recently-updated": {"spaces"},
    "contentbylabel": {"spaces", "cql"},
    "tasks-report-macro": {"spaces", "spaceAndPage", "pages"},
    "detailssummary": {"spaces", "cql"},
    "livesearch": {"spaceKey"},
    "blog-posts": {"spaces"},
    "popular-labels": {"spaceKey"},
    "listlabels": {"spaceKey"},
    "content-reporter": {"spaces", "scope"},
    "page-index": set(),
    "index": set(),
}
# cql 은 이런 조건이 있어야 범위가 있는 것으로 본다. 저장 때 서버가 labels 만으로
# `label = "…"` cql 을 만들어 붙이는데(P6), 그것만으로는 인스턴스 전체다.
CQL_SCOPE = re.compile(r"\b(space|ancestor|parent|id)\s*(=|in\b)|currentSpace\(\)", re.I)
# probe 대상은 아니지만 사내 기존 페이지에서 렌더링되는 것을 확인한 플러그인 매크로.
# 기존 페이지를 개정하려면 그대로 옮겨야 하므로 막지 않되, 근거가 probe가 아님을 밝힌다.
# P6(2026-10-02)에서 저장 후 다시 읽어 설치(등록)된 것을 확인한 매크로도 여기 둔다 —
# 렌더링과 파라미터는 확인하지 않았다.
IN_USE = {
    "table-filter": "Table Filter 플러그인",
    "report-table": "Reporting 플러그인",
    "report-column": "Reporting 플러그인",
    "report-info": "Reporting 플러그인",
    "report-empty": "Reporting 플러그인",
    "content-reporter": "Reporting 플러그인",
    "date-sort": "Reporting 플러그인",
    "contributors-summary": "Contributors 플러그인",
    "table-chart": "Table Filter 플러그인", "pivot-table": "Table Filter 플러그인",
    "ui-tabs": "Refined Toolkit", "ui-tab": "Refined Toolkit",
    "ui-expand": "Refined Toolkit", "ui-button": "Refined Toolkit",
    "divbox": "설치 확인", "horizontal-nav-group": "설치 확인",
    "horizontal-nav-item": "설치 확인", "tabs-group": "설치 확인",
    "tab-pane": "설치 확인",
    "multiexcerpt": "Multiexcerpt 플러그인", "multiexcerpt-include": "Multiexcerpt 플러그인",
    "excerpt-include": "기본 매크로", "change-history": "기본 매크로",
    "version-history": "설치 확인", "roadmap": "기본 매크로", "widget": "기본 매크로",
    "multimedia": "기본 매크로", "view-file": "기본 매크로", "viewpdf": "기본 매크로",
    "profile": "기본 매크로",
}
# 첨부를 반드시 가리켜야 하는 매크로. 없으면 페이지 저장이 서버 오류로 통째로 실패한다(P6)
NEEDS_ATTACHMENT = {"multimedia", "view-file", "viewpdf"}
# 렌더링이 안 되는 것을 probe로 확인했다. 저장하면 <ac:macro> 로 바뀌고 본문이 지워진다
UNAVAILABLE = {
    "mermaid": "미설치", "mermaid-cloud": "미설치", "mathblock": "미설치",
    "gliffy": "미설치", "lucidchart": "미설치", "iframe": "미설치",
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
TESTED_LANGS = {"c", "cpp", "c++", "diff", "bash", "shell", "text", "none", "python",
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
# 개정하는 페이지에 원래 있던 범위 없는 조회형 매크로를 그대로 옮길 때.
keep_query = "--keep-query" in sys.argv[1:]
# HTML 입력을 옮긴 조각. html 매크로를 페이지 범위 <style> 하나와 SVG 도식으로만 허용한다.
html_input = "--html-input" in sys.argv[1:]
WEBFONT_URL = "https://fonts.googleapis.com/css2?"


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


def check_query(el, name):
    """조회형 매크로는 범위를 명시해야 한다. 기본 범위는 매크로마다 다르다."""
    allowed = QUERY[name]
    scoped = []
    for p in el.findall(f"{{{NS['ac']}}}parameter"):
        pname = p.get(f"{{{NS['ac']}}}name", "")
        value = "".join(p.itertext()).strip()
        if pname not in allowed or not (value or len(p)):
            continue
        if pname == "cql" and not CQL_SCOPE.search(value):
            continue
        scoped.append(pname)
    if scoped:
        warn(f"매크로 `{name}`: 조회형이다. 사용자가 요청했을 때만 쓴다 — 범위"
             f"(`{'`, `'.join(scoped)}`)가 의도한 곳인지 확인한다")
    elif keep_query or probe_mode:
        warn(f"매크로 `{name}`: 범위 없는 조회형이다. 기존 페이지에 있던 것이라 그대로 둔다"
             f"(--keep-query)")
    elif not allowed:
        err(f"매크로 `{name}`: 범위를 줄 수 없는 조회형이다(space 전체를 훑는다). 쓰지 않는다")
    else:
        err(f"매크로 `{name}`: 조회형인데 범위를 정하지 않았다 — 기본 범위는 매크로마다 "
            f"다르고 인스턴스 전체일 수 있다. "
            f"`{'` / `'.join(sorted(allowed))}` 로 범위를 준다"
            + (" (cql 은 space·ancestor 조건이 있어야 한다)" if "cql" in allowed else "")
            + ". 개정하는 페이지에 원래 있던 것이면 --keep-query")


CSS_RULE = re.compile(r"([^{}]+)\{[^{}]*\}")
# style 속성 안에 큰따옴표가 또 들어가면(`font-family:"IBM Plex…"`) 속성이 거기서 끊기고
# 나머지가 이름 없는 속성 조각이 된다. 브라우저는 오류 없이 그 스타일을 버린다.
BROKEN_ATTR = re.compile(r'\b[\w-]+="[^"]*"[A-Za-z]')


def check_html_macro(el, n):
    """--html-input: html 매크로는 둘 중 하나만 허용한다.

    style — 이 페이지 본문(#main-content)에만 걸리는 <style> 블록 하나. 매크로가 막혀도
            글은 남는다.
    figure — SVG 도식 하나와 그 설명. 색 변수는 실제 색으로 풀려 있어야 한다.
    """
    b = el.find(f"{{{NS['ac']}}}plain-text-body")
    body = (b.text or "") if b is not None else ""
    where = f"html 매크로 {n}번째"
    low = body.lower()
    for bad, why in (("<script", "script"), ("<iframe", "iframe"), ("<form", "form"),
                     ("<input", "input")):
        if bad in low:
            err(f"{where}: <{why}> 를 넣지 않는다 — HTML 입력 경로는 style 과 SVG 도식만 쓴다")
    m = BROKEN_ATTR.search(body)
    if m:
        err(f"{where}: 속성 따옴표가 깨졌다 (`{m.group(0)[:40]}…`) — style 안의 글꼴 이름은 "
            f"작은따옴표로 쓴다")
    for url in re.findall(r"https?://[^\s\"'<>)]+", body):
        if url.startswith(WEBFONT_URL):
            warn(f"{where}: 웹폰트를 외부에서 불러온다. 사내 매뉴얼이 외부 리소스를 비권장한다 — "
                 f"막히면 대체 글꼴로 나온다")
        elif not url.startswith("http://www.w3.org/"):
            err(f"{where}: 외부 리소스 `{url[:60]}` 를 넣지 않는다")
    if "<style" in low:
        css = re.sub(r"/\*.*?\*/", "", body.split("<style", 1)[1].split(">", 1)[1]
                     .split("</style>", 1)[0], flags=re.S)
        if re.search(r"<svg", body, re.I):
            err(f"{where}: style 블록과 SVG 를 한 매크로에 섞지 않는다")
        for rule in CSS_RULE.finditer(css):
            for sel in rule.group(1).split(","):
                sel = sel.strip()
                if sel and not sel.startswith("#main-content"):
                    err(f"{where}: CSS 선택자 `{sel[:40]}` 가 #main-content 로 시작하지 않는다 — "
                        f"Confluence 화면 전체(메뉴·사이드바)에 걸린다")
        rest = re.sub(r"<link[^>]*>|<style.*?</style>", "", body, flags=re.S | re.I).strip()
        if rest:
            err(f"{where}: style 매크로에 style·link 말고 다른 내용이 있다 (`{rest[:40]}`)")
        return "style"
    if re.search(r"<svg", body, re.I):
        if "var(--" in body:
            err(f"{where}: SVG 에 CSS 색 변수(var(--…))가 남았다. Confluence 에는 그 변수가 "
                f"없어 검게 나온다 — 실제 색으로 바꾼다")
        return "figure"
    err(f"{where}: style 블록도 SVG 도식도 아니다. HTML 입력 경로는 그 둘만 html 매크로로 넣는다")
    return "other"


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

    # CDATA 안(code·html 매크로 본문)은 내용이므로 보지 않는다
    masked = CDATA.sub(lambda m: " " * len(m.group(0)), raw)
    for bad, why in [("<!DOCTYPE", "조각에 DOCTYPE을 쓰지 않는다"),
                     ("<html", "조각에 <html>을 쓰지 않는다"),
                     ("<body", "조각에 <body>를 쓰지 않는다"),
                     ("<style", "<style>은 무시된다 — 본문에 CSS 가 필요하면 HTML 입력 경로의 "
                                "html 매크로(reference/html-input.md)")]:
        m = re.search(re.escape(bad), masked, re.IGNORECASE)
        if m:
            err(f"{lineno(raw, m.start())}줄: {why}")
    m = re.search(r"<thead\b", masked, re.IGNORECASE)
    if m:
        warn(f"{lineno(raw, m.start())}줄: <thead> 는 저장은 되지만 이 스킬은 <tbody> 안 "
             f"<tr><th> 로 통일한다. 기존 페이지에 있던 표면 그대로 둔다")
    # 본문 style 속성의 font-size: `.78rem` `.86rem` 은 저장 때 지워졌고 px 는 남았다(2026-11-13).
    # html 매크로(CDATA) 안은 저장 때 건드리지 않으므로 masked 로만 본다
    for m in re.finditer(r"\bstyle=(\"[^\"]*\"|'[^']*')", masked):
        for size in re.findall(r"font-size\s*:\s*([^;\"']+)", m.group(1)):
            if not re.fullmatch(r"\d+(\.\d+)?px", size.strip()):
                err(f"{lineno(raw, m.start())}줄: 본문 style 의 font-size `{size.strip()}` 는 "
                    f"저장할 때 지워진다(.78rem 에서 확인) — px 로 쓴다")

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
    images, task_ids, excerpts = [], [], 0
    html_kinds = []
    for el in root.iter():
        tag = el.tag
        if el is not root and "}" not in tag and tag not in ALLOWED_TAGS:
            err(f"알 수 없는 태그 `<{tag}>`. Confluence가 받는 태그가 아니다 — "
                f"본문의 `<` 를 `&lt;` 로 이스케이프했는지 본다")
        if tag == f"{{{NS['ac']}}}structured-macro":
            name = el.get(f"{{{NS['ac']}}}name", "")
            if name in CONFIRMED:
                pass
            elif name == "html" and html_input:
                html_kinds.append(check_html_macro(el, len(html_kinds) + 1))
            elif name in CONDITIONAL:
                warn(f"매크로 `{name}`: {CONDITIONAL[name]}")
            elif name in QUERY:
                check_query(el, name)
            elif name in IN_USE:
                warn(f"매크로 `{name}`: {IN_USE[name]} — 기존 페이지에서 확인, "
                     f"probe 대상은 아니다. 새로 넣지 않는다")
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
                    warn("plantuml 매크로가 <p> 밖에 있다. 위아래 텍스트에 붙어 나온 "
                         "보고가 있었다 — <p> 로 감싼다 (감싸도 렌더링은 같다)")
            if name == "code":
                lang = el.find(f"{{{NS['ac']}}}parameter[@{{{NS['ac']}}}name='language']")
                if lang is None and not probe_mode:
                    warn("code 매크로에 language 가 없다. 기본 언어로 칠해진다 — "
                         "코드가 아니면 text")
                elif lang is not None and (lang.text or "") not in TESTED_LANGS:
                    warn(f"code language=`{lang.text}`: probe로 확인하지 않은 언어다. "
                         f"확실치 않으면 text")
            if name in ("code", "noformat"):
                check_cdata_head(el, name)
            if name == "excerpt":
                excerpts += 1
            if name == "column":
                body = parent.get(el)
                owner = parent.get(body) if body is not None else None
                if owner is None or owner.get(f"{{{NS['ac']}}}name") != "section":
                    err("column 매크로가 section 밖에 있다. 사내 매뉴얼: column 은 항상 "
                        "section 안에 둔다")
            if name in NEEDS_ATTACHMENT and el.find(f".//{{{NS['ri']}}}attachment") is None:
                err(f"매크로 `{name}` 이 첨부를 가리키지 않는다. 이대로 올리면 페이지 저장이 "
                    f"서버 오류로 실패한다")
            if name == "profile" and el.find(f".//{{{NS['ri']}}}user") is None:
                err("profile 매크로에 사용자가 없다. 저장하면 매크로가 "
                    "`[User Profile Macro (Malformed)]` 글자로 바뀐다")
        if tag == f"{{{NS['ac']}}}macro":
            # 저장할 때 Confluence 는 모르는 매크로를 이 옛 형식으로 바꾸고 본문을 지운다.
            # 이름이 아는 매크로면 오래된 페이지에 남은 옛 형식일 수 있다.
            name = el.get(f"{{{NS['ac']}}}name", "")
            if name in CONFIRMED or name in CONDITIONAL or name in QUERY or name in IN_USE:
                warn(f"`<ac:macro ac:name=\"{name}\">` 는 옛 형식이다. "
                     f"<ac:structured-macro> 로 쓴다")
            else:
                err(f"`<ac:macro ac:name=\"{name}\">` 는 설치되지 않은 매크로가 저장되며 "
                    f"바뀐 형태다. 본문은 이미 지워졌다 — 빼거나 원래 내용을 다시 쓴다")
        if tag == f"{{{NS['ac']}}}task" and not probe_mode:
            tid = el.find(f"{{{NS['ac']}}}task-id")
            if tid is None:
                err("<ac:task> 에 <ac:task-id> 가 없다. 체크박스를 누르면 저장 오류가 난다 — "
                    "페이지 안에서 겹치지 않는 번호를 넣는다")
            else:
                task_ids.append((tid.text or "").strip())
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
    if excerpts > 1:
        warn(f"excerpt 매크로가 {excerpts}개다. 사내 매뉴얼: 페이지에 하나만 — 끌어 쓰는 "
             f"쪽은 첫 번째만 인식한다")
    if html_input:
        styles = html_kinds.count("style")
        if styles > 1:
            err(f"style html 매크로가 {styles}개다. 페이지에 하나만 둔다")
        if html_kinds and html_kinds[0] != "style" and styles:
            warn("style html 매크로가 맨 앞에 있지 않다. 맨 앞에 두어야 본문이 그려지기 전에 "
                 "CSS 가 걸린다")
        print(f"html 매크로: style {styles}개, 도식 {html_kinds.count('figure')}개")
    dup = sorted({t for t in task_ids if task_ids.count(t) > 1})
    if dup:
        err(f"<ac:task-id> 가 겹친다: {', '.join(dup)}. 페이지 전체에서 겹치지 않게 매긴다")
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
    args = [a for a in sys.argv[1:]
            if a not in ("--probe", "--h1", "--keep-query", "--html-input")]
    if len(args) != 1:
        sys.exit("usage: check.py [--probe] [--h1] [--keep-query] [--html-input] <file.xhtml>")
    main(args[0])
