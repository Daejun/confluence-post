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
| `probe/ANSWER.md` | 1차 실측 응답표. B 완료 |
| `probe/PROBE-min.txt` | B단계 입력 (완료) |
| `probe/ANSWER-P.md` | 2차 응답표 — P1~P3 렌더링 결과를 받는다 |
| `probe/P1-languages.xhtml` | code 언어 22종 + 대조군. A3을 렌더링으로 대체 |
| `probe/P2-macros.xhtml` | 매크로 22종 + 대조군. A4를 렌더링으로 대체 |
| `probe/P3-structure.xhtml` | 표·링크·이스케이프·중첩 12항목 |
| `probe/optional/` | wiki markup 전수 probe. 경로를 바꾸게 되면 사용 |
| `out/` | 스킬이 만든 조각 파일 |

## 남은 것 — P1~P3 렌더링

사내 PC 안에서는 붙여넣기가 되므로, 메뉴를 읽는 대신 직접 렌더링해서 확인한다.
각 페이지에 항목 라벨(L01, M01, S01)이 그대로 찍히므로 화면 캡처로 판독된다.
응답은 `probe/ANSWER-P.md`.

이 결과가 오기 전에는 스킬이 보수적으로 동작한다 — 미확인 매크로를 쓰지 않고,
`c` 외의 언어는 `text`로 낸다.

각 페이지에 대조군이 있다. P1은 없는 언어(L00), P2는 없는 매크로(M99). 지원되는 것과
기본값으로 떨어진 것을 그 둘과 비교해 가른다.

## 검사기

```bash
python3 skills/confluence-post/scripts/check.py out/<slug>.xhtml
python3 skills/confluence-post/scripts/check.py --probe probe/P1-languages.xhtml
```

`--probe` 는 미확인 매크로를 ERROR 대신 WARN으로 낮춘다. probe 페이지 전용이다.

잡아내는 것: 이스케이프 안 된 `&`, 알 수 없는 엔티티, 본문의 `]]>`, 깨진 XML,
`<thead>`·`<html>`·DOCTYPE, `<li>` 밖의 중첩 목록, 확인 안 된 매크로,
미확인 code 언어, 첨부가 필요한 이미지 목록. ERROR가 있으면 종료 코드 1.
