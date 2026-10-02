# P1~P3 렌더링 응답표

사내 PC 안에서 붙여넣기가 되므로, 메뉴를 읽는 대신 **직접 렌더링해서** 확인한다.
세 페이지로 나눴다 — 하나가 저장을 거부해도 나머지는 살아남는다.

각 페이지를 개인 space에 새로 만들고 Edit Source에 파일 내용을 붙여넣고 저장한다.
**항목 라벨(L01, M01, S01)이 화면에 그대로 나오므로 화면 캡처만 주셔도 됩니다.**

---

# 결과 (2026-08-28)

## P1 — code 언어: 시험한 22종 전부 하이라이팅됨

`c` `cpp` `diff` `bash` `shell` `text` `none` `python` `py` `java` `js`
`javascript` `json` `yaml` `xml` `sql` `rust` `go` `perl` `powershell`
`makefile` `ruby`. `title` `linenumbers` `collapse` 도 동작.

미확인: 대조군 L00(`zzznotalang`)이 어떻게 보였는지. 대조군도 색이 났다면 위 중
일부는 기본 brush로 떨어진 것일 수 있다. 결과는 색이 안 나는 것뿐이라 위험은 낮다.

## P2 — 매크로

**쓸 수 있다**: `code` `expand` `info` `note` `warning` `tip` `panel` `toc`
`status` `noformat` `anchor` `plantuml` `latex` `attachments` `recently-updated`

**쓸 수 없다**: `mermaid` `mermaid-cloud` `mathblock` `gliffy` `excerpt` `children`

**조건부**
- `drawio` — "알 수 없는 매크로"가 아니라 **오류**가 났다. 즉 설치돼 있고,
  probe가 없는 다이어그램 이름(`test`)을 가리켜 난 오류다. 다만 에디터에서 그려야
  하므로 XHTML로 저작할 수 없다.
- `jira` — 매크로는 있다. 실제 이슈 키로만 렌더링된다.

`excerpt`·`children`은 보여줄 내용이 없어 비어 보인 것일 수도 있다. 스킬에서 안 쓰므로
구분하지 않았다.

## P3 — 구조: 전 항목 정상

3단 중첩 목록, 8열 표(안 잘림), 표 셀 안 code·expand, 긴 코드 한 줄,
code 파라미터 3종, 링크 4종, 첨부 없는 이미지, blockquote·hr, 인라인 서식,
본문·CDATA 이스케이프, h2~h5, 긴 한글 문단.

## 이 결과가 스킬에 반영된 곳

- `plugins/confluence-post/skills/post/SKILL.md` — 확정된 환경, 도식 정책
- `plugins/confluence-post/skills/post/reference/storage-format.md` — 언어 목록, PlantUML
- `plugins/confluence-post/skills/post/scripts/check.py` — CONFIRMED / UNAVAILABLE / TESTED_LANGS

---

# P4 — PlantUML (`probe/P4-plantuml.xhtml`)

사내 서버가 1.2024.8 이라고 들었다. 무엇이 실제로 그려지는지 확인한다.
개인 space에 새 페이지를 만들어 Edit Source에 붙여넣고 저장한다.

**V01 이 가장 중요하다** — PlantUML 이 스스로 버전과 환경을 그림으로 찍는다.
거기 나온 문자열을 그대로 적어 주세요. 1.2024.8 이 맞는지, JVM·폰트 정보가 무엇인지가
한 번에 나온다.

V11 은 대조군이다. 실패해야 정상이고, 실패 화면이 "렌더링 실패"가 어떻게 보이는지를 알려준다.

```
V01 version — 찍힌 문자열 그대로 =
V02 sequence =   V03 activity(새 문법) =   V04 class =   V05 component =   V06 state =
V07 한글 라벨 — 글자로 나옴 / 네모로 나옴 =
V08 title·note·legend =   V09 skinparam =   V10 !theme plain =
V11 !include stdlib(대조군, 실패해야 정상) =
V12 mindmap =   V13 json =   V14 gantt =   V15 salt =   V16 전처리기 변수 =
V17 listfonts — 폰트 목록이 나오면 한글 폰트가 있는지 =
```

## 이 결과로 푸는 것

- V07 이 글자로 나오면 도식에 한글 라벨을 쓴다. 네모면 영문 라벨로 고정한다.
- V12~V15 중 되는 것을 `check.py` 의 `PUML_ALLOWED` 에 넣는다.
- V10 이 되면 `!theme` 금지를 푼다.
- V11 이 되면(예상 밖) `!include` 금지를 완화한다.

---

# P5 — MCP 로 올려 확인 (`probe/P5-mcp.xhtml`, 2026-10-02)

Confluence MCP 의 `create_page` 로 테스트 페이지를 만들고, `get_page` 로 저장된 원문을
다시 읽은 뒤 브라우저에서 렌더링을 봤다.

## 다시 읽은 원문 — 렌더링 없이 아는 것

| 저장 후 형태 | 매크로 |
|---|---|
| `ac:structured-macro` 유지 + `ac:macro-id`·`ac:schema-version` 추가 | code, excerpt, children(schema 2), pagetree, include, details, section, column, chart, table-filter, drawio, plantuml |
| 옛 형식 `<ac:macro>` 로 바뀜 | mermaid, mathblock (plain-text 본문 삭제), gliffy, `zzznotamacro`(대조군) |

- 설치 안 된 매크로는 저장하는 순간 `<ac:macro>` 가 되고 plain-text 본문이 지워진다.
- drawio 는 `revision=1`, table-filter 는 `id` 파라미터가 저장 때 붙었다 — 플러그인이 살아 있다.
- plantuml 에 `atlassian-macro-output-type` 은 붙지 않았다. `INLINE` 은 에디터가 붙이는 값이다.
- code 의 language 는 검증하지 않는다. 없는 언어도 그대로 저장된다.
- `colspan` `rowspan` `<thead>` `ac:task-list` h6 은 그대로 저장됐다. `ac:task-id` 는 붙지 않았다.

