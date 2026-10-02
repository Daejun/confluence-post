# probe 응답표 — 빈칸만 채워 주세요

경로는 **storage format(XHTML)을 Edit Source에 직접 넣기**로 확정했다.
markdown 경로와 wiki markup 파서 테스트는 뺐다 — Edit Source가 있으면 둘 다 우회한다.

B는 끝났다(아래). **남은 것은 A뿐이고, A는 타이핑이 없다.**
A가 채워지면 코드 언어 매핑과 도식 정책이 확정된다.

---

## A. 화면에서 읽어 적기 (타이핑 0)

A1. Confluence 버전 — 도움말(?) > About Confluence, 또는 페이지 맨 아래
    → 

A2. Edit Source 화면이 **편집 가능한가, 읽기 전용인가.**
    내용을 고쳐서 저장까지 되면 "편집 가능", 보기만 되면 "읽기 전용".
    읽기 전용이면 B는 무의미하니 그 사실만 알려 주세요.
    → 

A3. **Code Block macro의 Language 드롭다운 목록 전부.** 매크로 삽입 > Code Block > Language.
    보이는 대로 옮겨 적어 주세요. `c` 유무가 커널 문서에서 매번 걸립니다.
    → 

A4. 매크로 브라우저({ 입력 또는 매크로 삽입)에서 검색해 **있는 것에만** 표시
    → expand □   toc □   info/note/warning/tip □   panel □   status □
       plantuml □   draw.io □   mermaid □   latex/math □   jira issue □

A5. **여기가 가장 값이 큽니다.** 사내에서 잘 쓰인 페이지 중 **표와 코드 블록이 둘 다 있는**
    페이지를 하나 골라 Edit Source로 엽니다. 아래만 적어 주세요 (전문 필요 없음).
    - 나오는 `<ac:structured-macro ac:name="___">` 의 **이름 전부**
      → 
    - code 매크로가 쓰는 `<ac:parameter ac:name="___">` 의 **이름 전부**
      (language / title / linenumbers / collapse / theme 중 무엇이 실제로 쓰이는지)
      → 
    - 표가 `<table>` + `<th>` 를 쓰는가, 아니면 전부 `<td>` 인가
      → 
    - 눈에 띄는 사내 고유 태그·매크로가 있으면
      → 

A6. 프로필 메뉴에 Personal Access Tokens 항목이 있는가 (나중에 API 자동화 여지)
    → 있음 / 없음

A7. 내 space key, 초안을 둘 부모 페이지
    → 

---

## B. 8줄 타이핑 — 완료 (2026-08-28)

`PROBE-min.txt` 를 Edit Source에 넣어 확인. **B1~B6 전부 통과.**

| | 확인한 것 | 결과 |
|---|---|---|
| B1 | 손으로 쓴 storage format이 저장되는가 | 됨 |
| B2 | 표 `<td>` 안의 code 매크로 | 표 안에 들어감 |
| B3 | CDATA 안의 `\|` 파이프 | 그대로 나옴 |
| B4 | `language="c"` | 하이라이팅 됨 (`cpp` 우회 불필요) |
| B5 | expand | 접힌 상태로 나옴 |
| B6 | 저장 후 Edit Source 재확인 | 쓴 XHTML 그대로 유지 |

이것으로 storage format 경로가 확정됐다. `plugins/confluence-post/skills/post/` 가 이 결과 위에 서 있다.

---

## 한 줄로 답해도 됩니다

A1=  A2=  A3=  A4=  A5=  A6=  A7=
