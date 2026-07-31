# paper-ink 컴포넌트 가이드

크림 페이퍼 라이트 팔레트 + 청록/앰버 세맨틱 페어. 캔버스 1080px.
모든 컴포넌트는 외부 라이브러리 없이 CSS/인라인 SVG만으로 렌더된다 (완전 오프라인).

## 레이아웃 원칙

- `.wrap` 컨테이너는 `--maxw`(1080px)를 쓰고, **모든 콘텐츠(프로즈·박스·테이블·차트)가
  전체 폭을 사용한다** — 박스와 테이블의 오른쪽 라인이 일직선으로 정렬되는 것이 이
  시스템의 룩이다. 특정 요소만 좁히지 말 것.
- 문서 구조: `header.hero` → `nav.toc` → `section.ch`×N → `footer`.

## 세맨틱 컬러 페어 (문서마다 의미를 재지정)

- `ar` = 청록(#0E7C63): 주인공/정답/구조적 접근/A안
- `arb` = 앰버(#C1611C): 대비/함정/주의/B안
- 문서에 중심 이분법(방법 A vs B, 장점 vs 함정)이 있으면 이 페어에 일관되게 매핑한다.
- 인라인 강조: `<span class="ar-t">`, `<span class="arb-t">`

## 컴포넌트 목록

| 컴포넌트 | 마크업 루트 | 용도 |
|---|---|---|
| 히어로 | `header.hero` > `.venue` `.title` `.thesis` `.metaline` | 제목·한줄 논지·메타 |
| 목차 | `nav.toc` > `.toc-inner` | 챕터 앵커 링크 (2열) |
| 챕터 | `section.ch` > `.ch-eyebrow`(`.cnum`+`.clabel`) + `h2.ch-title` | 반복 단위 |
| TL;DR | `.tldr` > `.h` + `p` | 챕터 서두 요약 (필수 관례) |
| 콜아웃 | `.call` / `.call.ar` / `.call.arb` > `.ct` + `p` | 포인트/주의/노트 |
| 비교 카드 | `.versus` > `.card.ar` + `.card.arb` | 2단 A/B 요점 비교 |
| Figure | `figure` > `.fig-top`(`.fnum`+`.ftitle`) + `.imgbox img` + `figcaption` | **embed 이미지 규격** — img는 `max-width:100%`, data URI 사용 |
| 수치 테이블 | `.tbl-wrap` > `.tbl-cap` + `.tbl-scroll table` (+`.tbl-foot`) | 센터 정렬, 첫열 sticky, `tr.hl` 하이라이트 |
| 비교 테이블 | `.tbl-wrap.tbl-compare` > 동일 구조 | 좌측 정렬·sticky 헤더·row hover. `td.dim`(+`.d-sub`), `th.c-ar/.c-arb`, `.yes-ar/.yes-arb/.no`, `.mini` |
| 스탯 타일 | `.stat-row` > `.stat`(`.v`[`.arb`]+`.l`) | 핵심 숫자 3개 |
| 키 카드 | `.keys` > `.key`(`.k-num`+`h4`+`p`) | 핵심 요점 3장. `.hl-ar/.hl-arb` 강조 |
| 바 차트 | `.axis-read` > `li`(`.ax-name`[+`.en`]+`.bars`>`.bar-wrap`(`.bar.ar/.arb>i`+`.v`)) | 가로 막대. `i`의 `style="width:N%"`로 값 표현 |
| 차트 박스 | `.chart-grid` > `.chart-box`(svg+`.chart-legend`) + 해설 div | 인라인 SVG 차트(레이더 등) + 우측 해설. `.chart-note` 각주 |
| 파이프라인 | `.stage-row`[`.n3`/`.n4`] > `.stage`[`.ar`/`.arb`] | 단계 흐름 3~5칸 |
| Pros/Cons | `.pc-grid` > `.pc.ar`+`.pc.arb` > `.pc-top`+`.pc-body`(`.lbl`+`ul.pros/ul.cons`) | 장단점 대면 비교 |
| 칩 | `.chips` > `.chip`[`.ar`/`.arb`] | 키워드 태그 |
| 용어 사전 | `.gloss` > `.gitem`(`.term`[+`.en`]+`p`) | 2열 용어집 |
| 한 장 정리 | `.takeaways` > `.take`(`.n`+`.body`) | 마무리 요점 4~6개 |

## 테이블 컬럼 폭 제어

컬럼 폭은 `<th>`의 인라인 스타일로 제어한다 — 이것이 공인된 방법이다 (CSS 클래스
추가 금지 원칙과 무관하게 허용).

- **% 단위 사용, px 금지**: `<th style="width:17%">`. px 고정은 1080px 캔버스에서
  나머지 한 컬럼이 과도하게 넓어지는 불균형을 만든다.
- **배분 원칙**: 문장이 들어가는 컬럼일수록 넓게. 서술형 컬럼이 2개 이상이면 내용
  길이에 비례해 나눈다 (예: 라벨 17% / 주 서술 53% / 보조 서술 30%). 라벨·ID·뱃지
  컬럼만 15~20%로 좁힌다.
- 모든 `<th>`에 %를 명시하면 합이 100%가 되도록. 일부만 지정하면 나머지가 잔여 폭을
  가져간다는 점을 의식하고 쓸 것.

## Ad-hoc 시각화 (목록에 없는 차트·다이어그램)

컴포넌트 목록은 완결 카탈로그가 아니다. 타임라인·산점도·플로우 다이어그램 등이
필요하면 `.chart-box`(또는 `figure`) 안에 **인라인 SVG로 직접 그린다**. 규칙:
시스템 토큰 컬러만 사용(시리즈 A `#0E7C63`, B `#C1611C`, 그리드 `#DDDCD0`,
라벨 `#4A4A55`), 라벨 폰트는 JetBrains Mono 11px, 외부 라이브러리 금지,
`<style>`에 새 클래스 추가 금지(미세 조정은 인라인 스타일). 아래 레이더가 선례.

## 레이더 SVG 작성법

`preview.html`의 `#ch4` SVG를 복사해서 수정한다. 규칙:
- viewBox `0 0 480 400`, 중심 (230,195), 반경 135
- 그리드: `stroke:#DDDCD0` 동심 폴리곤 4겹 + 축선
- 시리즈 A: `fill:rgba(14,124,99,.14); stroke:#0E7C63`, 시리즈 B: `fill:rgba(193,97,28,.13); stroke:#C1611C`
- 꼭짓점 좌표: 축 k(0..n-1), 값 v(0~10) → 각도 θ = -90° + k·(360/n)°,
  x = 230 + 13.5·v·cos(θ), y = 195 + 13.5·v·sin(θ)
- 라벨: `fill:#4A4A55`, JetBrains Mono 11px

## 이미지 embed 규격 (paper-explainer-ko 연동)

- `figure .imgbox img`는 반드시 `max-width:100%;height:auto` (CSS에 포함됨) — data URI
  base64 이미지가 컨테이너에 맞게 축소된다.
- 1080px 캔버스에서 이미지 최대 표시폭 ≈ 990px. 원본 다운스케일 상한은
  `embed_images.py` 기본값(narrow 1200px)이 담당한다.
- 오프라인 원칙: `<img src="http...">` 금지, data URI만.

## 폰트

Pretendard(본문) + JetBrains Mono(라벨·숫자·eyebrow)를 CDN @import로 로드하되,
오프라인에서는 시스템 폰트 폴백으로 자연스럽게 렌더된다. @import 두 줄을 제거하지 말 것.
