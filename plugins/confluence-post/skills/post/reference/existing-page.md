# 기존 페이지 읽기와 게시 — Confluence MCP

`mcp__confluence-mcp__*` 도구가 있으면 쓴다. 없거나 실패하면 이 파일의 내용 대신
사용자에게 Edit Source 내용을 한 번 요청하고, 게시는 붙여넣기 안내로 끝낸다.
**MCP 는 best effort 다** — 파일이 산출물이고, MCP 는 그 파일을 옮기는 수단일 뿐이다.

## 호출은 적게, 재시도는 하지 않는다

사내 REST 정책은 **Agent·MCP 서버를 통한 호출을 분당 15회로 제한**한다. 넘으면 429 가
오고, 불필요한 반복 호출은 모니터링해 **계정을 비활성화할 수 있다.** MCP 는 사용자의
PAT 로 돈다 — 위험은 사용자 계정에 간다.

- 한 번 실행에 필요한 호출은 몇 번이면 된다: 고칠 페이지 읽기 1, (필요하면) 형제 목록 1,
  링크 확인 1(제목 여러 개를 CQL 하나로 묶는다), (개정이면) 올리기 직전 version 확인 1,
  올리기 1, 다시 읽기 1.
- **429·502·타임아웃이 나면 재시도 루프를 돌지 않는다.** 한 번 멈추고 사용자에게 알린 뒤
  파일 전달로 넘어간다.
- 여러 페이지를 훑는 조사, 서브에이전트로 나눠 동시에 부르는 호출을 하지 않는다.
- 서버에 시험 페이지를 만들어 매크로를 넣어 보는 것은 사용자가 요청했을 때만, 한두 개씩
  한다. **조회형 매크로는 시험으로 넣지 않는다** — 범위 없이 여럿 넣은 시험 페이지가
  열리지 않은 일이 있다(원인을 따로 떼어 확인하지는 않았다). `reference/storage-format.md`
  의 조회형 절.

## 읽기

URL 에서 page ID 를 뽑는다.

| URL 형태 | 읽는 법 |
|---|---|
| `.../pages/viewpage.action?pageId=<ID>` | `get_page(page_id=<ID>)` |
| `.../spaces/<KEY>/pages/<ID>/<제목>` | `get_page(page_id=<ID>)` |
| `.../display/<KEY>/<제목>` | `get_page(title=<제목>, space_key=<KEY>)` (`+` 는 공백) |

```
mcp__confluence-mcp__get_page(page_id=<ID>, convert_to_markdown=false, include_metadata=true)
```

- **`convert_to_markdown=false` 를 반드시 준다.** markdown 변환본은 매크로 파라미터
  값을 본문에 붙여 버린다(`INLINE@startuml…`, toc 가 `2` 로만 남는다). 관례를 읽을 수
  없다.
- markdown 이든 아니든 **렌더링 결과가 아니라 저장된 소스**다. 매크로가 실제로
  그려지는지, 미설치 매크로 오류가 나는지는 MCP 로 알 수 없다.
- metadata 에서 `space.key`, `version`, `title` 을 쓴다. 부모 아래 형제 페이지는
  `get_page_children(parent_id=<ID>)`.
- `confluence_access_forbidden` 이면 **다시 부르지 않는다.** 극비·국핵 space 는 외부 AI
  Agent 에 반환되지 않도록 막혀 있고, 그 내용을 외부 LLM 에 넘기는 것도 사내 보안 정책상
  금지다. 그래서 **사용자에게 내용을 붙여 달라고도 하지 않는다.** 기본 관례로 쓰고 초안
  첫 줄에 "기존 페이지를 읽지 못했다(접근 제한)"고 적는다.

## 읽은 소스를 그대로 옮기면 안 되는 자리

MCP 응답은 storage 원문과 다른 곳이 있다. 이 부분을 그대로 `update_page` 에 넣으면
페이지가 깨진다.

| MCP 응답에 보이는 것 | 원래 형태 | 처리 |
|---|---|---|
| `<img src=".../download/attachments/<ID>/<파일>">` | `<ac:image><ri:attachment ri:filename="<파일>"/></ac:image>` | 원래 형태로 되돌린다. check.py 가 ERROR 로 막는다 |
| `@이름` 평문 | 사용자 멘션(`<ri:user>`)일 수 있다 (미확인) | 멘션이었는지 확인할 수 없으면 초안에 밝힌다 |

## 에디터가 남긴 흔적

Edit Source 로 저장하면 XHTML 이 그대로 남지만, **일반 편집 화면으로 한 번이라도
저장된 페이지**에는 아래가 붙어 있다.

