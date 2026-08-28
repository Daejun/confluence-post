#!/usr/bin/env python3
"""Confluence DC storage format 조각 검사기.

사내 Confluence의 Edit Source에 넣기 전에 돌린다.
ERROR가 하나라도 있으면 넣지 않는다. 종료 코드 1.
"""
import html.entities
import re
import sys
import xml.etree.ElementTree as ET

# probe(2026-08-28)로 렌더링을 직접 확인한 매크로
CONFIRMED = {"code", "expand"}
# Confluence DC 기본 번들. 설치 확인(ANSWER.md A4)은 아직 안 됐다.
BUNDLED = {"info", "note", "warning", "tip", "panel", "toc",
           "status", "noformat", "anchor"}

CDATA = re.compile(r"<!\[CDATA\[.*?\]\]>", re.DOTALL)
ENTITY = re.compile(r"&(#\d+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]*);")
NS = {"ac": "http://x/ac", "ri": "http://x/ri"}

errors, warns = [], []


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


def main(path):
    raw = open(path, encoding="utf-8").read()
    print(f"{path}: {raw.count(chr(10)) + 1}줄, {len(raw)}자")

    for kind, ln, msg in check_text(raw):
        (err if kind == "E" else warn)(f"{ln}줄: {msg}")

    for bad, why in [("<!DOCTYPE", "조각에 DOCTYPE을 쓰지 않는다"),
                     ("<html", "조각에 <html>을 쓰지 않는다"),
                     ("<body", "조각에 <body>를 쓰지 않는다"),
                     ("<thead", "<thead>는 저장 시 사라진다. <tr><th>만 쓴다"),
                     ("<style", "<style>은 무시된다")]:
        m = re.search(re.escape(bad), raw, re.IGNORECASE)
        if m:
            err(f"{lineno(raw, m.start())}줄: {why}")

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
        if tag == f"{{{NS['ac']}}}structured-macro":
            name = el.get(f"{{{NS['ac']}}}name", "")
            if name in CONFIRMED:
                pass
            elif name in BUNDLED:
                warn(f"매크로 `{name}`: DC 기본이지만 사내 설치 미확인 (ANSWER.md A4)")
            else:
                err(f"매크로 `{name}`: 확인되지 않은 매크로다. 쓰지 않는다")
            if name == "code":
                lang = el.find(f"{{{NS['ac']}}}parameter[@{{{NS['ac']}}}name='language']")
                if lang is not None and (lang.text or "") not in ("c", "text", ""):
                    warn(f"code language=`{lang.text}`: `c` 외에는 목록 미확인 "
                         f"(ANSWER.md A3). 확실치 않으면 text")
        if tag in ("ul", "ol") and parent.get(el) is not None \
                and parent[el].tag in ("ul", "ol"):
            err("중첩 목록이 <li> 밖에 있다. 부모 <li> 안으로 넣는다")
        if tag == f"{{{NS['ri']}}}attachment":
            images.append(el.get(f"{{{NS['ri']}}}filename", "?"))

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
        print(f"\n{len(errors)}건 — 고치기 전에는 Edit Source에 넣지 않는다")
        sys.exit(1)
    print("\nOK" + (f" (WARN {len(warns)}건)" if warns else ""))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: check.py <file.xhtml>")
    main(sys.argv[1])
