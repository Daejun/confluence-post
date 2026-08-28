# confluence-post

사내 Confluence(Data Center)에 문서를 올릴 때 쓸 **문법 가이드 스킬**을 만들기 위한 저장소.

Confluence DC는 Cloud의 fabric 에디터가 아니라 legacy 에디터 + storage format(XHTML)을
쓰므로, markdown을 그대로 붙여넣으면 표부터 깨진다. 무엇이 실제로 렌더링되는지를
**실측한 뒤에** 스킬 규칙을 쓴다.

## 현재 상태

probe 단계. 스킬은 아직 없다.

정해진 것:
- 게시 경로: 에디터에 직접 붙여넣기 (Insert > Markup > Confluence Wiki)
- 스킬 입력: 기존 markdown 변환 + 처음부터 작성, 둘 다 지원
- 사내망에서 복사·붙여넣기가 안 되므로 probe는 손으로 옮겨 적을 수 있는 크기여야 한다

## 파일

| 경로 | 용도 |
|---|---|
| `probe/ANSWER.md` | 응답표. **여기부터 읽는다.** A(타이핑 0) → B(22줄) → C(9줄) 순서 |
| `probe/PROBE-min.txt` | B단계 입력. Insert > Markup > Confluence Wiki 에 그대로 입력 |
| `probe/PROBE-min-markdown.txt` | C단계 입력. Markdown 선택지가 있을 때만 |
| `probe/optional/` | 26항목 전수 probe(249줄). 붙여넣기가 가능해지면 사용 |

## probe가 결정하는 것

- 단일 개행이 줄바꿈인가 문단 이어붙임인가 → 변환기가 md 문단을 합쳐야 하는지
- Code Block macro의 언어 목록에 `c`가 있는가 → 커널 코드를 `cpp`로 매핑할지
- 표 셀에서 `\|` 이스케이프가 되는가 → 표 안에 커맨드라인을 넣을 수 있는지
- plantuml/draw.io/mermaid 중 설치된 것 → 도식을 무엇으로 그릴지
- markdown insert가 표를 변환하는가 → md를 그대로 넘기는 경로가 사는지
