# QA Release Gate

**결제 단말기(Android) 릴리즈 품질 관리 대시보드**

매장에 배포되는 결제 단말기는 무선(OTA)으로 업데이트가 나가기 때문에, 배포 전 품질 검증이 무엇보다 중요합니다. QA Release Gate는 릴리즈 게이트 판정부터 테스트 케이스 관리, 결함 추적, 필드 이슈 분석, 품질 지표 시각화까지 QA 엔지니어링 전반을 하나의 콘솔에서 다룰 수 있도록 설계한 도구입니다.

> Device Team의 QA 업무 흐름(OTA 배포 전 검증 · 필드 이슈 대응 · 품질 지표 관리)을 기반으로 설계한 포트폴리오 프로젝트입니다.

---

## 핵심 기능

### 릴리즈 게이트 (Release Gate)
OTA 배포 전 통과 기준을 자동으로 점검하고 **Go / No-Go**를 판정합니다.
- Critical 결함 0건 · TC 통과율 90% 이상 · 미해결 결함 5건 이하를 기준으로 게이트 상태 시각화
- 릴리즈별 검증 진행률(Pass/Fail) 바 표시

### 테스트 케이스 관리
- Smoke / Regression / Integration 유형별 TC 등록 및 상태 관리(Pass·Fail·Blocked·미실행)
- 커버리지 바로 통과율을 한눈에 확인, 게이트 기준(90%) 연동

### 결함 트래커
- Critical / Major / Minor 심각도 분류
- **탈출 결함(Escaped Defect)** — 배포 후 발견된 결함 별도 추적
- 재발 결함 플래그, Jira 티켓 번호 연동

### 필드 이슈
- CS·현장·모니터링에서 유입된 이슈의 패턴/원인 분석
- 재발 이슈 감지 및 **테스트 케이스 전환 여부** 추적 (검증 커버리지 확장)

### 품질 지표
- 릴리즈별 TC 통과율 추이(꺾은선) · 결함 분포(막대) 차트 (의존성 없는 자체 SVG)
- 평균 통과율, 결함 밀도, 탈출 결함, Critical 누적 요약

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | Vue 3 (Options API), Vite |
| Backend | Flask (Python 3.11) |
| Database | PostgreSQL |
| 차트 | 자체 구현 SVG (라이브러리 미사용) |

---

## 프로젝트 구조

```
qa-release-gate/
├── backend/
│   ├── app.py              # Flask API + PostgreSQL
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue              # 사이드바 + 라우팅
        ├── api/index.js
        └── components/
            ├── ReleaseGate.vue     # 릴리즈 게이트
            ├── TestCases.vue       # 테스트 케이스
            ├── DefectTracker.vue   # 결함 트래커
            ├── FieldIssues.vue     # 필드 이슈
            └── QualityMetrics.vue  # 품질 지표 (차트)
```

---

## 로컬 실행

### 백엔드

```bash
cd backend
pip install -r requirements.txt
# PostgreSQL 연결 문자열을 환경변수로 전달
$env:DATABASE_URL="postgresql://user:pass@host:5432/dbname"   # Windows PowerShell
flask --app app run --port 5001
```

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:5173` 접속.

프론트는 백엔드 없이도 UI 확인이 가능하며, API 연결 시 실제 데이터가 표시됩니다.
API 주소를 바꾸려면 `frontend/.env`에 다음을 추가하세요.

```
VITE_API_URL=http://localhost:5001/api
```

---

## 데이터베이스 테이블

| 테이블 | 설명 |
|--------|------|
| `releases` | 릴리즈 버전 · 플랫폼 · 게이트 상태 |
| `test_cases` | 릴리즈별 테스트 케이스 |
| `defects` | 결함 (심각도 · 탈출/재발 플래그) |
| `field_issues` | 필드 유입 이슈 · TC 전환 여부 |

서버 시작 시 `init_db()`가 테이블을 자동 생성합니다.

---

## 설계 의도

- **릴리즈 게이트 중심** — OTA 배포는 되돌리기 어렵기 때문에, 정량 기준(Critical 0 · 통과율 90% · 미해결 ≤5)으로 배포 가부를 명확히 판정하도록 설계했습니다.
- **필드 → TC 전환 루프** — 현장에서 발생한 이슈를 테스트 케이스로 전환해 동일 결함의 재발을 막고 커버리지를 넓히는 QA 개선 사이클을 반영했습니다.
- **품질 지표 추적** — 릴리즈마다 통과율·결함 밀도·탈출 결함을 측정해 품질 추이를 정량적으로 관리합니다.

---

## 개발자

박수빈 · [@subeen-park](https://github.com/subeen-park)
