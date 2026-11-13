---
name: post
description: 사내 Confluence(Data Center)에 올릴 문서를 storage format(XHTML)으로 만든다. 기존 markdown을 변환하거나 처음부터 작성해 Edit Source에 그대로 넣을 조각 파일을 내고, Confluence MCP가 있으면 그 파일로 페이지를 만들거나 고친다. 입력이 HTML(한장 정리 등)이면 글은 Confluence 본문으로, 원본 CSS 는 페이지 범위 style 하나로, SVG 도식은 html 매크로로 옮겨 원본처럼 보이게 한다. Use when the user asks to write or convert a document for 사내 컨플루언스/Confluence, says "컨플루언스에 올릴 것", "컨플루언스 문법으로 바꿔줘", "이 html 컨플루언스에 올려줘", or asks to prepare a page for Confluence DC.
---

# 사내 Confluence 게시물 만들기

산출물은 **storage format(XHTML) 조각 파일** 하나다. Confluence MCP
(`mcp__confluence-mcp__*`)가 있으면 그 파일 그대로 페이지를 만들거나 고친다 —
**best effort** 다. MCP 가 없거나 실패하면 사용자가 파일을 **Edit Source**에 넣는다.
어느 쪽이든 파일이 먼저다. wiki markup(`h1.`, `{code}`)과 markdown insert는 쓰지 않는다 —
storage format 을 직접 넣어 둘 다 우회하고, 그 두 경로에만 있는 파서 함정을 피한다.

조각이므로 `<!DOCTYPE>`, `<html>`, `<body>`를 쓰지 않는다. 최상위는 `<p>`, `<h2>`,
`<table>`, `<ac:structured-macro>` 같은 요소들이 나열된 형태다.

## 확정된 환경 (2026-08-28, 2026-10-02 실측)

probe로 직접 렌더링해 확인한 것. 추측이 아니다.

**기본**
- Edit Source 편집·저장 가능. 저장해도 Confluence가 XHTML을 다시 쓰지 않는다
- 표 `<td>` 안에 code·expand 매크로가 들어간다
- CDATA 안의 `&` `<` `|` 가 그대로 나온다
- 8열 표, 긴 코드 한 줄, 3단 중첩 목록, h2~h6, blockquote, hr, 인라인 서식,
  외부·앵커·페이지 링크, 본문 이스케이프, `colspan`, `rowspan`, `<thead>` — 전부 정상

**code 언어 — 시험한 23종이 전부 하이라이팅된다**
`c` `cpp` `c++` `diff` `bash` `shell` `text` `none` `python` `py` `java` `js`
`javascript` `json` `yaml` `xml` `sql` `rust` `go` `perl` `powershell`
`makefile` `ruby`. `cpp` 우회가 필요 없다. 이 목록 밖 언어는 `text`로 낸다.
없는 언어는 회색(하이라이팅 없음)으로 나오므로 위 목록은 진짜로 칠해진 것이다.
**language 를 빼면 기본 언어로 칠해진다** — 로그·명령 출력은 `text` 를 준다.

`title` `linenumbers` `collapse` 파라미터도 동작한다.

**쓸 수 있는 매크로**
`code` `expand` `info` `note` `warning` `tip` `panel` `toc` `status`
`noformat` `anchor` `plantuml` `latex` `attachments`
`excerpt` `children` `pagetree` `include` `details` `section` `column` `chart`

**조회형 매크로는 사용자가 요청했을 때만, 범위를 정해서 넣는다** — `recently-updated`
`contentbylabel` `tasks-report-macro` `detailssummary` `livesearch` `content-reporter` 등은
페이지를 볼 때마다 검색을 돌린다. 범위(space·상위 페이지)를 정하지 않으면 기본값을
따르는데, 매크로마다 달라 인스턴스 전체가 될 수 있다. markdown 에는 대응이 없으니 변환할
때 스스로 만들지 않는다. 범위 없이 여럿 넣은 시험 페이지가 열리지 않은 일이 있었다 —
원인을 따로 떼어 확인하지는 않았다. 쓰는 법은 `reference/storage-format.md` 의 조회형 절.
check.py 는 범위가 없으면 ERROR, 있으면 WARN 이다. 개정하는 페이지에 원래 있던 범위 없는
것은 고치지 않고 `--keep-query` 로 둔다.

**커스텀 매크로도 새로 넣지 않는다** — ui-tabs·ui-expand·divbox·multiexcerpt·table-filter
등 설치는 돼 있지만 렌더링과 파라미터를 확인하지 않았다. 기존 페이지에 있던 것만
옮긴다. 확인되지 않은 매크로를 서버에 넣어 시험하지 않는다.

