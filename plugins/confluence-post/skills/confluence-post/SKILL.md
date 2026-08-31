---
name: confluence-post
description: 사내 Confluence(Data Center)에 올릴 문서를 storage format(XHTML)으로 만든다. 기존 markdown을 변환하거나 처음부터 작성해 Edit Source에 그대로 넣을 조각 파일을 낸다. Use when the user asks to write or convert a document for 사내 컨플루언스/Confluence, says "컨플루언스에 올릴 것", "컨플루언스 문법으로 바꿔줘", or asks to prepare a page for Confluence DC.
---

# 사내 Confluence 게시물 만들기

산출물은 **storage format(XHTML) 조각 파일** 하나다. 사용자가 그것을 사내 Confluence의
**Edit Source**에 넣는다. wiki markup(`h1.`, `{code}`)과 markdown insert는 쓰지 않는다 —
Edit Source가 있어 둘 다 우회하고, 그 두 경로에만 있는 파서 함정을 피한다.

조각이므로 `<!DOCTYPE>`, `<html>`, `<body>`를 쓰지 않는다. 최상위는 `<p>`, `<h2>`,
`<table>`, `<ac:structured-macro>` 같은 요소들이 나열된 형태다.

## 확정된 환경 (2026-08-28 실측)

probe로 직접 렌더링해 확인한 것. 추측이 아니다.

**기본**
- Edit Source 편집·저장 가능. 저장해도 Confluence가 XHTML을 다시 쓰지 않는다
- 표 `<td>` 안에 code·expand 매크로가 들어간다
- CDATA 안의 `&` `<` `|` 가 그대로 나온다
- 8열 표, 긴 코드 한 줄, 3단 중첩 목록, h2~h5, blockquote, hr, 인라인 서식,
  외부·앵커·페이지 링크, 본문 이스케이프 — 전부 정상

**code 언어 — 시험한 22종이 전부 하이라이팅된다**
`c` `cpp` `diff` `bash` `shell` `text` `none` `python` `py` `java` `js`
`javascript` `json` `yaml` `xml` `sql` `rust` `go` `perl` `powershell`
`makefile` `ruby`. `cpp` 우회가 필요 없다. 이 목록 밖 언어는 `text`로 낸다.

`title` `linenumbers` `collapse` 파라미터도 동작한다.

**쓸 수 있는 매크로**
`code` `expand` `info` `note` `warning` `tip` `panel` `toc` `status`
`noformat` `anchor` `plantuml` `latex` `attachments` `recently-updated`

**쓸 수 없는 매크로 (렌더링 안 되는 것을 확인)**
`mermaid` `mermaid-cloud` `mathblock` `gliffy` `excerpt` `children`

**조건부**
- `drawio` — 설치돼 있다(미설치가 아니라 오류가 났다). 다만 다이어그램을 에디터에서
  그려야 하므로 XHTML로 저작할 수 없다. 스킬이 내지 않는다.
- `jira` — 매크로는 있다. 실제 이슈 키로만 렌더링된다.

## 도식

**PlantUML을 쓸 수 있다.** 사내 서버는 **1.2024.8** 이다.
문법 규칙과 쓰지 않는 것은 `reference/plantuml.md` 에 있다 — 도식을 낼 때 그 파일을 읽는다.
소스가 평문이라 XHTML 안에 그대로 담긴다.

check.py 는 문법 규칙(뼈대, 금지 구문, 다이어그램 타입)만 정적으로 본다. 실제로 그려지는지는
사내 서버에 넣어 봐야 안다. 도식을 낸 초안에는 그 점을 밝힌다.

```xml
<ac:structured-macro ac:name="plantuml"><ac:plain-text-body><![CDATA[@startuml
A -> B: write
@enduml]]></ac:plain-text-body></ac:structured-macro>
```

다만 **기본은 도식 없음**이다. 전역 게시물 규칙이 도식을 빼도록 되어 있다.
사용자가 도식을 요구했을 때만 PlantUML로 낸다. ASCII 도식은 어느 경우에도 내지 않는다.

## 아직 확인 안 된 것

- P1의 대조군(없는 언어 `zzznotalang`)이 어떻게 보였는지 확인하지 않았다.
  대조군도 색이 났다면 위 22종 중 일부는 기본 brush로 떨어진 것일 수 있다.
  결과는 색이 안 나는 것뿐이라 위험은 낮다.
- Confluence 버전, space key, 초안을 둘 부모 페이지
- 사내가 실제로 쓰는 매크로·파라미터 어휘 (기존 페이지 Edit Source)

