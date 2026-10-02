# confluence-post

사내 Confluence Data Center에 올릴 문서를 **storage format(XHTML)** 으로 만들어 주는
Claude Code 스킬. markdown을 주면 변환하고, 없으면 새로 쓴다. 결과는 파일 한 장으로
저장하고, **Confluence MCP** 가 연결돼 있으면 그 파일로 페이지까지 올린다(best effort).
MCP 가 없거나 실패하면 그 파일을 페이지의 **Edit Source** 에 붙여넣으면 끝이다.

## 빠른 시작

**1. 설치** — Claude Code 안에서 두 줄.

```
/plugin marketplace add https://github.samsungds.net/daejun7-park/confluence-post.git
/plugin install confluence-post@confluence-post
```

**2. 부른다** — 스킬 이름은 외울 필요 없다. 파일을 주면 변환하고, 안 주면 새로 쓴다.
직접 부르려면 `/confluence-post:post`.

```
work/bench/STATUS.md 컨플루언스에 올릴 문서로 바꿔줘
```

**3. 올린다** — 초안을 승인하면 `out/<slug>.xhtml` 이 나온다. Confluence MCP 가 있으면
승인한 곳(새 페이지의 부모, 또는 고칠 페이지)에 스킬이 바로 올린다. 없거나 실패하면
페이지 편집 화면 오른쪽 위 `< >` (소스 편집) 를 눌러 그 파일 내용을 **전체** 붙여넣고
저장한다. 일반 편집 화면에 붙이면 태그가 글자로 보이니 반드시 `< >` 안에 넣는다.

