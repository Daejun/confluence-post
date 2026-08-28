# M01 제목

M02 이 문장과
이 문장은 단일 개행으로 나뉜다.

**M03 굵게** / *기울임* / `인라인 코드` / ~~취소선~~

M04 식별자: `mtfs_zone_alloc()` 과 이스케이프 없는 mtfs_zone_alloc()

M05 목록:
- 1단계
  - 2단계
    - 3단계

1. 번호 하나
2. 번호 둘

M06 표:

| 항목 | f2fs | mtfs | 비고 |
|---|---|---|---|
| rand write IOPS | 12,400 | 18,900 | 4K, QD32 |
| 평균 지연 | 2.1 ms | 1.4 ms | |

M07 fenced code block (언어 지정):

```c
static int mtfs_gc_zone(struct mtfs_sb_info *sbi, unsigned int zno)
{
	return migrate_zone(sbi, &sbi->zones[zno]);
}
```

M08 fenced code block (언어 없음):

```
+---------+---------+
| zone 0  | zone 1  |
+---------+---------+
```

M09 indent code block:

    mkfs.mtfs -z 48M /dev/nvme0n1p3

M10 인용:

> 인용 블록 본문.

M11 링크: [GitHub PR](https://github.com/example/repo/pull/1)

M12 이미지: ![도식](zone-layout.png)

M13 가로줄:

---

M14 체크박스:

- [ ] 안 됨
- [x] 됨

M15 각주[^1]

[^1]: 각주 본문
