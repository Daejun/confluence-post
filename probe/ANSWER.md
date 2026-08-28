# probe 응답표 — 빈칸만 채워 주세요

붙여넣기가 안 되므로 **A부터** 합니다. A는 타이핑이 없고, 스킬 규칙의 대부분이 A에서 정해집니다.
B는 A로 알 수 없는 것(실제 렌더링)만 남긴 22줄입니다.

---

## A. 화면에서 읽어 적기 (타이핑 0)

A1. Confluence 버전 — 도움말(?) > About Confluence, 또는 페이지 맨 아래
    → 

A2. 편집 화면 Insert(+) 메뉴에 **Markup** 항목이 있는가, 있으면 대화상자의 선택지
    → 있음/없음 :  Confluence Wiki □   Markdown □

A3. **Code Block macro의 Language 드롭다운 목록 전부.** 매크로 삽입 > Code Block > Language.
    이 목록이 커널 문서에서 매번 걸리는 항목입니다. 보이는 대로 옮겨 적어 주세요.
    → 

A4. 매크로 브라우저({ 입력 또는 매크로 삽입)에서 아래를 검색해 **있는 것에만** 표시
    → expand □   toc □   info/note/warning/tip □   panel □   status □
       plantuml □   draw.io □   mermaid □   latex/math □   jira issue □

A5. 사내에서 잘 쓰인 페이지 하나를 열고 `...` > **소스 보기(View Source)**.
    `ac:name="___"` 에 나오는 **매크로 이름만** 적어 주세요 (예: code, info, expand, toc).
    사내 문서가 실제로 쓰는 어휘가 여기 나옵니다. 메뉴가 없으면 "없음".
    → 

A6. 프로필 메뉴에 **Personal Access Tokens** 항목이 있는가
    → 있음 / 없음

A7. 내 space key, 초안을 둘 부모 페이지
    → 

---

## B. 22줄 타이핑 후 렌더 확인

개인 space에 빈 페이지를 만들고, 편집 화면 Insert(+) > Markup > **Confluence Wiki** 에
`PROBE-min.txt` 를 그대로 입력 → Insert → **저장** → 저장된 읽기 화면에서 봅니다.
A2가 "없음"이면 B는 건너뛰고 그 사실만 알려 주세요.

B1 (T1). "가나다"와 "라마바"가
    → 한 줄로 붙음 / 두 줄로 나뉨

B2 (T2). 세 개 중 밑줄이 사라지거나 기울임이 된 것에 표시
    → mtfs_zone_alloc() □   _do_fork() □   {{_do_fork()}} □   (셋 다 멀쩡하면 "이상 없음")

B3 (T3). 표가
    → 2열로 정상 / 깨짐.   `p | q` 셀이 그대로 보이는가 → 보임 / 안 보임

B4 (T4). `language=c` 로 지정한 code block이
    → 색 하이라이팅 됨 / 색 없는 평문 / 오류 표시

B5 (T5). status 매크로가
    → 초록 라벨로 나옴 / 글자 그대로 나옴 / 오류

B6 (T6). "하나"와 "둘"이
    → 같은 목록으로 이어짐 / 코드에서 목록이 끊김

---

## C. markdown 경로 (A2에 Markdown이 있을 때만)

새 페이지에 Insert(+) > Markup > **Markdown** 으로 `PROBE-min-markdown.txt` 입력.

C1. 표가 표로 변환되는가          → 예 / 아니오
C2. ```c 코드가 code block이 되는가, 색이 들어가는가 → 표/색 :
C3. 체크박스                       → 됨 / 안 됨

---

## 한 줄로 답해도 됩니다

A1=  A2=  A3=  A4=  A5=  A6=  A7=  B1=  B2=  B3=  B4=  B5=  B6=  C1=  C2=  C3=
