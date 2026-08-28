---
name: confluence-post
description: 사내 Confluence(Data Center)에 올릴 문서를 storage format(XHTML)으로 만든다. 기존 markdown을 변환하거나 처음부터 작성해 Edit Source에 그대로 넣을 조각 파일을 낸다. Use when the user asks to write or convert a document for 사내 컨플루언스/Confluence, says "컨플루언스에 올릴 것", "컨플루언스 문법으로 바꿔줘", or asks to prepare a page for Confluence DC.
---

# 사내 Confluence 게시물 만들기

산출물은 **storage format(XHTML) 조각 파일** 하나다. 사용자가 그것을 사내 Confluence의
**Edit Source**에 넣는다. wiki markup(`h1.`, `{code}`)과 markdown insert는 쓰지 않는다 —
Edit Source가 있어 둘 다 우회하고, 그 두 경로에만 있는 파서 함정을 피한다.

조각이므로 `<!DOCTYPE>`, `<html>`, `<body>`를 쓰지 않는다. 최상위는 `<p>`, `<h2>`,
`<table>`, `<ac:structured-macro>` 같은 요소들이 나열된 형태다.

## 확정된 환경 (2026-08-28 실측)

probe로 직접 확인한 것. 추측이 아니다.

- Edit Source 편집·저장 가능
- 표 `<td>` 안에 code 매크로가 들어간다 — 벤치 결과 표에 커맨드를 넣을 수 있다
- CDATA 안의 `|` 가 그대로 나온다
- `<ac:parameter ac:name="language">c</ac:parameter>` 가 하이라이팅된다 — 커널 코드에
  `cpp` 우회가 필요 없다
- expand 매크로가 접힌 상태로 나온다
- 저장해도 Confluence가 XHTML을 다시 쓰지 않는다 — 낸 그대로 남는다

## 아직 확인 안 된 것

확인 전에는 **쓰지 않는다.** 필요해지면 사용자에게 물어 `probe/ANSWER.md`를 채운다.

- Code Block macro의 전체 언어 목록 (`c`만 확인됨). 미확인 언어는 `text`로 낸다.
- 설치된 3rd-party 매크로 (plantuml / draw.io / mermaid / latex). **없다고 가정한다.**
- 사내가 실제로 쓰는 매크로·파라미터 어휘
- space key, 초안을 둘 부모 페이지

## 순서

1. **입력을 정한다.** 변환할 markdown 파일 경로가 있으면 읽는다. 없으면 새로 쓴다.
   어느 쪽인지 한 줄로 밝히고 시작한다.

2. **내용을 게시물 규칙으로 줄인다.** 전역 CLAUDE.md의 "게시물" 규칙이 그대로 적용된다.
   사실·근거·요청만 남긴다. 근거는 `파일:줄`, 커밋 SHA, 측정치 + 조건.
   빼는 것: 배경 설명, 용어 정의, 경위 서술, 날짜 서술, 감상, 대안 기각 목록, 인사말,
   자기 요약 절. **ASCII 도식도 뺀다** — 표나 문장으로 바꾼다.

3. **변환한다.** 매핑은 `reference/storage-format.md`. 외우지 말고 그 파일을 읽는다.

4. **`out/<slug>.xhtml` 에 쓴다.** slug은 영문 kebab-case.

5. **검증한다.**
   ```bash
   python3 skills/confluence-post/scripts/check.py out/<slug>.xhtml
   ```
   ERROR가 하나라도 있으면 고쳐서 다시 돌린다. 통과하지 않은 것을 사용자에게 주지 않는다.

6. **초안을 보여주고 승인을 받는다.** 렌더링될 내용을 읽기 좋은 형태로 보여준다
   (XHTML 원문을 통째로 화면에 쏟지 않는다). 수정 요청을 받으면 변호하지 말고 고친 초안을
   다시 보여준다.

7. **전달한다.** 파일 경로와 함께 **줄 수·문자 수**를 말한다. 사내망에서 손으로 옮겨
   적어야 할 수 있어 분량이 곧 비용이다. 길면 어디서 끊어 나눠 넣을지 같이 알려준다.

## 가장 틀리기 쉬운 자리

- **이스케이프.** CDATA 밖의 텍스트에서 `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`.
  `A && B`, `if (a < b)` 를 문단에 그대로 쓰면 저장이 거부된다.
- **CDATA 안에 `]]>` 가 들어가면 안 된다.** 코드에 그 세 글자가 있으면 code 매크로를
  둘로 쪼갠다.
- **중첩 목록은 부모 `<li>` 안에 넣는다.** `<ul>` 형제로 두면 목록이 끊긴다.
- **이미지는 먼저 첨부해야 한다.** `<ac:image>`만 넣고 첨부를 안 하면 깨진 이미지가 된다.
  첨부가 필요한 파일은 초안에서 목록으로 따로 알려준다.
- **미확인 매크로를 쓰지 않는다.** check.py가 걸러낸다.
