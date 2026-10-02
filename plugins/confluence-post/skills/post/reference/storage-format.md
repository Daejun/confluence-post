# markdown → Confluence DC storage format 매핑

조각으로 낸다. `<!DOCTYPE>`, `<html>`, `<body>` 없음.
아래에서 "확인됨"은 probe(2026-08-28, 2026-10-02)로 실제 렌더링을 본 것, 나머지는
Confluence DC 기본 매크로 기준이다.

## 들여쓰기 — CDATA 안만 예외

요소 사이의 들여쓰기와 줄바꿈은 렌더링에 영향이 없다. 읽기 좋게 들여쓴다.
Edit Source에서 사람이 고칠 수 있어야 하므로 들여쓰는 편이 낫다.

**단 `<ac:plain-text-body>` 의 CDATA 안은 예외다.** 그 안의 공백은 코드 내용 그 자체다.

```xml
<!-- 틀림: 코드 앞에 공백 4칸이 붙어 렌더링된다 -->
<ac:structured-macro ac:name="code">
  <ac:plain-text-body><![CDATA[
    int x;
  ]]></ac:plain-text-body>
</ac:structured-macro>

<!-- 맞음: 여는 태그 바로 뒤부터 내용, 닫는 ]]> 는 마지막 줄 끝에 붙인다 -->
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">c</ac:parameter>
  <ac:plain-text-body><![CDATA[int x;
	return 0;]]></ac:plain-text-body>
</ac:structured-macro>
```

코드 자체의 들여쓰기(위의 탭)는 그대로 살린다. 커널 코드는 탭이다.

문장 중간에서도 줄바꿈하지 않는다. `<p>앞<code>x</code>뒤</p>` 사이에 줄바꿈을 넣으면
렌더링에 공백이 하나 생긴다.

## 문단·인라인

| markdown | storage format |
|---|---|
| 문단 | `<p>본문</p>` |
| 문단 안 줄바꿈 | `<br/>` |
| `**굵게**` | `<strong>굵게</strong>` |
| `*기울임*` | `<em>기울임</em>` |
| `~~취소~~` | `<s>취소</s>` |
| `` `코드` `` | `<code>코드</code>` |
| `---` | `<hr/>` |

`_`는 storage format에서 아무 의미가 없다. `mtfs_zone_alloc()`을 그대로 쓴다.
이스케이프가 필요한 것은 `&` `<` `>` 셋뿐이다.

## 제목

`## 제목` → `<h2>제목</h2>`. h1은 페이지 제목과 겹치므로 본문은 h2부터 쓴다.

## 목록

```xml
<ul>
  <li>1단계
    <ul><li>2단계</li></ul>
  </li>
  <li>다음 항목</li>
</ul>
```

중첩 `<ul>`은 **부모 `<li>` 안에** 넣는다. 번호 목록은 `<ol>`.

### 체크박스 — `<ac:task-list>` — 확인됨

markdown `- [x]` / `- [ ]` 목록은 네이티브 체크박스로 바꾼다. 화면에서 눌러 체크하고
저장할 수 있다.

```xml
<ac:task-list>
<ac:task><ac:task-id>1</ac:task-id><ac:task-status>complete</ac:task-status><ac:task-body>zone 재선택 경로 수정</ac:task-body></ac:task>
<ac:task><ac:task-id>2</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>xfstests 재확인</ac:task-body></ac:task>
</ac:task-list>
```

- **`<ac:task-id>` 를 반드시 넣는다.** 없으면 보이기는 하지만 누를 때 저장 오류가 난다.
  페이지 전체에서 1 부터 겹치지 않게 매긴다 — 목록이 여럿이면 이어서 센다. 기존
  페이지를 개정할 때는 그 페이지에서 쓰인 가장 큰 id 다음부터 쓴다. check.py 가 빠진
  것과 겹친 것을 ERROR 로 막는다.
- `[x]` → `complete`, `[ ]` → `incomplete`. 리터럴 `[x]` `[ ]` 를 남기지 않는다.
- `<ac:task-body>` 안은 인라인만 둔다(글자, `<code>`, `<strong>`, 링크). 중첩 체크박스와
  본문 안 목록은 확인하지 않았다 — 하위 항목은 평탄화하거나 바로 아래 일반 목록으로 뺀다.

**체크박스와 일반 항목이 섞인 목록**, 그리고 **표 안의 상태 칸**은 status 매크로를
쓴다. Green `완료` 와 Grey `대기` 두 가지만 쓴다 — 표기를 매번 새로 정하지 않는다.

```xml
<td><ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Green</ac:parameter><ac:parameter ac:name="title">완료</ac:parameter></ac:structured-macro></td>
```