**`html` 매크로는 HTML 입력일 때만 새로 넣는다** — 렌더링은 확인했다(2026-11-12:
`<style>`, inline SVG, `<script>`, `<iframe srcdoc>` 가 그려졌다). 사내 매뉴얼이 외부
리소스와 과한 CSS 를 비권장하므로, 입력이 HTML 일 때 **페이지 범위 `<style>` 하나와 SVG
도식**에만 쓴다. 그 밖의 문서에는 넣지 않는다. `reference/html-input.md`.
`panel` 의 `borderColor` `bgColor` `borderStyle` `borderWidth` 와 `status` 의 `subtle` 도
그려지는 것을 같은 때 확인했다.

**쓸 수 없는 매크로 (렌더링 안 되는 것을 확인)**
`mermaid` `mermaid-cloud` `mathblock` `gliffy`. 넣고 저장하면 Confluence 가
`<ac:macro>` 로 바꾸고 **본문을 지운다** — mermaid 소스가 소리 없이 사라진다.

**조건부**
- `drawio` — 설치돼 있다(미설치가 아니라 오류가 났다). 다만 다이어그램을 에디터에서
  그려야 하므로 XHTML로 저작할 수 없다. 스킬이 내지 않는다.
- `jira` — 매크로는 있다. 실제 이슈 키로만 렌더링된다.
- 체크박스(`<ac:task-list>`) — `ac:task-id` 를 넣으면 눌러서 저장까지 된다. 없으면
  보이기만 하고 누를 때 저장 오류가 난다. markdown 체크박스는 이것으로 바꾼다.
  `reference/storage-format.md` 의 체크박스 절.

**매크로 설치 여부는 저장 후 다시 읽으면 안다.** 설치된 매크로는
`ac:structured-macro` 로 남고 `ac:macro-id`·`ac:schema-version` 이 붙는다. 설치되지
않은 매크로는 `<ac:macro>` 로 바뀐다. 렌더링을 보지 않고도 구분된다.

## 실제 페이지에서 확인한 것 (2026-10-02)

MCP 로 사내 페이지의 storage 원문을 읽어 본 것이다. 렌더링 결과가 아니라 저장된
형태다.

- `class`(`wrapped`, `relative-table`), 표의 `style="width:…"`, `<colgroup>` 은
  저장된다. 새로 쓸 때는 넣지 않고, 기존 페이지에 있던 것은 그대로 둔다.
- `<thead>` 는 렌더링도 되지만 이 스킬은 `<tbody>` 안 `<tr><th>` 로 통일한다.
- code 언어는 `c++` 가 가장 흔하고, language 없는 code 매크로도 흔하다.
- 본문을 h1 부터 쓰는 페이지가 h2 부터 쓰는 페이지보다 많다. 이어 붙일 페이지가
  h1 부터 쓰면 그 관례를 따르고 check.py 에 `--h1` 을 준다.
- plantuml 매크로는 에디터가 `atlassian-macro-output-type=INLINE` 으로 저장한다.
  줄 나뉨에는 영향이 없다. `reference/plantuml.md`.

## 도식

**PlantUML을 쓸 수 있다.** 사내 서버는 **1.2024.8** 이다.
문법 규칙과 쓰지 않는 것은 `reference/plantuml.md` 에 있다 — 도식을 낼 때 그 파일을 읽는다.
소스가 평문이라 XHTML 안에 그대로 담긴다.

check.py 는 문법 규칙(뼈대, 금지 구문, 다이어그램 타입)만 정적으로 본다. 실제로 그려지는지는
사내 서버에 넣어 봐야 안다. 도식을 낸 초안에는 그 점을 밝힌다.

```xml
<p><ac:structured-macro ac:name="plantuml"><ac:plain-text-body><![CDATA[@startuml
A -> B: write
@enduml]]></ac:plain-text-body></ac:structured-macro></p>
```

다만 **기본은 도식 없음**이다. 전역 게시물 규칙이 도식을 빼도록 되어 있다.
사용자가 도식을 요구했을 때만 PlantUML로 낸다. ASCII 도식은 어느 경우에도 내지 않는다.

## 아직 확인 안 된 것

- Confluence 버전 — 사내 REST 정책 문서가 8.9.3 문서를 가리키지만 실제 버전은 적혀 있지 않다
- 중첩 체크박스, 체크박스 본문 안의 목록
- PlantUML 이 위아래 텍스트에 붙어 나온 보고의 원인 — probe 로는 재현되지 않았다

## 순서

