#!/usr/bin/env python3
"""한장 정리 HTML → Confluence storage format 조각.

입력은 one-page-summary 템플릿으로 만든 HTML 이다(<head> 의 :root 색 변수, <main> 안의
header/section/figure/details/footer). 글·목록·표·상자는 Confluence 본문 요소로 옮기고,
원본 CSS 는 이 페이지 본문(#main-content)에만 걸리는 <style> 하나로, SVG 도식은 각각
html 매크로로 옮긴다. reference/html-input.md 참조.

모르는 요소를 만나면 멈춘다 — 손으로 옮길 자리를 알려 주는 것이지 실패가 아니다.

usage: html2storage.py [--no-webfont] [--source "<원본 설명>"] <in.html> <out.xhtml>
"""
import argparse
import html
import re
import sys
import xml.etree.ElementTree as ET

ap = argparse.ArgumentParser()
ap.add_argument("--no-webfont", dest="webfont", action="store_false",
                help="Google Fonts 를 불러오는 <link> 를 빼고 대체 글꼴로 낸다(외부 리소스를 막아야 할 때)")
ap.add_argument("--source", default="", help="footer 끝에 붙일 원본 설명(저장소, commit)")
ap.add_argument("src")
ap.add_argument("out")
opt = ap.parse_args()

src = open(opt.src, encoding="utf-8").read()
m = re.search(r":root\s*\{(.*?)\}", src, re.S)
if not m:
    sys.exit(f"{opt.src}: :root 색 변수가 없다 — 한장 정리 템플릿이 아니다. 손으로 옮긴다")
COL = dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{3,8})", m.group(1)))
need = {"bg", "surface", "fg", "muted", "line", "accent", "accent-soft", "good", "good-soft",
        "wait", "wait-soft"}
if need - COL.keys():
    sys.exit(f"{opt.src}: 색 변수 {sorted(need - COL.keys())} 가 없다 — 템플릿이 다르다")
MUTED, LINE, ACCENT = COL["muted"], COL["line"], COL["accent"]

BODY = '"IBM Plex Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif'
MONO = '"IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace'
# style 속성 안에 넣을 때는 작은따옴표로 — 큰따옴표면 속성이 거기서 끊긴다
BODY_A, MONO_A = BODY.replace('"', "'"), MONO.replace('"', "'")

# 본문 폭. 760px 은 좁았고 912·1064 를 거쳐 사용자가 988px 을 골랐다(2026-11-13, page 4141483804 v6).
# 그림 상자도 같은 폭으로 맞춘다.
WIDTH = "988px"

WEBFONT = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:'
           'wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">\n')