## 표 — 확인됨

```xml
<table><tbody>
<tr><th>항목</th><th>f2fs</th><th>mtfs</th></tr>
<tr><td>rand write IOPS</td><td>12,400</td><td>18,900</td></tr>
</tbody></table>
```

헤더 행은 `<tbody>` 안의 `<th>`. `<thead>` 도 렌더링되지만 쓰지 않는다 — 한 가지로
통일한다. 기존 페이지에 있던 `<thead>` 는 그대로 둔다.
**`<td>` 안에 매크로를 넣을 수 있다** — 확인됨. 표 셀에 code 매크로가 들어간다.

셀 병합 `colspan` `rowspan` — 확인됨. `class`(`wrapped` 등)·`style="width:…"`·
`<colgroup>` 은 저장되지만 새로 쓸 때는 넣지 않는다. 기존 페이지 표에 있던 것은
그대로 둔다.

## 코드 — 확인됨

```xml
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">c</ac:parameter>
  <ac:parameter ac:name="title">fs/mtfs/gc.c</ac:parameter>
  <ac:parameter ac:name="linenumbers">true</ac:parameter>
  <ac:plain-text-body><![CDATA[if (z->valid_blocks == 0)
	return 0;]]></ac:plain-text-body>
</ac:structured-macro>
```

- CDATA 안에서는 `&` `<` `>` `|` 를 이스케이프하지 않는다. 확인됨.
- **CDATA 안에 `]]>` 가 있으면 안 된다.** 있으면 매크로를 둘로 나눈다.
- `title` `linenumbers` `collapse` 파라미터 전부 동작한다. 긴 로그는 `collapse=true`.

### 확인된 language (23종, 전부 하이라이팅됨)

`c` `cpp` `c++` `diff` `bash` `shell` `text` `none` `python` `py` `java` `js`
`javascript` `json` `yaml` `xml` `sql` `rust` `go` `perl` `powershell`
`makefile` `ruby`

커널 코드는 `c`를 그대로 쓴다 — `cpp` 우회가 필요 없다. 패치는 `diff`.
이 목록 밖 언어는 `text`로 낸다. 없는 언어는 회색으로 나온다.

**language 를 빼지 않는다.** 빼면 기본 언어로 칠해져 로그·명령 출력에 엉뚱한 색이
든다. 코드가 아니면 `text`.

언어 없는 고정폭 블록은 `ac:name="noformat"` + `<ac:plain-text-body>`.

## 패널

```xml
<ac:structured-macro ac:name="info">
  <ac:parameter ac:name="title">제목</ac:parameter>
  <ac:rich-text-body><p>본문</p></ac:rich-text-body>
</ac:structured-macro>
```

`info` / `note` / `warning` / `tip` / `panel` 이 같은 형태다.
본문은 `<ac:rich-text-body>` 안에 `<p>`로 감싼다. 코드와 달리 CDATA가 아니라 XHTML이다.

## 접기 — 확인됨

```xml
<ac:structured-macro ac:name="expand">
  <ac:parameter ac:name="title">벤치 원본 로그</ac:parameter>
  <ac:rich-text-body><p>안쪽</p></ac:rich-text-body>
</ac:structured-macro>
```

긴 로그·원본 출력은 여기 넣는다. 안에 code 매크로를 중첩할 수 있다.

## 목차·상태

```xml
<ac:structured-macro ac:name="toc"><ac:parameter ac:name="maxLevel">2</ac:parameter></ac:structured-macro>
<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">Green</ac:parameter><ac:parameter ac:name="title">MERGED</ac:parameter></ac:structured-macro>
```

`colour`는 Grey / Red / Yellow / Green / Blue.

## 링크

```xml
<a href="https://github.com/...">PR #12</a>
<ac:link><ri:page ri:content-title="다른 페이지 제목"/><ac:plain-text-link-body><![CDATA[표시할 글자]]></ac:plain-text-link-body></ac:link>
```

URL 안의 `&`도 `&amp;`로 바꿔야 한다.

**로컬 상대경로 링크는 링크로 만들지 않는다.** 원문의 `[DESIGN.md](DESIGN.md)`,
`[logs/](logs/)` 는 읽는 사람이 열 수 없는 경로다. 기본은 평문
`<code>DESIGN.md</code>` 다. 저장소가 GitHub에 있고 `gh` 로 URL을 확인한 경우에만
절대 URL `<a href>` 로 바꾼다 — URL을 기억으로 쓰지 않는다.

## 이미지

```xml
<ac:image ac:width="600"><ri:attachment ri:filename="zone-layout.png"/></ac:image>
```

