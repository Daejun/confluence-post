# confluence-post

사내 Confluence(Data Center)에 문서를 올릴 때 쓸 **문법 가이드 스킬**을 만들기 위한 저장소.

Confluence DC는 Cloud의 fabric 에디터가 아니라 legacy 에디터 + storage format(XHTML)을
쓴다. 무엇이 실제로 렌더링되는지를 **실측한 뒤에** 스킬 규칙을 쓴다.

## 현재 상태

probe 단계. 스킬은 아직 없다.

정해진 것:
- **출력 형식: storage format (XHTML).** 사내 Confluence에 Edit Source가 있으므로
  wiki markup과 markdown insert를 둘 다 우회한다. 단일 개행 처리, `_` 이스케이프,
  표 셀의 `|` 이스케이프는 전부 wiki markup 파서 문제라 여기서는 발생하지 않는다.
- 게시 경로: Edit Source에 직접 입력
- 스킬 입력: 기존 markdown 변환 + 처음부터 작성, 둘 다 지원
- markdown insert 경로는 쓰지 않는다
- 사내망에서 복사·붙여넣기가 안 되므로 probe는 손으로 옮겨 적을 수 있는 크기여야 한다

## 파일

| 경로 | 용도 |
|---|---|
| `probe/ANSWER.md` | 응답표. **여기부터 읽는다.** A(타이핑 0) → B(8줄) |
| `probe/PROBE-min.txt` | B단계 입력. Edit Source에 그대로 입력하는 storage format |
| `probe/optional/` | wiki markup 전수 probe(249줄). 경로를 바꾸게 되면 사용 |

## probe가 결정하는 것

- Code Block macro의 언어 목록에 `c`가 있는가 → 커널 코드를 `cpp`로 매핑할지
- 설치된 매크로 → 도식을 무엇으로 그릴지, expand·status·toc를 쓸 수 있는지
- 기존 사내 페이지의 storage format → 사내가 실제로 쓰는 매크로·파라미터 어휘
- 표 셀 안에 code 매크로가 들어가는가 → 벤치 결과 표에 커맨드를 넣을 수 있는지
- 저장 시 Confluence가 XHTML을 다시 쓰는가 → 스킬이 낼 XHTML 형태