## 브라우저 렌더링

- **P1~P4 PlantUML** — 최상위, `<p>` 감쌈, `BLOCK`, `INLINE` 네 가지 모두 위아래 문장과
  다른 줄에 나왔다. 붙어 나오는 현상은 재현되지 않았다.
- **L01~L04 code** — `cpp` `c++` language 없음은 칠해졌고, 없는 언어(L03)만 회색이었다.
  P1 대조군 미확인이 풀렸다: 확인된 22종은 진짜로 칠해진 것이다.
- **M07~M13** — excerpt, children, pagetree, include, details, section/column, chart 정상.
- **S01~S05** — colspan, rowspan, thead, h6 정상. 체크박스는 보이지만 누르면 "저장할 수
  없다" 오류.
- **S04b** — `<ac:task-id>` 를 넣은 체크박스는 눌러서 저장된다. markdown 체크박스를
  이것으로 바꾼다.

## 이 결과가 반영된 곳

- `plugins/confluence-post/skills/post/SKILL.md` — 확정된 환경, 설치 여부 확인법
- `plugins/confluence-post/skills/post/reference/storage-format.md` — 언어 23종, 표 병합,
  그 밖의 매크로, 체크박스
- `plugins/confluence-post/skills/post/reference/plantuml.md` — `<p>` 감싸기의 근거
- `plugins/confluence-post/skills/post/reference/existing-page.md` — 게시 후 `<ac:macro>` 확인
- `plugins/confluence-post/skills/post/scripts/check.py` — CONFIRMED, TESTED_LANGS,
  `<ac:macro>`·`task-id` 없는 체크박스·language 없는 code

---

# P6 — 커스텀 매크로 설치 확인 (2026-10-02) — 다시 하지 않는다

실제 페이지에서 쓰이는 매크로 이름을 모아, 확인 안 된 것 35종을 한 페이지에 넣고 MCP 로
올린 뒤 다시 읽었다. **이 페이지는 열리지 않았다.** 범위 없이 넣은 조회형 매크로
(content-reporter, tasks-report-macro, detailssummary, contentbylabel, livesearch, report-*)
가 페이지를 열 때마다 서버 검색을 돌린 것으로 본다. 페이지는 지웠고, 원본 파일도 저장소에
두지 않는다. **조회형 매크로는 시험으로도 넣지 않는다.**

## 다시 읽어서 안 것 (렌더링은 못 봤다)

| 판정 | 매크로 |
|---|---|
| 설치됨 | ui-tabs/ui-tab, ui-expand, ui-button, divbox, horizontal-nav-group/item, tabs-group/tab-pane, html, multiexcerpt, multiexcerpt-include, excerpt-include, table-chart, pivot-table, contributors-summary, change-history, version-history, contentbylabel, livesearch, tasks-report-macro, detailssummary, roadmap, profile, widget, multimedia, view-file, viewpdf, report-table/column/info/empty, content-reporter, date-sort |
| 미설치 (`<ac:macro>` 로 바뀜) | lucidchart, iframe |

- multimedia·view-file·viewpdf 를 첨부 없이 넣으면 서버가 NullPointerException 을 내고
  **페이지 생성 전체가 실패했다.**
- profile 은 사용자 없이 넣으면 저장 때 `[User Profile Macro (Malformed)]` 글자로 바뀌었다.
- 매크로 파라미터 안의 페이지 링크가 저장 시점에 없는 페이지(자기 자신)를 가리키면
  `<ac:link></ac:link>` 로 비워졌다. 페이지가 생긴 뒤 다시 올리자 남았다.
- horizontal-nav-item·tab-pane 은 `anchor`, table-chart·pivot-table 은 `id` 파라미터가 생성 때
  붙었고, 같은 내용으로 다시 올렸을 때는 붙지 않았다.
- contentbylabel 은 schema-version 3 으로 올라가며 `cql` 파라미터가 붙었다.

## 사내 매뉴얼과 정책 (DSConfluence 매뉴얼 아래)

- 매크로 매뉴얼에는 부하·성능 경고가 없다. 쓰는 법 규칙만 있다: excerpt 는 페이지에 하나,
  multiexcerpt 이름은 서로 달라야 한다, column 은 section 안, ui-tab 은 ui-tabs 안,
  chart-from-filter 는 table-filter 를 감싼다.
- 첨부는 페이지당 100개·합계 50MB 이하, 파일 하나 50MB 미만.
- html 매크로는 외부 리소스·과한 CSS 를 비권장하고 사이드바에는 넣지 말라고 한다.
- **REST 정책: Agent·MCP 서버 호출은 분당 15회. 넘으면 429, 반복 호출은 계정 비활성화
  대상.** 극비·국핵 데이터는 외부 LLM 에 넘기지 않는다.

## 반영된 곳

- `plugins/confluence-post/skills/post/SKILL.md` — 조회형·커스텀 매크로는 새로 넣지 않는다,
  접근 제한 페이지는 내용을 요청하지 않는다
- `plugins/confluence-post/skills/post/reference/existing-page.md` — 호출 수와 재시도,
  게시 실패·저장 시 바뀌는 것, 첨부 한도, minor edit
- `plugins/confluence-post/skills/post/reference/storage-format.md` — 매뉴얼 규칙, 쓰지 않는 것
- `plugins/confluence-post/skills/post/scripts/check.py` — QUERY, IN_USE 확장, NEEDS_ATTACHMENT,
  column·excerpt·profile 검사, lucidchart·iframe 미설치
