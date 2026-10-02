# PlantUML — 사내 서버 기준 (1.2024.8)

사내 Confluence의 PlantUML 매크로가 도는 버전은 **1.2024.8** 이다.

이 문서는 그 버전의 변경 목록을 옮긴 것이 아니다. **오래 안정된 부분집합으로 좁혀**
버전 차이가 문제되지 않게 한 것이다. 1.2024.8 이후에 들어온 문법은 물론이고, 그 무렵에
들어온 것도 쓰지 않는다. 실제 지원 여부는 `probe/P4-plantuml.xhtml` 로 확인한다.

## 뼈대

```
@startuml
...
@enduml
```

첫 줄이 `@start...`, 마지막 줄이 짝이 맞는 `@end...` 여야 한다. Confluence 매크로 본문에
넣을 때도 이 두 줄을 생략하지 않는다.

## 쓰는 다이어그램

`@startuml` 하나만 쓴다. sequence / class / component / state / activity 가 전부
`@startuml` 안에서 표현된다.

```
@startuml
participant Client
participant MTFS

Client -> MTFS: write(4K)
activate MTFS
MTFS -> MTFS: alloc zone
MTFS --> Client: ack
deactivate MTFS
@enduml
```

activity 는 새 문법(`start` / `:단계;` / `stop`)만 쓴다. 옛 문법(`(*)` 로 시작하는 것)은
쓰지 않는다.

```
@startuml
start
:zone 선택;
if (valid_blocks == 0?) then (yes)
  :즉시 회수;
else (no)
  :migration;
endif
stop
@enduml
```

## 쓰지 않는 것

| 쓰지 않음 | 이유 |
|---|---|
| `!include`, `!includeurl`, `!includesub` 에 URL 이나 `<stdlib>` | 서버가 외부망을 못 쓰면 렌더링이 통째로 실패한다. stdlib(`<awslib/...>` 등) 번들 여부도 확인 안 됐다 |
| `!theme` | 번들 테마에 의존한다. 확인 전에는 쓰지 않는다 |
| `sprite`, `<img:...>` | 외부 이미지·스프라이트 의존 |
| `!procedure`, `!function`, `!unquoted` | 전처리기. 버전에 민감하고 읽기 어렵다 |
| `@startmindmap`, `@startwbs`, `@startgantt`, `@startsalt`, `@startjson`, `@startyaml` | 다이어그램 타입별 지원 여부 미확인. P4 로 확인되면 푼다 |
| 한글 라벨 | **서버 폰트에 달렸다.** 폰트가 없으면 네모로 나온다. P4 V07 로 확인되기 전에는 영문 라벨을 쓴다 |

## 그 밖의 규칙

- `skinparam` 은 최소한만. 이름이 버전에 따라 바뀐 것이 있어 꾸미기는 서버 기본값에 맡긴다.
- 본문에 `]]>` 가 들어가면 CDATA 가 끊긴다.
- CDATA 안이므로 `&` `<` `>` 를 이스케이프하지 않는다. `-->` 를 그대로 쓴다.
- **도식은 기본이 없음이다.** 전역 게시물 규칙이 도식을 빼도록 되어 있어, 사용자가
  요구했을 때만 낸다.

## storage format 형태

```xml
<p><ac:structured-macro ac:name="plantuml"><ac:plain-text-body><![CDATA[@startuml
Client -> MTFS: write(4K)
MTFS --> Client: ack
@enduml]]></ac:plain-text-body></ac:structured-macro></p>
```

`<![CDATA[` 바로 뒤에 `@startuml` 이 붙는다. 들여쓰면 PlantUML 이 첫 줄을 못 읽는다.

## PlantUML 매크로는 `<p>` 로 감싼다

**위아래 텍스트에 붙어 한 줄로 나왔다는 보고가 있었고, `<p> ... </p>` 로 감싸
고쳐졌다.** 그래서 감싸는 것을 규칙으로 둔다.

다만 **원인은 아직 모른다.** probe(P5)에서 위아래가 `<p>` 문단인 자리에 네 가지로
넣어 봤는데 전부 다른 줄에 나왔다 — 최상위에 그냥 둔 것, `<p>` 로 감싼 것,
`atlassian-macro-output-type` 을 `BLOCK` 으로 준 것, `INLINE` 으로 준 것. 감싸지 않아도
붙지 않았고, 감싸도 렌더링은 같았다. 붙는 것은 이웃이 `<p>` 가 아닌 경우(맨 텍스트,
`<br/>`)일 가능성이 있다.

에디터로 저장된 실제 페이지의 plantuml 매크로는 전부 `INLINE` 을 달고 있지만, 위
결과대로 줄 나뉨과는 관계가 없다. 같은 매크로를 쓰는 페이지 상당수가 앞뒤에
`<br/>` 나 빈 `<p><br/></p>` 를 끼워 두는데, 줄을 나누기보다 위아래 여백을 주려는
것으로 보인다.

- 감싸는 것은 **PlantUML 만**이다. code·expand·info 같은 매크로는 감싸지 않는다.
- 표 셀이나 목록 항목 안에 넣을 때도 `<td><p>…</p></td>`, `<li><p>…</p></li>` 로 감싼다.
- `atlassian-macro-output-type` 은 넣지 않는다. 값이 무엇이든 결과가 같았다.
- 앞뒤는 `<p>` 문단으로 둔다. 맨 텍스트나 `<br/>` 를 매크로에 바로 붙이지 않는다.
- check.py 는 `<p>` 밖의 plantuml 매크로를 WARN 으로 알린다.