# 원본 CSS 를 Confluence 가 그리는 DOM 에 옮긴 것. 모든 규칙이 #main-content 로 시작한다 —
# check.py --html-input 이 이것을 본다. html 매크로가 막히면 이 블록만 빠지고 글은 남는다.
# 문단·목록에 줄 길이 제한(max-width:65ch)을 두지 않는다 — 두면 본문 폭을 늘려도 글 폭이 그대로다.
STYLE = """<style>
#main-content{max-width:%(width)s;margin:0 auto;color:%(fg)s;font-family:%(body)s;font-size:16px;line-height:1.7}
#main-content p,#main-content li{font-family:%(body)s;font-size:16px;line-height:1.7}
#main-content p{margin:0 0 14px}
#main-content h2{font-family:%(body)s;font-size:1.3rem;font-weight:700;line-height:1.3;color:%(fg)s;margin:40px 0 14px;padding-bottom:6px;border-bottom:1px solid %(line)s}
#main-content h3{font-family:%(body)s;font-size:1.05rem;font-weight:700;line-height:1.3;color:%(fg)s;margin:0 0 8px}
#main-content ul,#main-content ol{margin:0 0 14px;padding-left:1.3em}
#main-content li{margin:0 0 6px}
#main-content li>ul,#main-content li>ol{margin:6px 0 0}
#main-content li::marker{color:%(muted)s}
#main-content strong{font-weight:700}
#main-content code{font-family:%(mono)s;font-size:.88em;color:inherit;background:%(accent_soft)s;border:0;padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
#main-content .table-wrap{border:1px solid %(line)s;border-radius:6px;background:%(surface)s;overflow-x:auto;margin:0 0 14px}
#main-content table.confluenceTable{border-collapse:collapse;width:100%%;margin:0;font-size:.92rem;font-variant-numeric:tabular-nums}
#main-content th.confluenceTh,#main-content td.confluenceTd{border:0;border-bottom:1px solid %(line)s;padding:9px 12px;text-align:left;vertical-align:top;font-size:inherit}
#main-content th.confluenceTh{font-weight:500;color:%(muted)s;font-size:.82rem;background:%(bg)s}
#main-content tr:last-child>td.confluenceTd{border-bottom:0}
#main-content .panel{border-radius:6px;margin:0 0 14px;max-width:none}
#main-content .panelContent{padding:14px 16px}
#main-content .panel[style*="%(accent)s"]{border-color:%(line)s !important;border-left:4px solid %(accent)s !important}
#main-content .panel[style*="%(accent)s"] .panelContent{padding:16px 18px}
#main-content .panel ul{margin-bottom:0;max-width:none}
#main-content .status-macro.aui-lozenge{text-transform:none;font-size:.78rem;font-weight:500;line-height:1.5;padding:2px 10px;border-radius:999px;border:1px solid transparent;background:%(bg)s;color:%(muted)s}
#main-content .status-macro.aui-lozenge-subtle{border-color:%(line)s;background:%(bg)s;color:%(muted)s}
#main-content .status-macro.aui-lozenge-success{background:%(good_soft)s;color:%(good)s}
#main-content .status-macro.aui-lozenge-complete{background:%(accent)s;color:%(surface)s;font-weight:700}
#main-content .status-macro.aui-lozenge-current{background:%(wait_soft)s;color:%(wait)s}
#main-content .status-macro.aui-lozenge-error{background:%(bad_soft)s;color:%(bad)s}
#main-content .expand-container{background:%(surface)s;border:1px solid %(line)s;border-radius:6px;padding:12px 16px;margin:0 0 14px}
#main-content .expand-control-text{font-weight:700;color:%(fg)s}
#main-content hr{border:0;border-top:1px solid %(line)s;margin:40px 0 14px}
</style>"""

# 칩·진행 띠 class → status colour. CSS 가 aui-lozenge-* 를 원본 색으로 다시 칠한다.
CHIP = {"good": "Green", "done": "Green", "wait": "Yellow", "todo": "Grey", "bad": "Red",
        "now": "Blue"}

SVGS = re.findall(r"<svg.*?</svg>", src, re.S)


def esc(s):
    return html.escape(s or "", quote=False)


# 본문 span 의 font-size 는 px 로 쓴다. `.78rem` `.86rem` 은 저장할 때 Confluence 가 지웠고 px 는
# 남았다(2026-11-13). html 매크로(CDATA) 안은 저장 때 건드리지 않으므로 rem 을 써도 된다.
def muted(inner, size):
    return f'<span style="color:{MUTED};font-size:{size};">{inner}</span>'


def status(colour, title, subtle=False):
    sub = '<ac:parameter ac:name="subtle">true</ac:parameter>' if subtle else ""
    return (f'<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">{colour}</ac:parameter>'
            f'<ac:parameter ac:name="title">{esc(title)}</ac:parameter>{sub}</ac:structured-macro>')


def panel(body, border, bg):
    return ('<ac:structured-macro ac:name="panel">'
            '<ac:parameter ac:name="borderStyle">solid</ac:parameter>'
            f'<ac:parameter ac:name="borderColor">{border}</ac:parameter>'
            '<ac:parameter ac:name="borderWidth">1</ac:parameter>'
            f'<ac:parameter ac:name="bgColor">{bg}</ac:parameter>'
            f'<ac:rich-text-body>{body}</ac:rich-text-body></ac:structured-macro>')


