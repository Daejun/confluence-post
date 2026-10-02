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
<ac:structured-macro ac:name="plantuml"><ac:plain-text-body><![CDATA[@startuml
Client -> MTFS: write(4K)
MTFS --> Client: ack
@enduml]]></ac:plain-text-body></ac:structured-macro>
```

`<![CDATA[` 바로 뒤에 `@startuml` 이 붙는다. 들여쓰면 PlantUML 이 첫 줄을 못 읽는다.

## 앞뒤 텍스트에 붙어 나올 때

**소스에 빈 줄이 있어도 매크로가 위아래 텍스트에 붙어 한 줄로 렌더링될 수 있다.**
**[실측]** 2026-09-09, plantuml 매크로 31개를 넣은 문서에서 사용자가 "plantuml
앞뒤로 줄바꿈이 왜 안되냐"고 보고했다. 소스에는 매크로 앞뒤로 빈 줄이 모두 있었고
`</p>` 와 같은 줄에 붙은 곳도 없었다. 원인은 소스가 아니라 **Confluence 가 매크로를
block 이 아니라 inline 으로 그리는 것**으로 보인다.

**후보 조치:** 매크로를 `<p> ... </p>` 로 감싼다. 31개 전부에 적용했으나
**[미확인]** — 실제로 줄바꿈이 고쳐졌는지 사용자 확인을 받지 못했다. P8 probe 로
확인하기 전에는 확정하지 않는다. `<p>` 감싸기는 매크로를 최상위에서 한 단계 안으로
넣는 것이라, 확정 전에는 쓰지 않는다.