1. **입력을 정한다.** 변환할 markdown 파일 경로가 있으면 읽는다. 없으면 새로 쓴다.
   어느 쪽인지 한 줄로 밝히고 시작한다. 고칠 페이지나 올릴 부모 페이지의 URL 을
   받았으면 그것도 적어 둔다 — 6단계에서 읽고 9단계에서 올린다.
   **입력이 HTML 이면 `reference/html-input.md` 를 읽고 그 경로로 간다.** 같은 내용의
   markdown 이 옆에 있어도, 사용자가 HTML 을 가리켰으면 HTML 을 옮긴다 — 원본처럼 보이는
   것이 요청이다. 문서 유형(2단계)은 원본이 이미 정한 것이므로 줄이지 않고 그대로 옮긴다.

2. **문서 유형을 정하고 그 기준으로 줄인다.** 전역 CLAUDE.md의 "게시물" 규칙이
   적용되지만, 유형에 따라 근거로 볼 것이 갈린다.

   - **보고형** — 상태를 알리거나 무언가를 요청하는 글(주간보고, PR 요약, 장애 보고).
     규칙을 그대로 적용한다. 배경 설명, 용어 정의, 경위 서술, 대안 기각 목록을 뺀다.
   - **기록형** — 조사·설계 기록 자체가 산출물인 글(분석 노트, DESIGN, 리뷰 근거).
     **기각한 가설과 "왜 이렇게 됐나"는 결론의 근거이므로 빼지 않는다.** 근거에는
     커밋 SHA와 `파일:줄`을 붙인다.

   어느 유형이든 빼는 것: 날짜 서술, 감상, 인사말, 자기 요약 절.
   **ASCII 도식도 뺀다** — 표나 문장으로 바꾼다. 도식이 꼭 필요하다고 사용자가
   말했을 때만 PlantUML로 낸다.

   **유형이 추론되면 묻지 않는다.** 사용자가 "주간보고", "공유용", "설계 노트"처럼
   말했거나, 원문이 기각 가설 표·`git show` 인용·"왜 …인가" 절로 이루어져 있으면
   그것으로 정하고 **한 줄로 밝히고 진행한다.**
   추론이 안 될 때만 AskUserQuestion 으로 한 번 묻는다 — 질문 하나, 선택지는
   보고형/기록형 둘. 그 뒤로는 다시 묻지 않는다. 초안을 보여준 다음의 수정 요청은
   자유 형식으로 받는다.

   남긴 것과 뺀 것은 8단계 초안에서 밝힌다. 유형을 잘못 잡았으면 거기서 되돌린다.

3. **변환한다.** 매핑은 `reference/storage-format.md`, 완성된 예시는
   `reference/example.xhtml`. 외우지 말고 두 파일을 읽는다.
   위 "확정된 환경" 에 없는 매크로·언어는 쓰지 않는다.
   HTML 입력이면 `scripts/html2storage.py` 로 옮긴다(한장 정리 템플릿). 모르는 요소에서
   멈추면 그 자리만 `reference/html-input.md` 의 대응표대로 손으로 옮긴다.

4. **`out/<slug>.xhtml` 에 쓴다.** 기준은 **현재 작업 디렉터리**다 — 원본 markdown이
   있는 곳도, 스킬이 설치된 곳도 아니다. slug은 영문 kebab-case.
   현재 디렉터리에 쓸 수 없으면 scratchpad에 쓴다. 어느 쪽이든 **절대 경로로** 알린다.

5. **검증한다.** 검사기는 이 SKILL.md 와 같은 디렉터리의 `scripts/check.py` 다.
   스킬을 불러올 때 표시된 base directory 가 있으면 그 아래를 쓴다. 없으면 설치 형태에
   따라 절대 경로가 다르니 한 번 찾아서 쓴다.
   ```bash
   CHECK=$(find -L ~/.claude -path "*/skills/post/scripts/check.py" 2>/dev/null | head -1)
   python3 "$CHECK" out/<slug>.xhtml
   ```
   이어 붙일 페이지가 본문을 h1 부터 쓰면 `--h1` 을 준다(6단계에서 확인한 관례).
   HTML 입력이면 `--html-input` 을 준다 — `html` 매크로를 style 하나와 SVG 도식으로만
   허용하고, 범위 밖 CSS·외부 리소스·script·깨진 속성 따옴표를 ERROR 로 막는다.
   ERROR가 하나라도 있으면 고쳐서 다시 돌린다. 통과하지 않은 것을 사용자에게 주지 않는다.
   WARN 은 막지 않지만 그냥 넘기지 않는다 — 제목 단계 WARN 은 절 구분이 어긋났다는
   신호다. 고치거나, 그대로 두는 이유를 초안에 적는다.