## 순서

1. **입력을 정한다.** 변환할 markdown 파일 경로가 있으면 읽는다. 없으면 새로 쓴다.
   어느 쪽인지 한 줄로 밝히고 시작한다.

2. **내용을 게시물 규칙으로 줄인다.** 전역 CLAUDE.md의 "게시물" 규칙이 그대로 적용된다.
   사실·근거·요청만 남긴다. 근거는 `파일:줄`, 커밋 SHA, 측정치 + 조건.
   빼는 것: 배경 설명, 용어 정의, 경위 서술, 날짜 서술, 감상, 대안 기각 목록, 인사말,
   자기 요약 절. **ASCII 도식도 뺀다** — 표나 문장으로 바꾼다. 도식이 꼭 필요하다고
   사용자가 말했을 때만 PlantUML로 낸다.

3. **변환한다.** 매핑은 `reference/storage-format.md`, 완성된 예시는
   `reference/example.xhtml`. 외우지 말고 두 파일을 읽는다.
   `colspan` 처럼 probe로 확인하지 않은 것은 쓰지 않는다.

4. **`out/<slug>.xhtml` 에 쓴다.** 기준은 **현재 작업 디렉터리**다 — 원본 markdown이
   있는 곳도, 스킬이 설치된 곳도 아니다. slug은 영문 kebab-case.
   현재 디렉터리에 쓸 수 없으면 scratchpad에 쓴다. 어느 쪽이든 **절대 경로로** 알린다.

5. **검증한다.** 검사기는 이 SKILL.md 와 같은 디렉터리의 `scripts/check.py` 다.
   설치 형태에 따라 절대 경로가 다르니 한 번 찾아서 쓴다.
   ```bash
   CHECK=$(find -L ~/.claude -path "*confluence-post/scripts/check.py" 2>/dev/null | head -1)
   python3 "$CHECK" out/<slug>.xhtml
   ```
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
     toc 가 어긋난다.
   - **덩어리가 보존됐는가.** 목록의 중첩 단계, 표의 열 수와 헤더 행, 코드 블록의 개수와
     언어가 원문과 같은가. 원문에서 코드였던 것이 문단으로, 표였던 것이 목록으로
     뭉개지지 않았는가.
   - **이어 붙일 페이지가 있으면 그 페이지의 관례를 따른다.** 개정이거나 기존 페이지에
     덧붙이는 것이면 그 페이지의 Edit Source 를 먼저 본다. 제목을 h2 부터 쓰는지 h3
     부터 쓰는지, 절 이름, toc 사용 여부, code 매크로 파라미터(`title` `linenumbers`
     `collapse`) 관례를 그대로 쓴다. 내 형식을 새로 만들지 않는다.
     **그 페이지를 못 구했으면 사용자에게 한 번 요청한다.** 그래도 없으면 기본
     관례(본문 h2 시작, toc 없음, code 파라미터는 language 만)로 쓰고, 초안 첫 줄에
     "기존 페이지 관례를 대조하지 못했다"고 적는다. 혼자 절충안을 만들지 않는다.

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
   다시 보여준다.

9. **전달한다. 여기까지가 이 스킬의 끝이다** — 산출물은 XHTML 파일 한 장이고,
   Confluence 에 넣는 것은 사용자가 한다.

   **넣는 방법을 이 문장 그대로 적는다.** `<파일명>` 자리에 실제 산출물 이름을 넣는다.

   > 페이지 작성 화면에서 오른쪽 위의 `< >` 를 눌러 `<파일명>` 출력물을 넣어주세요.

   그 다음 줄에 파일 경로와 **줄 수·문자 수**를 적는다. 분량이 곧 옮기는 비용이다.
   길면 어디서 끊어 나눠 넣을지 같이 알려준다.

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
- **미설치 매크로를 쓰지 않는다.** mermaid·mathblock·gliffy는 렌더링되지 않는다.
  check.py가 ERROR로 걸러낸다.
- **PlantUML 소스에 `]]>` 가 들어가지 않게 한다.** CDATA가 거기서 끊긴다.
- **CDATA 안을 들여쓰지 않는다.** 요소 사이 들여쓰기는 렌더링에 영향이 없지만,
  CDATA 안의 공백은 코드 내용 그 자체다. `<![CDATA[` 바로 뒤부터 내용을 시작하고
  `]]>` 는 마지막 줄 끝에 붙인다. 코드 자체의 들여쓰기(커널이면 탭)는 그대로 살린다.
