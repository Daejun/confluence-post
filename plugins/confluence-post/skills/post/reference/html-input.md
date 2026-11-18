# HTML 입력 — 한장 정리를 원본처럼 보이게 옮기기

입력이 markdown 이 아니라 **HTML 파일**일 때 쓰는 경로다. 특히 one-page-summary
템플릿으로 만든 한장 정리 — `<head>` 의 `:root` 색 변수, `<main>` 안의 header·section·
figure·details·footer — 는 `scripts/html2storage.py` 가 그대로 옮긴다.

## 무엇을 내는가

세 겹으로 나눠 옮긴다.

| 겹 | 옮기는 곳 | html 매크로가 막히면 |
|---|---|---|
| 글·목록·표·상자·칩·접기 | Confluence 본문 요소 (`p` `ul` `table` `panel` `status` `expand`) | 그대로 남는다. Confluence 기본 모양이 된다 |
| 글꼴·크기·폭·표와 칩의 모양 | 맨 앞의 `html` 매크로 하나에 든 `<style>`. 모든 규칙이 `#main-content` 로 시작한다 | 이 블록만 빠진다 |
| SVG 도식 | 도식마다 `html` 매크로 하나. CSS 색 변수는 실제 색으로 바꾼다 | 도식만 빈다 |

글은 Confluence 본문이라 검색되고 에디터로 고칠 수 있다. 겉모습만 HTML 로 얹는다.

## 왜 이 방식인가

같은 한장 정리(AnTuTu storage 분석)를 네 가지로 올려 보고 정한 것이다.

| 시도 | 결과 |
|---|---|
| 본문만, 도식은 PlantUML | 원본보다 가독성이 많이 떨어졌다 (2026-11-11) |
| 원본 HTML 전체를 `html` 매크로의 `<iframe srcdoc>` 에 | 원본과 똑같이 보였다 (2026-11-12, page 4125637690 v3). 하지만 iframe 안 글은 검색되지 않고, 에디터로 고칠 수 없고, 매크로가 막히면 페이지가 통째로 빈다 |
| 본문 + 도식만 `html` 매크로 | 구성은 같았지만 글꼴·글씨 크기·폭이 달랐다 (2026-11-13, page 4141483543 v1) |
| 본문 + 도식 `html` + 페이지 범위 `<style>` | **사용자가 가장 낫다고 했다** (2026-11-13, page 4141483543 v2). 채택 |

폭과 글씨는 다음 페이지(점수 계산, page 4141483804)에서 맞췄다.

| 시도 | 결과 |
|---|---|
| 본문 폭 760px | 좁다고 했다. 912px, 1064px 로 넓혔다 |
| 폭만 넓힘 | 페이지는 넓어졌는데 글 폭은 그대로였다 — 문단·목록의 `max-width:65ch` 때문. 뺐다 |
| 맑은 고딕 | 원래 글꼴(IBM Plex)로 되돌려 달라고 했다 |
| 1064px → **988px**, IBM Plex 웹폰트, 본문 span 글씨 크기 px | **사용자가 좋다고 했다** (2026-11-13, v6). 지금 기본값 |

iframe 방식은 "원본과 글자 하나까지 같아야 하고 검색은 필요 없다"고 할 때만 쓴다. 그때는
원본 HTML 을 `<script type="text/plain">` 에 넣고 script 로 `iframe.srcdoc` 에 옮긴다 —
`srcdoc` 속성에 직접 넣으면 따옴표를 모두 `&quot;` 로 바꿔야 해 크기가 크게 는다.
check.py `--html-input` 은 script·iframe 을 막으므로 이 경우는 `--html-input` 없이 검사하고
`html` 매크로 WARN 을 초안에 적는다.

## 확인된 것과 안 된 것

- **`html` 매크로는 이 인스턴스에서 렌더링된다.** `<style>`, inline SVG, `<script>`,
  `<iframe srcdoc>` 가 모두 동작했다 (2026-11-12, 사용자가 화면 확인).
- **페이지 범위 `<style>` 은 본문 요소에도 걸린다.** `html` 매크로가 내놓은 `<style>` 은
  문서 전체에 적용되므로, `#main-content` 로 범위를 좁혀 본문만 꾸민다.
- `panel` 의 `borderStyle` `borderColor` `borderWidth` `bgColor`, `status` 의 `subtle` 은
  저장되고 그려진다 (2026-11-13).
- **본문 span 의 inline `font-size` 는 `.78rem` `.86rem` `.9rem` `.85rem` 이 저장할 때 지워졌다.**
  색은 `rgb(…)` 로 바뀌어 남았고, `12.5px` `13.8px` 같은 px 값과 `letter-spacing:0.06em` 은
  남았다 (2026-11-13). rem 단위 때문인지 앞의 0 이 없어서인지는 떼어 보지 않았다 — px 로 쓴다.
  html 매크로(CDATA) 안은 저장 때 건드리지 않는다.
