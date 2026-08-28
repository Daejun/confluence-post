# P1~P3 렌더링 응답표

사내 PC 안에서 붙여넣기가 되므로, 메뉴를 읽는 대신 **직접 렌더링해서** 확인한다.
세 페이지로 나눴다 — 하나가 저장을 거부해도 나머지는 살아남는다.

각 페이지를 개인 space에 새로 만들고 Edit Source에 파일 내용을 붙여넣고 저장한다.
**항목 라벨(L01, M01, S01)이 화면에 그대로 나오므로 화면 캡처만 주셔도 됩니다.**

---

## P1 — code 언어 (`P1-languages.xhtml`)

L00 / L06 text / L07 none 셋은 **대조군**이다. 색이 없거나 서로 같은 모양이면
그 language 는 지원되지 않고 기본 brush로 떨어진 것이다.

판정: 색이 들어간 것에 O, L00 과 똑같아 보이는 것에 X.

```
L00 zzznotalang(대조군)=   L01 c=   L02 cpp=   L03 diff=   L04 bash=   L05 shell=
L06 text=   L07 none=   L08 python=   L09 py=   L10 java=   L11 js=   L12 javascript=
L13 json=   L14 yaml=   L15 xml=   L16 sql=   L17 rust=   L18 go=   L19 perl=
L20 powershell=   L21 makefile=   L22 ruby=
```

**L01 c 와 L02 cpp 가 서로 다르게 보이는가** → 
**L03 diff 에서 `-` 줄과 `+` 줄에 색이 다르게 들어가는가** → 

## P2 — 매크로 설치 (`P2-macros.xhtml`)

M99 가 **대조군**이다. 설치 안 된 매크로가 어떤 모양인지(보통 "Unknown macro") M99 로
보고, 같은 모양인 것을 미설치로 판정한다.

판정: 제대로 렌더링된 것에 O, M99 와 같은 모양이면 X.

```
M01 info=  M02 note=  M03 warning=  M04 tip=  M05 panel=  M06 expand=  M07 toc=
M08 status=  M09 noformat=  M10 anchor=  M11 excerpt=  M12 children=  M13 jira=
M14 plantuml=  M15 drawio=  M16 mermaid=  M17 mermaid-cloud=  M18 mathblock=
M19 latex=  M20 gliffy=  M21 attachments=  M22 recently-updated=  M99(대조군)=
```

M14~M20 이 전부 X면 **도식은 표·문장·이미지 첨부로만 간다.** 그 경우 매크로 브라우저에서
"diagram", "uml", "draw" 로 한 번만 검색해 다른 이름의 앱이 있는지 봐 주세요 → 

## P3 — 구조 (`P3-structure.xhtml`)

```
S01 3단 중첩 목록이 계단으로 나오는가 =
S02 8열 표: 잘림 / 가로 스크롤 / 글자만 줄어듦 =
S03 표 셀 안의 code / 셀 안의 expand =
S04 긴 코드 한 줄: 줄이 감김 / 가로 스크롤 =
S05 code 파라미터 — title 보임= , linenumbers 붙음= , collapse 접힘=
S06 외부 링크= , 맨 URL 자동 링크= , URL 안 &= , 없는 페이지 링크 모양=
S07 첨부 없는 이미지가 어떻게 보이는가 =
S08 blockquote / hr =
S09 <code> 인라인 / 본문의 mtfs_zone_alloc() 밑줄 유지 =
S10 본문 이스케이프 / CDATA 안 && < | 그대로 =
S11 h2~h5 가 구분되는가 =
S12 긴 한글 문단이 자연스럽게 감기는가 =
```

## 세 페이지 공통

저장 후 Edit Source를 다시 열었을 때 **내가 넣은 XHTML이 그대로인가**
(8줄 probe에서는 그대로였다. 분량이 커져도 같은지 본다) → 

저장을 거부한 페이지가 있으면 그 오류 문구를 그대로 → 
