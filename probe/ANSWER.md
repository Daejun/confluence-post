# probe 응답표 — 빈칸만 채워 주세요

경로는 **storage format(XHTML)을 Edit Source에 직접 넣기**로 확정했다.
markdown 경로와 wiki markup 파서 테스트는 뺐다 — Edit Source가 있으면 둘 다 우회한다.

A는 타이핑이 없다. A만으로 스킬 규칙의 대부분이 정해진다.
B는 8줄이고, storage format을 손으로 써서 넣을 수 있는지만 본다.

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

## B. 8줄 타이핑 (A2가 "편집 가능"일 때만)

개인 space에 빈 페이지를 만들고 Edit Source를 열어 `PROBE-min.txt` 를 그대로 입력 → 저장.

B1. 저장이 되는가
    → 됨 / 거부됨 (거부되면 오류 문구를 그대로)

B2. 표 셀 안의 code block이 표 안에 들어간 채로 보이는가
    → 들어감 / 표 밖으로 밀림 / 코드가 사라짐

B3. 코드 안의 `a|b` 파이프 문자가 그대로 보이는가
    → 보임 / 깨짐

B4. `language="c"` 지정이
    → 색 하이라이팅 됨 / 색 없는 평문 / 오류

B5. expand(펼치기)가 접힌 상태로 나오는가
    → 나옴 / 안 나옴

B6. **저장한 뒤 Edit Source를 다시 연다.** 내가 쓴 XHTML이
    → 그대로 있음 / Confluence가 다시 써 놓음(태그·속성이 늘거나 순서가 바뀜)
    다시 쓰였다면 code 매크로 한 개만 바뀐 모습 그대로 적어 주세요. 스킬이 낼
    XHTML 형태를 여기에 맞춥니다.
      → 

---

## 한 줄로 답해도 됩니다

A1=  A2=  A3=  A4=  A5=  A6=  A7=  B1=  B2=  B3=  B4=  B5=  B6=
