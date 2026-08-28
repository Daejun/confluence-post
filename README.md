# confluence-post

사내 Confluence(Data Center)에 문서를 올릴 때 쓰는 **문법 가이드 스킬**과, 그 근거가 된
렌더링 실측 probe.

## 확정된 것 (2026-08-28 실측)

출력 형식은 **storage format (XHTML)** 이다. 사내 Confluence에 Edit Source가 있어
wiki markup과 markdown insert를 둘 다 우회한다. 그 두 경로에만 있는 파서 함정
(단일 개행 처리, `_` 이스케이프, 표 셀의 `|` 이스케이프)이 전부 사라진다.

probe로 직접 확인한 것:

- Edit Source 편집·저장 가능
- 표 `<td>` 안에 code 매크로가 들어간다
- CDATA 안의 `|` 가 그대로 나온다
- `language="c"` 가 하이라이팅된다 — 커널 코드에 `cpp` 우회가 필요 없다
- expand가 접힌 상태로 나온다
- 저장해도 Confluence가 XHTML을 다시 쓰지 않는다

## 파일

| 경로 | 용도 |
|---|---|
| `skills/confluence-post/SKILL.md` | 스킬 본체. `~/.claude/skills/confluence-post` 가 여기를 symlink |
| `skills/confluence-post/reference/storage-format.md` | markdown → storage format 매핑 |
| `skills/confluence-post/scripts/check.py` | 조각 검사기. 넣기 전에 돌린다 |
| `probe/ANSWER.md` | 실측 응답표. B는 완료, **A가 남았다** |
| `probe/PROBE-min.txt` | B단계 입력 (완료) |
| `probe/optional/` | wiki markup 전수 probe. 경로를 바꾸게 되면 사용 |
| `out/` | 스킬이 만든 조각 파일 |

## 남은 것 — probe A (타이핑 0)

A가 채워지기 전에는 스킬이 보수적으로 동작한다. 미확인 매크로를 쓰지 않고,
`c` 외의 언어는 `text`로 낸다.

- A3 Code Block macro의 전체 언어 목록
- A4 설치된 3rd-party 매크로 (plantuml / draw.io / mermaid / latex)
- A5 기존 사내 페이지의 storage format — 사내가 실제로 쓰는 매크로·파라미터 어휘
- A1 버전, A6 PAT 메뉴 유무, A7 space key

## 검사기

```bash
python3 skills/confluence-post/scripts/check.py out/<slug>.xhtml
```

잡아내는 것: 이스케이프 안 된 `&`, 알 수 없는 엔티티, 본문의 `]]>`, 깨진 XML,
`<thead>`·`<html>`·DOCTYPE, `<li>` 밖의 중첩 목록, 확인 안 된 매크로,
미확인 code 언어, 첨부가 필요한 이미지 목록. ERROR가 있으면 종료 코드 1.