**먼저 페이지에 첨부해야 보인다.** 첨부가 필요한 파일은 초안에서 따로 목록으로 알린다.

## 도식 — PlantUML (설치 확인됨)

```xml
<p><ac:structured-macro ac:name="plantuml"><ac:plain-text-body><![CDATA[@startuml
A -> B: write
@enduml]]></ac:plain-text-body></ac:structured-macro></p>
```

**`<p>` 로 감싼다.** 위아래 텍스트에 붙어 나온 보고가 있었고 감싸서 고쳐졌다. 감싸도
렌더링은 같다. 감싸는 것은 PlantUML 만이다 — code·expand·info 같은 매크로는 위 절의
형태 그대로 둔다. 자세한 건 `reference/plantuml.md`.

소스가 평문이라 XHTML에 그대로 담긴다. 다만 **기본은 도식 없음**이고,
사용자가 도식을 요구했을 때만 낸다.

수식은 `ac:name="latex"` + `<ac:plain-text-body>`. 설치 확인됨.

## 그 밖의 매크로 — 확인됨

markdown 에는 대응이 없어 변환할 때 새로 만들지는 않는다. 사용자가 요구했거나 기존
페이지에 있던 것이면 이 형태로 쓴다.

```xml
<!-- 하위 페이지 목록 -->
<ac:structured-macro ac:name="children"><ac:parameter ac:name="page"><ac:link><ri:page ri:content-title="부모 페이지 제목"/></ac:link></ac:parameter></ac:structured-macro>
<!-- 트리. root 아래 -->
<ac:structured-macro ac:name="pagetree"><ac:parameter ac:name="root"><ac:link><ri:page ri:content-title="부모 페이지 제목"/></ac:link></ac:parameter></ac:structured-macro>
<!-- 다른 페이지 본문 끼워 넣기. 파라미터 이름이 빈 문자열이다 -->
<ac:structured-macro ac:name="include"><ac:parameter ac:name=""><ac:link><ri:page ri:content-title="페이지 제목"/></ac:link></ac:parameter></ac:structured-macro>
<!-- 발췌. 본문이 그대로 보인다 -->
<ac:structured-macro ac:name="excerpt"><ac:rich-text-body><p>요약 한 줄</p></ac:rich-text-body></ac:structured-macro>
<!-- page properties. 안에 2열 표 -->
<ac:structured-macro ac:name="details"><ac:rich-text-body><table><tbody>
<tr><th>상태</th><td>진행 중</td></tr>
</tbody></table></ac:rich-text-body></ac:structured-macro>
<!-- 2단 배치 -->
<ac:structured-macro ac:name="section"><ac:rich-text-body>
<ac:structured-macro ac:name="column"><ac:parameter ac:name="width">50%</ac:parameter><ac:rich-text-body><p>왼쪽</p></ac:rich-text-body></ac:structured-macro>
<ac:structured-macro ac:name="column"><ac:parameter ac:name="width">50%</ac:parameter><ac:rich-text-body><p>오른쪽</p></ac:rich-text-body></ac:structured-macro>
</ac:rich-text-body></ac:structured-macro>
<!-- 표를 그래프로. 첫 행이 헤더. 쉼표 넣은 값(18,400)은 시험하지 않았다 -->
<ac:structured-macro ac:name="chart"><ac:parameter ac:name="type">bar</ac:parameter><ac:parameter ac:name="title">제목</ac:parameter><ac:rich-text-body><table><tbody>
<tr><th>fs</th><th>IOPS</th></tr>
<tr><td>a</td><td>18400</td></tr>
</tbody></table></ac:rich-text-body></ac:structured-macro>
```

`ri:content-title` 은 같은 space 의 페이지 제목과 글자 그대로 같아야 한다. MCP 가
있으면 CQL `title = "…" and space = "…"` 로 있는지 확인한다.

## 쓰지 않는 것

- ASCII 도식 — 전역 게시물 규칙에서 금지. 표나 문장, 또는 PlantUML로 바꾼다.
- `mermaid` `mermaid-cloud` `mathblock` `gliffy` — 렌더링되지 않는 것을 확인했다.
  저장하면 `<ac:macro>` 로 바뀌고 본문이 지워진다.
- `drawio` — 설치돼 있으나 에디터에서 그려야 한다. XHTML로 저작할 수 없다.
- `jira` — 실제 이슈 키가 있을 때만. 없는 키는 오류가 난다.
- 각주 — storage format에 대응이 없다. 본문으로 푼다.
- `<style>` — 무시된다.
- `<thead>`, `class` 속성 — 저장은 되지만 새로 쓰지 않는다. 위 `표` 절.
