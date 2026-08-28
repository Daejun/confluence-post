# markdown → Confluence DC storage format 매핑

조각으로 낸다. `<!DOCTYPE>`, `<html>`, `<body>` 없음.
아래에서 "확인됨"은 2026-08-28 probe로 실제 렌더링을 본 것, 나머지는 Confluence DC
기본 매크로 기준이다.

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

## 표 — 확인됨

```xml
<table><tbody>
<tr><th>항목</th><th>f2fs</th><th>mtfs</th></tr>
<tr><td>rand write IOPS</td><td>12,400</td><td>18,900</td></tr>
</tbody></table>
```

헤더 행은 `<th>`. `<thead>`는 쓰지 않는다.
**`<td>` 안에 매크로를 넣을 수 있다** — 확인됨. 표 셀에 code 매크로가 들어간다.

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

### 확인된 language (22종, 전부 하이라이팅됨)

`c` `cpp` `diff` `bash` `shell` `text` `none` `python` `py` `java` `js`
`javascript` `json` `yaml` `xml` `sql` `rust` `go` `perl` `powershell`
`makefile` `ruby`

커널 코드는 `c`를 그대로 쓴다 — `cpp` 우회가 필요 없다. 패치는 `diff`.
이 목록 밖 언어는 `text`로 낸다.

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

## 이미지

```xml
<ac:image ac:width="600"><ri:attachment ri:filename="zone-layout.png"/></ac:image>
```

**먼저 페이지에 첨부해야 보인다.** 첨부가 필요한 파일은 초안에서 따로 목록으로 알린다.

## 도식 — PlantUML (설치 확인됨)

```xml
<ac:structured-macro ac:name="plantuml"><ac:plain-text-body><![CDATA[@startuml
A -> B: write
@enduml]]></ac:plain-text-body></ac:structured-macro>
```

소스가 평문이라 XHTML에 그대로 담긴다. 다만 **기본은 도식 없음**이고,
사용자가 도식을 요구했을 때만 낸다.

수식은 `ac:name="latex"` + `<ac:plain-text-body>`. 설치 확인됨.

## 쓰지 않는 것

- ASCII 도식 — 전역 게시물 규칙에서 금지. 표나 문장, 또는 PlantUML로 바꾼다.
- `mermaid` `mermaid-cloud` `mathblock` `gliffy` `excerpt` `children`
  — 렌더링되지 않는 것을 확인했다.
- `drawio` — 설치돼 있으나 에디터에서 그려야 한다. XHTML로 저작할 수 없다.
- `jira` — 실제 이슈 키가 있을 때만. 없는 키는 오류가 난다.
- 체크박스, 각주 — storage format에 대응이 없다. 목록과 본문으로 푼다.
- `<thead>`, `<style>`, `class` 속성 — 저장 시 사라지거나 무시된다.