6. **원문 구조와 대조한다.** check.py 는 출력물 안에서 닫힌 규칙(h1 사용, 건너뛴 제목
   단계, 빈 제목, 제목 없음)만 본다. 원문과 나란히 놓고 보는 것은 사람이 한다.
   변환한 markdown 이 있으면 원문을 다시 열어 아래를 확인한다.
   - **절이 그대로 있는가.** 절의 수와 순서가 원문과 같은가. 두 절이 하나로 붙거나
     한 절이 통째로 빠지지 않았는가. **줄인 것과 빠뜨린 것은 다르다** — 게시물 규칙으로
     뺀 절이 있으면 초안에서 무엇을 왜 뺐는지 밝힌다. 소리 없이 사라지면 안 된다.
   - **제목 단계가 대응하는가.** 원문 `#` 는 페이지 제목이 가져가므로 본문은 h2 부터다.
     `##`→h2, `###`→h3 로 문서 전체에 같은 규칙을 적용했는가. 한 절만 단계가 다르면
     toc 가 어긋난다. 이어 붙일 페이지가 h1 부터 쓰면 한 단계씩 올려 `##`→h1 로
     맞춘다.
   - **덩어리가 보존됐는가.** 목록의 중첩 단계, 표의 열 수와 헤더 행, 코드 블록의 개수와
     언어가 원문과 같은가. 원문에서 코드였던 것이 문단으로, 표였던 것이 목록으로
     뭉개지지 않았는가.
   - **이어 붙일 페이지가 있으면 그 페이지의 관례를 따른다.** 개정이거나 기존 페이지에
     덧붙이는 것이면 그 페이지의 storage 원문을 먼저 본다. MCP 가 있으면
     `get_page(convert_to_markdown=false)` 로 읽는다 — 읽는 법, 그대로 옮기면 안 되는
     자리, 에디터가 남긴 흔적의 처리는 `reference/existing-page.md` 를 읽는다.
     제목을 h2 부터 쓰는지 h3 부터 쓰는지, 절 이름, toc 사용 여부, code 매크로
     파라미터(`title` `linenumbers` `collapse`) 관례를 그대로 쓴다. 내 형식을 새로
     만들지 않는다.
     **MCP 가 없어서 못 읽었으면 사용자에게 Edit Source 내용을 한 번 요청한다.** 접근
     제한(`confluence_access_forbidden`)으로 못 읽었으면 요청하지 않는다 — 극비·국핵일 수
     있고, 그 내용을 외부 LLM 에 넘기는 것은 사내 보안 정책상 금지다. 어느 쪽이든 못
     구했으면 기본 관례(본문 h2 시작, toc 없음, code 파라미터는 language 만)로 쓰고, 초안
     첫 줄에 "기존 페이지 관례를 대조하지 못했다"고 적는다. 혼자 절충안을 만들지 않는다.
     MCP 호출은 분당 15회 제한이 있다 — 호출 수와 재시도 규칙은 `reference/existing-page.md`.

7. **매크로 안의 내용을 검토한다.** check.py 는 문법만 본다. XHTML 이 맞아도 안의
   내용은 틀릴 수 있고, 그건 사람이 읽어야 잡힌다. 아래를 하나씩 확인한다.
   - **PlantUML** — 화살표 방향, 참여자 이름, 분기 조건이 본문 설명과 맞는가.
     설명은 "GC 가 zone 을 고른다"인데 그림은 반대로 가 있는 식의 어긋남을 본다.
     check.py 는 문법 규칙만 보고 의미는 보지 않으니, 그림을 말로 다시 읽어 본다.
   - **code 매크로** — title 에 파일 경로를 적었으면 **그 파일을 실제로 열어 대조한다.**
     기억으로 쓴 코드를 올리지 않는다. diff 는 커밋에서 뽑는다(`git show`).
   - **표의 수치** — 측정 출력에서 복사한 것인가. 조건(커널·디스크 실측 채움·워크로드·
     마운트 옵션·기능 발동 여부)이 같이 적혀 있는가.
   - **링크와 번호** — PR·이슈·커밋 번호를 기억으로 쓰지 않는다. `gh` 출력에서 복사한다.

   하나라도 대조하지 못한 것이 있으면 초안에 그렇게 밝힌다. "확인함"으로 넘기지 않는다.