자세한 것은 아래 [쓰는 법](#쓰는-법), 설치 옵션은 [설치](#설치).

## 왜 쓰나

**markdown을 그대로 붙여넣으면 깨진다.** DC는 Cloud의 fabric 에디터가 아니라 legacy
에디터를 쓴다. 표는 `|` 줄이 그대로 글자로 남고, 코드 블록은 하이라이팅 없이 평문이 된다.

**wiki markup(`h1.`, `{code}`)은 함정이 많다.** 단일 개행이 무시돼 줄이 붙고, `_` 가
기울임으로 먹히고, 표 셀 안의 `|` 가 셀 구분자로 잘린다. 커널 로그·diff·경로를 붙이면
거의 매번 하나는 걸린다.

**Edit Source + storage format은 그 두 경로를 다 우회한다.** 파서를 거치지 않고 최종
XHTML을 직접 넣기 때문에 위 함정이 전부 사라진다. 대신 손으로 쓰기엔 번거로운 형식이라
(`<ac:structured-macro>`, CDATA, 엔티티 이스케이프) 스킬이 대신 쓴다.

여기에 두 가지가 더 붙는다.

- **쓸 수 있는 매크로와 언어를 실측해 뒀다.** mermaid를 넣었다가 페이지에 빨간 오류가
  뜨는 일이 없다. 근거는 `probe/` — 실제 사내 인스턴스에 넣어 렌더링을 확인한 결과다.
- **내용도 게시물 규칙으로 줄인다.** 배경 설명, 경위 서술, 감상, 인사말을 빼고 사실·근거·
  요청만 남긴다. 근거는 `파일:줄`, 커밋 SHA, 측정치와 그 조건.

### 변환 예시

주는 것 (markdown):

```markdown
## 결론
zone 크기를 48M 으로 줄이면 rand-write IOPS 가 12% 오른다.

| fs | IOPS |
|---|---|
| f2fs | 18,400 |
| mtfs | 20,600 |

    if (a < b && c)
            return -EINVAL;
```

나오는 것 (`out/<slug>.xhtml`):

```xml
<h2>결론</h2>
<p>zone 크기를 48M 으로 줄이면 rand-write IOPS 가 12% 오른다.</p>
<table><tbody>
<tr><th>fs</th><th>IOPS</th></tr>
<tr><td>f2fs</td><td>18,400</td></tr>
<tr><td>mtfs</td><td>20,600</td></tr>
</tbody></table>
<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">c</ac:parameter>
<ac:plain-text-body><![CDATA[if (a < b && c)
	return -EINVAL;]]></ac:plain-text-body></ac:structured-macro>
```

`a < b && c` 가 본문에 있었다면 `&lt;` `&amp;&amp;` 로 바뀐다. CDATA 안이라 그대로
둔 것이고, 그 구분을 놓치면 저장이 거부된다. 이런 자리를 대신 지켜 주는 게 이 스킬이다.

## 설치

Claude Code 안에서:

```
/plugin marketplace add https://github.samsungds.net/daejun7-park/confluence-post.git
/plugin install confluence-post@confluence-post
```

갱신은 `/plugin update confluence-post`, 제거는 `/plugin uninstall confluence-post`.
갱신은 `plugin.json` 의 `version` 이 바뀌어야 받아진다 — 스킬을 고쳐 올리는 쪽은
`version` 을 같이 올린다.
재시작은 필요 없다. 설치됐는지는 `/plugin` 목록에서 확인한다.

### 고쳐가며 쓸 때는 clone + symlink

플러그인은 사본을 받아오므로 스킬을 손보려면 `/plugin update` 를 거쳐야 한다.
직접 고치면서 쓸 거면 symlink 를 쓴다 — 저장소를 고치는 즉시 반영된다.

```bash
git clone https://github.samsungds.net/daejun7-park/confluence-post.git ~/confluence
ln -s ~/confluence/plugins/confluence-post/skills/post ~/.claude/skills/post
```

**둘 중 하나만 쓴다.** 같이 쓰면 같은 스킬이 두 번 잡힌다.

### 요구사항

- Confluence **Data Center**. Cloud는 storage format이 달라 대상이 아니다.
- 페이지의 **Edit Source**(소스 편집) 권한. 읽기 전용 계정이면 못 쓴다.
- `check.py` 실행에 python3. 표준 라이브러리만 쓴다. 다른 의존성은 없다.
- 선택: 사내 **Confluence MCP**(`mcp__confluence-mcp__*`). 있으면 고칠 페이지를 읽어
  관례를 맞추고 결과를 직접 올린다. 없어도 파일까지는 똑같이 나온다.

## 쓰는 법

### 1. 부른다

스킬 이름을 외울 필요는 없다. 이렇게 말하면 잡힌다.

```
work/bench/STATUS.md 컨플루언스에 올릴 문서로 바꿔줘
```

```
지난주 mtfs 벤치 결과로 컨플루언스 페이지 하나 써줘
```

파일 경로를 주면 변환하고, 안 주면 대화 내용으로 새로 쓴다. 어느 쪽으로 갈지 먼저
한 줄로 밝히고 시작한다.

문서 유형(보고형 / 기록형)에 따라 얼마나 잘라낼지가 갈린다. 말이나 원문에서 분명하면
그대로 가고, 애매할 때만 한 번 묻는다. 조사·설계 노트는 기각한 가설과 경위를 근거로
보고 남기고, 주간보고·PR 요약은 뺀다.

기존 페이지를 고치거나 그 아래에 새로 쓸 거면 페이지 URL 을 같이 준다. MCP 로 그
페이지를 읽어 제목 단계·toc·code 파라미터 관례를 맞춘다.

### 2. 초안을 확인한다

XHTML 원문을 쏟아내지 않고, 렌더링될 내용을 읽기 좋은 형태로 보여준다. 고칠 곳을
말하면 고친 초안을 다시 보여준다. 승인 전에는 파일을 넘기지도, 페이지에 올리지도 않는다.
MCP 로 올릴 거면 올릴 곳도 이때 같이 승인한다.

이때 함께 확인하는 것: code 매크로의 `title` 에 적힌 파일을 실제로 열어 대조했는지,
표의 수치가 측정 출력에서 복사한 것인지와 조건이 적혀 있는지, PR·이슈·커밋 번호를
`gh` 출력에서 가져왔는지. 대조하지 못한 것이 있으면 초안에 그렇게 적는다.

### 3. 검사를 통과한 파일을 받는다

MCP 로 올렸으면 페이지 URL 이 같이 온다. 렌더링은 MCP 로 확인할 수 없으니 브라우저에서
한 번 본다. 이미지 첨부는 MCP 로 못 올리므로 첨부할 목록이 있으면 직접 올린다.

MCP 가 없거나 실패했으면 이렇게 받는다.

```
out/mtfs-zone-bench.xhtml: 142줄, 6,318자

페이지 작성 화면에서 오른쪽 위의 < > 를 눌러 mtfs-zone-bench.xhtml 출력물을 넣어주세요.
```

줄 수·문자 수를 같이 주는 이유는 그게 곧 옮기는 비용이라서다. 길면 어디서 끊어
나눠 넣을지도 알려준다.

### 4. Confluence에 넣는다 (붙여넣기)

1. 페이지를 만들거나 편집 화면을 연다
2. 오른쪽 위 `< >` (소스 편집 / Edit Source) 를 누른다
3. 파일 내용을 **전체** 복사해 그 창에 붙여넣는다 (기존 내용에 이어 붙일 거면 끝에)
4. 창을 닫고 저장한다

일반 편집 화면에 붙여넣으면 `<ac:structured-macro ...>` 가 글자로 보인다. 반드시
`< >` 안에 넣는다.

**이미지가 있으면 먼저 첨부한다.** 검사기가 첨부해야 할 파일 목록을 따로 알려준다.
첨부 없이 저장하면 깨진 이미지로 나온다.

## 쓸 수 있는 것 (2026-08-28, 2026-10-02 실측)

`probe/` 로 실제 렌더링을 확인한 결과다. 추측이 아니다.

**code 언어 23종 전부 하이라이팅** — `c` `cpp` `c++` `diff` `bash` `shell` `text`
`none` `python` `py` `java` `js` `javascript` `json` `yaml` `xml` `sql` `rust` `go`
`perl` `powershell` `makefile` `ruby`. 커널 코드에 `cpp` 우회가 필요 없다. 없는 언어는
회색으로 나오고, language 를 빼면 기본 언어로 칠해진다. `title` `linenumbers`
`collapse` 파라미터도 동작한다.

**쓸 수 있는 매크로** — `code` `expand` `info` `note` `warning` `tip` `panel`
`toc` `status` `noformat` `anchor` `plantuml` `latex` `attachments`
`recently-updated` `excerpt` `children` `pagetree` `include` `details` `section`
`column` `chart`

**쓸 수 없는 매크로** — `mermaid` `mermaid-cloud` `mathblock` `gliffy`.
저장하면 Confluence 가 `<ac:macro>` 로 바꾸고 본문을 지운다. check.py 가 ERROR로 막는다.

**조건부** — `drawio` 는 설치돼 있으나 에디터에서 그려야 해 XHTML로 저작할 수 없다.
`jira` 는 실제 이슈 키로만 렌더링된다. 체크박스(`ac:task-list`)는 `task-id` 를 넣으면
눌러서 저장까지 되고, 없으면 누를 때 저장 오류가 난다. markdown 체크박스는 id 를 붙인
네이티브 체크박스로 바꾼다.

**구조** — 3단 중첩 목록, 8열 표(안 잘림), 표 셀 안 code·expand, 긴 코드 한 줄,
링크 4종, 본문 이스케이프, h2~h6, `colspan`·`rowspan`·`<thead>` 전부 정상. Edit Source
로 저장해도 Confluence가 XHTML을 다시 쓰지 않는다.

**매크로 설치 여부는 MCP 로도 안다.** 페이지에 올린 뒤 다시 읽으면 설치된 매크로는
`ac:structured-macro` 로 남고 `ac:macro-id` 가 붙는다. 설치 안 된 매크로는 `<ac:macro>`
로 바뀐다. 스킬이 게시 후 이것을 확인한다.

### 도식

PlantUML을 쓸 수 있다 (사내 서버 1.2024.8). 소스가 평문이라 XHTML에 그대로 담긴다.
다만 **기본은 도식 없음**이고, 요구가 있을 때만 낸다. ASCII 도식은 어느 경우에도 내지
않는다. check.py 는 문법 규칙만 정적으로 보므로, 실제로 그려지는지는 넣어 봐야 안다 —
도식이 든 초안에는 그 점을 밝힌다.

### 남은 미확인

- Confluence 버전
- 중첩 체크박스, 체크박스 본문 안의 목록
- PlantUML 이 위아래 텍스트에 붙어 나온 보고의 원인 — probe 로는 재현되지 않았다.
  `<p>` 로 감싸면 고쳐졌고, 감싸도 렌더링은 같아서 감싸 둔다

실제 페이지의 storage 원문을 MCP 로 읽어 본 결과(class·`<colgroup>` 이 저장되고,
본문을 h1 부터 쓰는 페이지가 많다 등)는 SKILL.md 의 "실제 페이지에서 확인한 것" 에 있다.

## 검사기

스킬이 파일을 내기 전에 자동으로 돌린다. 직접 돌릴 수도 있다.

```bash
python3 plugins/confluence-post/skills/post/scripts/check.py out/<slug>.xhtml
```

```
out/mtfs-zone-bench.xhtml: 142줄, 6,318자

OK
```

잡아내는 것: 이스케이프 안 된 `&` 와 `<`, 알 수 없는 엔티티, 본문의 `]]>`, 깨진 XML,
`<html>`·DOCTYPE, `<thead>`(WARN), `<li>` 밖의 중첩 목록, 확인 안 된 매크로,
미확인 code 언어, 제목 단계, `<p>` 밖의 PlantUML, MCP 조회 결과에서 그대로 옮긴
첨부 이미지, 첨부가 필요한 이미지 목록. ERROR가 있으면 종료 코드 1이고,
그 파일은 붙여넣지도 MCP 로 올리지도 않는다.

`--probe` 는 미확인 매크로를 ERROR 대신 WARN으로 낮춘다. probe 페이지 전용이다.
`--h1` 은 본문을 h1 부터 쓰는 페이지에 이어 붙일 때 준다. h1 WARN 을 끈다.

```bash
python3 .../scripts/check.py --probe probe/P1-languages.xhtml
```

## 파일

| 경로 | 용도 |
|---|---|
| `.claude-plugin/marketplace.json` | 마켓플레이스 정의 |
| `plugins/confluence-post/` | 플러그인. 스킬 하나를 담는다 |
| `.../skills/post/SKILL.md` | 스킬 본체 |
| `.../reference/storage-format.md` | markdown → storage format 매핑 |
| `.../reference/plantuml.md` | PlantUML 문법 규칙과 쓰지 않는 것 |
| `.../reference/existing-page.md` | MCP 로 기존 페이지 읽기, 옮기면 안 되는 자리, 게시 |
| `.../reference/example.xhtml` | 완성된 예시 (벤치 보고 한 장) |
| `.../scripts/check.py` | 조각 검사기. 넣기 전에 돌린다 |
| `probe/ANSWER.md` | 1차 실측 응답표 |
| `probe/ANSWER-P.md` | 2차 응답표 — P1~P3, P5 렌더링 결과 |
| `probe/P1-languages.xhtml` | code 언어 22종 + 대조군 |
| `probe/P2-macros.xhtml` | 매크로 22종 + 대조군 |
| `probe/P3-structure.xhtml` | 표·링크·이스케이프·중첩 12항목 |
| `probe/P4-plantuml.xhtml` | PlantUML 다이어그램 타입 |
| `probe/P5-mcp.xhtml` | MCP 로 올려 확인한 매크로·PlantUML 배치·언어·표·체크박스 |
| `probe/optional/` | wiki markup 전수 probe. 경로를 바꾸게 되면 사용 |
| `out/` | 스킬이 만든 조각 파일 |