| 흔적 | 같은 페이지를 개정할 때 | 다른 페이지를 본떠 새로 만들 때 |
|---|---|---|
| `ac:macro-id`, `ac:schema-version` | 둔다 | 지운다. 저장 시 새로 붙는다 |
| `data-uuid` (`<li>` 등) | 둔다 | 지운다 |
| `class=""`, `<span style="font-family:…">`, `style="letter-spacing:…"` | 둔다 | 지운다 |
| `<ac:inline-comment-marker>` | **둔다.** 지우면 달린 코멘트가 고아가 된다 | 태그만 벗기고 글자는 남긴다 |
| plantuml 의 `atlassian-macro-output-type` | 둔다 | 지운다. 값과 상관없이 렌더링이 같다 |
| `<ac:macro ac:name="…">` (옛 형식) | 이름이 설치 안 된 매크로면 저장 때 바뀐 흔적이고 본문은 이미 없다 — 사용자에게 알린다. 아는 매크로면 오래된 페이지의 옛 형식이다 — `ac:structured-macro` 로 바꾼다 | 옮기지 않는다 |

새로 쓰는 부분에는 이런 것을 만들어 넣지 않는다.

## 따를 관례

내 형식을 새로 만들지 않는다. 읽은 페이지에서 아래를 보고 그대로 쓴다.

- 본문 첫 제목 단계 (h1 / h2), 절 이름과 번호 매기기
- toc 사용 여부와 `maxLevel`
- code 매크로 파라미터 (`title` `linenumbers` `collapse`)
- 표 헤더 행 형태 (`<th>` 위치)

## 게시

8단계 승인을 받을 때 **어디에 올리는지(새 페이지의 부모, 또는 고칠 페이지)를 같이
보여주고 승인받는다.** 승인 없이 올리지 않는다. 대상을 모르면 그때 한 번 묻는다.
답이 없으면 붙여넣기 안내로 끝낸다.

**content 는 check.py 를 통과한 파일을 그대로 읽어 넣는다.** 넣기 직전에 다시 쓰거나
고치지 않는다 — 고칠 게 있으면 파일을 고치고 check.py 를 다시 돌린다.

새 페이지:
```
mcp__confluence-mcp__create_page(space_key=<KEY>, parent_id=<부모 ID>, title=<제목>,
                                 content=<파일 내용>, content_format="storage")
```
MCP 에는 삭제 도구가 없다. 잘못 만든 페이지는 사용자가 지워야 한다 — 제목과 부모를
승인받은 그대로 쓴다.

개정:
```
mcp__confluence-mcp__update_page(page_id=<ID>, title=<제목>,
                                 content=<파일 내용>, content_format="storage")
```
- **본문 전체를 덮어쓴다.** 기존 내용에 덧붙이는 것이면 파일이 기존 본문 전체를
  담고 있어야 한다.
- **올리기 직전에 `version` 을 다시 본다.** 읽었을 때와 다르면 그 사이 누가 고친
  것이다. 덮어쓰지 않고 다시 읽어 합친 뒤 승인을 다시 받는다.
- 페이지를 고치면 watcher 전원에게 메일이 간다. 올린 직후 사소한 것을 고쳐 다시 올릴
  때는 `is_minor_edit=true` 로 알림을 줄인다. 내용이 바뀐 개정은 minor 로 올리지 않는다.

**올리기가 서버 오류로 실패하면** 파일의 매크로를 먼저 의심한다. 필수 파라미터가 빠진
매크로 하나 때문에 페이지 생성 전체가 실패할 수 있다(첨부를 가리키는 multimedia·
view-file·viewpdf 를 첨부 없이 넣으면 서버가 NullPointerException 을 낸다). 같은 내용으로
다시 부르지 않는다.

저장하면서 Confluence 가 내용을 바꾸는 경우도 있다. 다시 읽을 때 본다.
- 사용자를 지정하지 않은 profile 매크로는 `[User Profile Macro (Malformed)]` 글자로 바뀐다.
- 매크로 파라미터 안의 페이지 링크가 **저장 시점에 없는 페이지**를 가리키면 링크가 비워진다
  (`<ac:link></ac:link>`). 같은 페이지를 가리키는 링크는 페이지를 만든 뒤 다시 올려야 남는다.
- 첨부는 페이지당 100개·합계 50MB 이하, 파일 하나 50MB 미만이다(사내 운영 기준).

올린 뒤:
- `get_page(convert_to_markdown=false)` 로 다시 읽어 제목·매크로 개수가 파일과 같은지
  본다. 위 표의 이미지·멘션 변환 때문에 글자 단위로는 같지 않다.
- **다시 읽은 원문에 `<ac:macro ac:name="…">` 가 있으면 그 매크로는 설치돼 있지 않다.**
  Confluence 는 설치된 매크로를 `ac:structured-macro` 로 두고 `ac:macro-id`·
  `ac:schema-version` 을 붙이지만, 모르는 매크로는 `<ac:macro>` 로 바꾸고 plain-text
  본문을 지운다. 렌더링을 보지 않고도 알 수 있는 유일한 신호다. 보이면 사용자에게 알리고,
  파일에서 그 매크로를 빼 다시 올린다.
- 페이지 URL 을 주고 **브라우저에서 한 번 봐 달라고** 한다. 렌더링은 MCP 로 확인할 수
  없다. PlantUML 이 있으면 특히.
- 첨부가 필요한 이미지가 있으면 목록을 준다. MCP 로는 첨부를 올릴 수 없다.