8. **초안을 보여주고 승인을 받는다.** 렌더링될 내용을 읽기 좋은 형태로 보여준다
   (XHTML 원문을 통째로 화면에 쏟지 않는다). 수정 요청을 받으면 변호하지 말고 고친 초안을
   다시 보여준다. MCP 로 올릴 거면 **올릴 곳**(새 페이지의 부모와 제목, 또는 고칠 페이지)도
   같이 보여주고 승인받는다. 모르면 여기서 한 번 묻는다.

9. **전달한다. 여기까지가 이 스킬의 끝이다.**

   **MCP 가 있고 올릴 곳을 승인받았으면 올린다.** 파일 내용을 그대로 `create_page` /
   `update_page(content_format="storage")` 에 넣는다. 절차와 올린 뒤 확인할 것은
   `reference/existing-page.md` 의 "게시" 절. 성공하면 페이지 URL 을 주고 브라우저에서
   한 번 봐 달라고 한다 — 렌더링은 MCP 로 확인할 수 없다.

   **MCP 가 없거나, 올릴 곳이 없거나, 실패했으면** 실패한 이유를 한 줄로 적고 붙여넣기로
   넘어간다. 넣는 방법을 이 문장 그대로 적는다. `<파일명>` 자리에 실제 산출물 이름을 넣는다.

   > 페이지 작성 화면에서 오른쪽 위의 `< >` 를 눌러 `<파일명>` 출력물을 넣어주세요.

   어느 쪽이든 그 다음 줄에 파일 경로와 **줄 수·문자 수**를 적는다. 붙여넣기라면 분량이
   곧 옮기는 비용이다. 길면 어디서 끊어 나눠 넣을지 같이 알려준다.

## 가장 틀리기 쉬운 자리

- **이스케이프.** CDATA 밖의 텍스트 **전부** — 문단만이 아니라 `<code>` 안, 제목,
  표 셀, 링크 글자도 해당한다. `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`.
  커널 로그·주소·메일 인용이 자주 걸린다 — `<code>&lt;writer&gt; blocked</code>`,
  `<code>hanqi &lt;hanqi@vivo.com&gt;</code>`, `<code>fg_gc_time &gt; 0</code>`.
  코드를 그대로 보여줄 자리면 `<code>` 대신 code 매크로(CDATA)를 쓴다.
- **CDATA 안에 `]]>` 가 들어가면 안 된다.** 코드에 그 세 글자가 있으면 code 매크로를
  둘로 쪼갠다.
- **중첩 목록은 부모 `<li>` 안에 넣는다.** `<ul>` 형제로 두면 목록이 끊긴다.
- **이미지는 먼저 첨부해야 한다.** `<ac:image>`만 넣고 첨부를 안 하면 깨진 이미지가 된다.
  첨부가 필요한 파일은 초안에서 목록으로 따로 알려준다.
- **미설치 매크로를 쓰지 않는다.** mermaid·mathblock·gliffy는 렌더링되지 않고,
  저장하는 순간 본문이 지워진다. check.py가 ERROR로 걸러낸다.
- **PlantUML 소스에 `]]>` 가 들어가지 않게 한다.** CDATA가 거기서 끊긴다.
- **PlantUML 매크로는 `<p> ... </p>` 로 감싼다.** 위아래 텍스트에 붙어 나온 보고가
  있었고 감싸서 고쳐졌다. probe 에서는 감싸지 않아도 줄이 나뉘었으니 원인은 따로
  있지만, 감싸도 렌더링은 같으므로 감싸 둔다. **PlantUML 만** 감싼다.
  code·expand·info 는 감싸지 않는다. `reference/plantuml.md` 참조.
- **본문 span 의 `font-size` 는 px 로 쓴다.** `.86rem` 같은 rem 값은 저장할 때 Confluence 가
  지운다 — 색만 남고 글씨는 본문 크기로 나온다. check.py 가 ERROR 로 막는다. html 매크로
  (CDATA) 안은 그대로 남는다.
- **HTML 입력의 style 속성 안에 큰따옴표를 쓰지 않는다.** `style="font-family:"IBM …""` 는
  속성이 거기서 끊기고 브라우저가 소리 없이 버린다. 글꼴 이름은 작은따옴표로 쓴다.
  `reference/html-input.md`.
- **CDATA 안을 들여쓰지 않는다.** 요소 사이 들여쓰기는 렌더링에 영향이 없지만,
  CDATA 안의 공백은 코드 내용 그 자체다. `<![CDATA[` 바로 뒤부터 내용을 시작하고
  `]]>` 는 마지막 줄 끝에 붙인다. 코드 자체의 들여쓰기(커널이면 탭)는 그대로 살린다.
