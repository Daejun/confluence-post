# confluence-post

## 설치

```
/plugin marketplace add Daejun/confluence-post
/plugin install confluence-post@confluence-post
```

`/plugin update confluence-post` 로 갱신한다.

스킬을 직접 고치면서 쓰려면 플러그인 대신 clone + symlink 를 쓴다. 저장소를 고치는 즉시
반영된다(두 방식을 같이 쓰면 스킬이 둘로 잡히니 하나만 고른다).

```bash
git clone https://github.com/Daejun/confluence-post.git ~/confluence
ln -s ~/confluence/plugins/confluence-post/skills/confluence-post ~/.claude/skills/confluence-post
```

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
| `.claude-plugin/marketplace.json` | 마켓플레이스 정의 |
| `plugins/confluence-post/` | 플러그인. 스킬 하나를 담는다 |
| `.../skills/confluence-post/SKILL.md` | 스킬 본체 |
| `.../reference/storage-format.md` | markdown → storage format 매핑 |
| `.../reference/example.xhtml` | 완성된 예시 (벤치 보고 한 장) |
| `.../scripts/check.py` | 조각 검사기. 넣기 전에 돌린다 |
| `probe/ANSWER.md` | 1차 실측 응답표. B 완료 |
| `probe/PROBE-min.txt` | B단계 입력 (완료) |
| `probe/ANSWER-P.md` | 2차 응답표 — P1~P3 렌더링 결과를 받는다 |
| `probe/P1-languages.xhtml` | code 언어 22종 + 대조군. A3을 렌더링으로 대체 |
| `probe/P2-macros.xhtml` | 매크로 22종 + 대조군. A4를 렌더링으로 대체 |
| `probe/P3-structure.xhtml` | 표·링크·이스케이프·중첩 12항목 |
| `probe/optional/` | wiki markup 전수 probe. 경로를 바꾸게 되면 사용 |
| `out/` | 스킬이 만든 조각 파일 |

## 실측 결과 (`probe/ANSWER-P.md`)

**code 언어 22종 전부 하이라이팅** — `c` `cpp` `diff` `bash` `shell` `text` `none`
`python` `py` `java` `js` `javascript` `json` `yaml` `xml` `sql` `rust` `go`
`perl` `powershell` `makefile` `ruby`. `title` `linenumbers` `collapse` 동작.

**쓸 수 있는 매크로** — `code` `expand` `info` `note` `warning` `tip` `panel`
`toc` `status` `noformat` `anchor` `plantuml` `latex` `attachments`
`recently-updated`

**쓸 수 없는 매크로** — `mermaid` `mermaid-cloud` `mathblock` `gliffy`
`excerpt` `children`

**조건부** — `drawio` 는 설치돼 있으나 에디터에서 그려야 해 XHTML로 저작할 수 없다.
`jira` 는 실제 이슈 키로만 렌더링된다.

**구조** — 3단 중첩 목록, 8열 표(안 잘림), 표 셀 안 code·expand, 긴 코드 한 줄,
링크 4종, 이스케이프, h2~h5 전부 정상.

### 도식

PlantUML을 쓸 수 있다. 소스가 평문이라 XHTML에 그대로 담긴다. 다만 기본은 도식 없음이고
(전역 게시물 규칙), 요구가 있을 때만 낸다. ASCII 도식은 어느 경우에도 내지 않는다.

### 남은 미확인

- P1 대조군(없는 언어 `zzznotalang`)이 어떻게 보였는지. 대조군도 색이 났다면 22종 중
  일부는 기본 brush로 떨어진 것일 수 있다. 결과는 색이 안 나는 것뿐이라 위험은 낮다.
- Confluence 버전, space key, 초안을 둘 부모 페이지

## 검사기

```bash
python3 skills/confluence-post/scripts/check.py out/<slug>.xhtml
python3 skills/confluence-post/scripts/check.py --probe probe/P1-languages.xhtml
```

`--probe` 는 미확인 매크로를 ERROR 대신 WARN으로 낮춘다. probe 페이지 전용이다.

잡아내는 것: 이스케이프 안 된 `&`, 알 수 없는 엔티티, 본문의 `]]>`, 깨진 XML,
`<thead>`·`<html>`·DOCTYPE, `<li>` 밖의 중첩 목록, 확인 안 된 매크로,
미확인 code 언어, 첨부가 필요한 이미지 목록. ERROR가 있으면 종료 코드 1.