- CSS 가 기대는 Confluence DOM class 이름은 아래와 같다. Confluence DC 의 일반적인 이름이고,
  페이지 전체가 원본처럼 보이는 것은 사용자가 확인했다. **규칙 하나하나를 따로 확인하지는
  않았다** — 어느 부분이 원본과 다르면 그 요소의 class 를 개발자 도구로 받아 고친다.

| 원본 | Confluence 가 그리는 것 | CSS 갈고리 |
|---|---|---|
| 본문 영역 | 본문 컨테이너 | `#main-content` |
| `.tbl` 감싼 표 | `div.table-wrap > table.confluenceTable` | `.table-wrap`, `th.confluenceTh`, `td.confluenceTd` |
| `.box`, `.verdict` | `div.panel > div.panelContent` | `.panel`, `.panelContent` |
| `.verdict` 의 왼쪽 굵은 선 | 테두리색이 accent 인 panel | `.panel[style*="<accent>"]` — panel 의 inline style 에 테두리색이 들어간다 |
| `.chip`, `.track li` | `span.status-macro.aui-lozenge` | `.aui-lozenge-success`(Green) `-current`(Yellow) `-complete`(Blue) `-error`(Red) `-subtle`, 회색은 수식어 없음 |
| `details` | expand 매크로 | `.expand-container`, `.expand-control-text` |

## 사내 매뉴얼과 맞추는 규칙

사내 매뉴얼은 `html` 매크로에서 외부 리소스와 과한 CSS 를 비권장하고, 사이드바에는 넣지
말라고 한다. 그래서 이 경로에서도 아래를 지킨다. check.py `--html-input` 이 본다.

- CSS 선택자는 모두 `#main-content` 로 시작한다. Confluence 메뉴·사이드바에 걸리지 않게 한다.
- `<style>` 매크로는 페이지에 하나, 맨 앞에 둔다.
- 외부 리소스는 웹폰트(IBM Plex, Google Fonts) 하나만 넣는다. 사용자가 원본 글꼴을 골랐다
  (2026-11-13). check.py 가 WARN 으로 알리고, 막히면 대체 글꼴(Apple SD Gothic Neo, Malgun
  Gothic)로 나온다. 외부 리소스를 막아야 하는 곳이면 `html2storage.py --no-webfont`.
  글꼴 파일을 첨부해 직접 두는 방식은 쓰지 않는다 — 번거롭고, IBM Plex 는 OFL 의 Reserved Font
  Name 이라 고친(subset 등) 파일을 같은 이름으로 배포할 수 없다.
- `<script>` `<iframe>` `<form>` 을 넣지 않는다. 도식 매크로에는 SVG 와 그 설명만 둔다.
- 사이드바·템플릿·다른 페이지에 넣지 않는다. 이 페이지 본문에만 둔다.

## 순서

SKILL.md 의 순서를 따르되 3·5단계가 이렇게 바뀐다.

1. **템플릿인지 본다.** `<head>` 에 `:root { --bg … --accent … }` 가 있고 `<main>` 안이
   header·section·details·footer 면 템플릿이다.
2. **변환한다.**
   ```bash
   S=$(dirname "$(find -L ~/.claude -path '*/skills/post/scripts/html2storage.py' 2>/dev/null | head -1)")
   python3 -I "$S/html2storage.py" --source "원본: <저장소> <경로>, commit <sha>" in.html out/<slug>.xhtml
   ```
   스크립트가 모르는 요소에서 멈추면, 그 요소만 아래 대응표대로 손으로 옮기거나 스크립트에
   한 갈래를 더한다. 멈춘 자리를 건너뛰지 않는다.
   템플릿이 아니면 대응표와 `STYLE`(스크립트 안의 CSS)을 보고 손으로 옮긴다. 원본 CSS 의
   선택자를 위 DOM 갈고리로 바꾸고 `#main-content` 를 앞에 붙인다.
3. **검사한다.** `check.py --html-input --source-html <원본.html> out/<slug>.xhtml`.
   끝에 찍히는 "style 1개, 도식 N개"를 원본과 대조한다. `--source-html` 을 주면 그 대조를
   검사기가 한다 — style 을 옮기지 않았거나 도식 수가 다르면 ERROR 다.
4. **원문과 대조한다**(SKILL.md 6단계). h2 수, 표 수와 행 수, 목록 항목 수를 원본과 센다.
   스크립트는 글을 고치지 않으므로 문장은 같아야 한다.
5. 초안 승인과 게시는 SKILL.md 8·9단계 그대로다. 게시한 뒤 화면에서 볼 곳을 알려 준다 —
   판정 상자의 왼쪽 선, 칩 모양, 표 테두리, 도식 크기.

## 대응표