def html_macro(body):
    assert "]]>" not in body
    return ('<ac:structured-macro ac:name="html"><ac:plain-text-body><![CDATA['
            + body + ']]></ac:plain-text-body></ac:structured-macro>')


def style_macro():
    v = {k.replace("-", "_"): c for k, c in COL.items()}
    v.setdefault("bad", "#b3261e")
    v.setdefault("bad_soft", "#fbe9e7")
    v.update(body=BODY, mono=MONO, width=WIDTH)
    return html_macro((WEBFONT if opt.webfont else "") + STYLE % v)


def figure_macro(svg, caption):
    for name, value in COL.items():
        svg = svg.replace(f"var(--{name})", value)
    svg = svg.replace(' text-anchor="start"', "").replace(' font-weight="400"', "")
    left = sorted(set(re.findall(r"var\(--[a-z-]+\)", svg)))
    if left:
        sys.exit(f"SVG 에 풀리지 않은 색 변수가 있다: {left}")
    return html_macro(
        f'<div style="max-width:{WIDTH};box-sizing:border-box;border:1px solid {LINE};border-radius:6px;'
        f'padding:16px;background:{COL["surface"]};overflow-x:auto"><div style="min-width:560px">{svg}</div>'
        f'<div style="font-family:{BODY_A};font-size:.88rem;line-height:1.7;color:{MUTED};margin-top:10px">'
        f'{caption}</div></div>')


SIMPLE = {"em": "em", "i": "em", "b": "strong", "sub": "sub", "sup": "sup", "s": "s"}


def inline(el, strong_colour=None):
    out = esc(el.text)
    for c in el:
        cls = c.get("class", "")
        if (c.tag == "span" and cls == "label") or c.tag == "strong":
            body = inline(c)
            if strong_colour:
                body = f'<span style="color:{strong_colour};">{body}</span>'
            out += f"<strong>{body}</strong>"
        elif c.tag == "code" or (c.tag == "span" and cls == "mono"):
            out += f"<code>{inline(c)}</code>"
        elif c.tag == "span" and cls.startswith("chip"):
            out += status(CHIP[cls.split()[1]], "".join(c.itertext()))
        elif c.tag == "a":
            out += f'<a href="{html.escape(c.get("href", ""), quote=True)}">{inline(c)}</a>'
        elif c.tag == "br":
            out += "<br/>"
        elif c.tag in SIMPLE:
            out += f"<{SIMPLE[c.tag]}>{inline(c)}</{SIMPLE[c.tag]}>"
        elif c.tag in ("ul", "ol"):
            pass                                # li 안의 목록은 list_block 이 붙인다
        else:
            sys.exit(f"인라인 <{c.tag} class={cls!r}> 를 모른다 — 이 자리는 손으로 옮긴다")
        out += esc(c.tail)
    return out


def list_block(el, strong_colour=None):
    items = []
    for li in el:
        body = inline(li, strong_colour).rstrip()
        for c in li:
            if c.tag in ("ul", "ol"):
                body += list_block(c, strong_colour)
        items.append(f"<li>{body}</li>")
    return f"<{el.tag}>" + "".join(items) + f"</{el.tag}>"


