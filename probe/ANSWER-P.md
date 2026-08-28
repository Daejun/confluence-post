# P1~P3 렌더링 응답표

사내 PC 안에서 붙여넣기가 되므로, 메뉴를 읽는 대신 **직접 렌더링해서** 확인한다.
세 페이지로 나눴다 — 하나가 저장을 거부해도 나머지는 살아남는다.

각 페이지를 개인 space에 새로 만들고 Edit Source에 파일 내용을 붙여넣고 저장한다.
**항목 라벨(L01, M01, S01)이 화면에 그대로 나오므로 화면 캡처만 주셔도 됩니다.**

---

# 결과 (2026-08-28)

## P1 — code 언어: 시험한 22종 전부 하이라이팅됨

`c` `cpp` `diff` `bash` `shell` `text` `none` `python` `py` `java` `js`
`javascript` `json` `yaml` `xml` `sql` `rust` `go` `perl` `powershell`
`makefile` `ruby`. `title` `linenumbers` `collapse` 도 동작.

미확인: 대조군 L00(`zzznotalang`)이 어떻게 보였는지. 대조군도 색이 났다면 위 중
일부는 기본 brush로 떨어진 것일 수 있다. 결과는 색이 안 나는 것뿐이라 위험은 낮다.

## P2 — 매크로

**쓸 수 있다**: `code` `expand` `info` `note` `warning` `tip` `panel` `toc`
`status` `noformat` `anchor` `plantuml` `latex` `attachments` `recently-updated`

**쓸 수 없다**: `mermaid` `mermaid-cloud` `mathblock` `gliffy` `excerpt` `children`

**조건부**
- `drawio` — "알 수 없는 매크로"가 아니라 **오류**가 났다. 즉 설치돼 있고,
  probe가 없는 다이어그램 이름(`test`)을 가리켜 난 오류다. 다만 에디터에서 그려야
  하므로 XHTML로 저작할 수 없다.
- `jira` — 매크로는 있다. 실제 이슈 키로만 렌더링된다.

`excerpt`·`children`은 보여줄 내용이 없어 비어 보인 것일 수도 있다. 스킬에서 안 쓰므로
구분하지 않았다.

## P3 — 구조: 전 항목 정상

3단 중첩 목록, 8열 표(안 잘림), 표 셀 안 code·expand, 긴 코드 한 줄,
code 파라미터 3종, 링크 4종, 첨부 없는 이미지, blockquote·hr, 인라인 서식,
본문·CDATA 이스케이프, h2~h5, 긴 한글 문단.

## 이 결과가 스킬에 반영된 곳

- `skills/confluence-post/SKILL.md` — 확정된 환경, 도식 정책
- `skills/confluence-post/reference/storage-format.md` — 언어 목록, PlantUML
- `skills/confluence-post/scripts/check.py` — CONFIRMED / UNAVAILABLE / TESTED_LANGS