| 원본 | storage format |
|---|---|
| `header .eyebrow` | `<p><span style="…mono, 12.5px, uppercase…">` |
| `header h1` | 쓰지 않는다 — 페이지 제목이 가져간다. 스크립트가 원본 제목을 찍어 준다 |
| `.verdict` | `panel` (borderColor = accent, bgColor = surface). 굵은 글씨는 accent 색 span |
| `.track li.done / .now / .wait / (없음)` | 한 문단에 `status` Green / Blue / Yellow / Grey+subtle |
| `section > h2`, `h3` | `h2`, `h3` |
| `.box` | `panel` (borderColor = line, bgColor = surface) |
| `span.label`, `strong` | `<strong>` |
| `code`, `span.mono` | `<code>` |
| `span.chip.good / .wait / .todo / .bad` | `status` Green / Yellow / Grey / Red |
| `.tbl > table` (`thead` 포함) | `<table><tbody>` 안 `<tr><th>`. `colspan` `rowspan` 은 그대로 |
| `p.note` | `<p><span style="color:muted;font-size:14.4px">` |
| `figure` (SVG + figcaption) | `html` 매크로 하나: 테두리 상자 + SVG(색 변수를 실제 색으로) + 설명 |
| `ol.steps` (n·t·small·chip) | 3열 표: 번호 / 제목 + 회색 설명(13.8px) / `status` |
| `details > summary` | `expand` (title = summary) |
| `footer` | `<hr/>` + 회색 작은 글씨 문단(13.6px). `--source` 를 끝에 붙인다 |
| `a` | `<a href>` |

## 가장 틀리기 쉬운 자리

- **본문만 다시 쓰고 통과하는 함정.** HTML 입력을 native 매크로(info·expand·status·table)로
  다시 쓴 조각은 `--html-input` 만으로는 `style 0개, 도식 0개`로 OK 가 나온다. 원본의
  겉모습과 도식이 사라졌는데도 그렇다. 2026-11-18에 한장 정리를 이렇게 올렸다가 사용자가
  되돌리게 했다. **`--source-html` 을 빼지 않는다.** 없이 돌렸다면 "html 매크로가 하나도
  없다" WARN 을 그냥 넘기지 않는다.
- **선례를 먼저 본다.** 새 페이지라도 같은 space 에 같은 종류(한장 정리)의 page 가 있으면
  `get_page(convert_to_markdown=false)` 로 storage 를 한 번 연다. 원하는 모습이 이미 어떤
  형식으로 저장돼 있는지가 한 번의 호출로 보인다. 형식이 갈리면 사용자에게 묻기 전에
  선례를 따른다.
- **"확인 안 된 것"을 피하지 않는다.** SKILL.md 의 "아직 확인 안 된 것"에 걸리는 매크로나
  동작을 만나면 쓰지 않는 쪽으로 피하기 전에, 한 번 재 본다(저장 후 다시 읽어
  `ac:structured-macro` 인지 `ac:macro` 인지). 피한 결정은 초안에 이유와 함께 적는다.
- **style 속성 안의 큰따옴표.** `style="font-family:"IBM Plex Sans KR", …"` 는 속성이 첫
  `"` 에서 끊기고, 브라우저는 오류 없이 그 스타일을 버린다. 실제로 그림 설명 글꼴이 이렇게
  한 번 깨졌다. 속성 안의 글꼴 이름은 작은따옴표로 쓴다. check.py `--html-input` 이 잡는다.
- **본문 span 의 글씨 크기는 px.** rem 으로 쓰면 저장할 때 크기만 지워지고 색은 남아, 작은 회색
  글씨가 본문 크기로 나온다. 표 칸 안에서 줄이 엉뚱하게 바뀐다. check.py 가 px 가 아닌 본문
  `font-size` 를 ERROR 로 막는다. 원본 CSS 의 rem 은 16 을 곱해 px 로 바꾼다.
- **줄 길이 제한.** 원본의 `max-width:65ch` 같은 글 폭 제한을 문단·목록에 옮기면, 본문 폭을
  늘려도 글이 그 폭에서 줄바꿈한다. 옮기지 않는다. 폭은 `#main-content` 하나로 정한다.
- **CSS 색 변수.** 원본 SVG 의 `fill="var(--accent)"` 는 Confluence 에 그 변수가 없어
  검게 나온다. 실제 색으로 바꾼다. 원본의 밝은 화면 `:root` 값을 쓴다.
- **다크 모드.** 원본 CSS 의 `prefers-color-scheme: dark` 규칙은 옮기지 않는다. Confluence
  본문은 밝은 화면이다.
- **크기.** MCP `create_page`/`update_page` 는 본문을 한 번에 보내야 한다. 도식 4개짜리
  한장 정리가 4.8만 자로 들어갔다. SVG 가 크면 그보다 커질 수 있으니 문자 수를 먼저 본다.
- **CDATA 안에 `]]>`.** SVG·CSS 에 그 세 글자가 있으면 매크로가 끊긴다. 스크립트가 막는다.
- **에디터로 고칠 때.** 글은 에디터로 고쳐도 되지만 맨 앞의 style 매크로와 도식 매크로는
  지우지 않는다. 원본이 바뀌었으면 스크립트를 다시 돌려 `update_page` 로 덮어쓴다 —
  덮어쓰기 전에 `version` 을 다시 보는 규칙(`reference/existing-page.md`)은 그대로다.