def table_block(tbl):
    rows = []
    for tr in tbl.iter("tr"):
        cells = []
        for c in tr:
            tag = "th" if c.tag == "th" else "td"
            span = "".join(f' {a}="{c.get(a)}"' for a in ("colspan", "rowspan") if c.get(a))
            cells.append(f"<{tag}{span}>{inline(c)}</{tag}>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return "<table><tbody>" + "".join(rows) + "</tbody></table>"


def steps_block(ol):
    rows = []
    for li in ol:
        n = li.find("span[@class='n']")
        t = li.find("span[@class='t']")
        chip = [x for x in li if "chip" in x.get("class", "")]
        small = t.find("small") if t is not None else None
        if n is None or t is None or not chip:
            sys.exit("ol.steps 항목 모양이 다르다(n·t·chip) — 손으로 옮긴다")
        desc = f"<br/>{muted(inline(small), '13.8px')}" if small is not None else ""
        kind = chip[0].get("class").split()[1]
        rows.append(f"<tr><td>{esc(n.text)}</td><td><strong>{esc(t.text)}</strong>{desc}</td>"
                    f"<td>{status(CHIP[kind], chip[0].text)}</td></tr>")
    return "<table><tbody>" + "".join(rows) + "</tbody></table>"


fig_no = 0


def block(el):
    global fig_no
    cls = el.get("class", "")
    if el.tag in ("h2", "h3", "h4"):
        return f"<{el.tag}>{inline(el)}</{el.tag}>"
    if el.tag == "p":
        body = inline(el)
        return f"<p>{muted(body, '14.4px') if 'note' in cls else body}</p>"
    if el.tag in ("ul", "ol") and "steps" in cls:
        return steps_block(el)
    if el.tag in ("ul", "ol"):
        return list_block(el)
    if el.tag == "div" and "box" in cls:
        return panel("".join(block(c) for c in el), LINE, COL["surface"])
    if el.tag == "div" and "tbl" in cls:
        return table_block(el.find("table"))
    if el.tag == "table":
        return table_block(el)
    if el.tag == "figure":
        if el.find(".//svg") is None:
            sys.exit("SVG 없는 <figure> 를 모른다 — 손으로 옮긴다")
        cap = el.find("figcaption")
        out = figure_macro(SVGS[fig_no], inline(cap) if cap is not None else "")
        fig_no += 1
        return out
    if el.tag == "section":
        return "".join(block(c) for c in el)
    if el.tag == "details":
        title = "".join(el.find("summary").itertext())
        body = "".join(block(c) for c in el if c.tag != "summary")
        return ('<ac:structured-macro ac:name="expand">'
                f'<ac:parameter ac:name="title">{esc(title)}</ac:parameter>'
                f'<ac:rich-text-body>{body}</ac:rich-text-body></ac:structured-macro>')
    sys.exit(f"블록 <{el.tag} class={cls!r}> 를 모른다 — 이 자리는 손으로 옮긴다")


def header_block(h):
    out = []
    eyebrow = h.find("span[@class='eyebrow']")
    if eyebrow is not None:
        out.append(f'<p><span style="color:{MUTED};font-family:{MONO_A};font-size:12.5px;'
                   f'letter-spacing:0.06em;text-transform:uppercase;">{esc(eyebrow.text)}</span></p>')
    verdict = h.find("div[@class='verdict']")
    if verdict is not None:
        # 테두리색 accent 가 CSS 의 갈고리다: 왼쪽 4px 선으로 바꿔 그린다
        out.append(panel("".join(list_block(c, ACCENT) if c.tag in ("ul", "ol") else block(c)
                                 for c in verdict), ACCENT, COL["surface"]))
    track = h.find("ol[@class='track']")
    if track is not None:
        chips = []
        for li in track:
            kind = li.get("class", "")
            chips.append(status(CHIP[kind], li.text) if kind else status("Grey", li.text, True))
        out.append("<p>" + " ".join(chips) + "</p>")
    return "".join(out)


main = ET.fromstring(re.search(r"<main>.*</main>", src, re.S).group(0))
title = ""
parts = [style_macro()]
for el in main:
    if el.tag == "header":
        h1 = el.find("h1")
        title = "".join(h1.itertext()).strip() if h1 is not None else ""
        parts.append(header_block(el))
    elif el.tag == "footer":
        tail = f" · {esc(opt.source)}" if opt.source else ""
        parts.append("<hr/>" + f"<p>{muted(inline(el).strip() + tail, '13.6px')}</p>")
    else:
        parts.append(block(el))
if fig_no != len(SVGS):
    sys.exit(f"SVG {len(SVGS)}개 가운데 {fig_no}개만 figure 로 옮겼다 — 남은 것을 손으로 본다")
open(opt.out, "w", encoding="utf-8").write("\n".join(parts) + "\n")
print(f"{opt.out}: 도식 {fig_no}개, 원본 제목: {title}")
