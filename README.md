# BangBangGokGok (방방곡곡)

Flask 기반 아파트 매물 검색 및 데이터 분석 API 서비스입니다.

## 주요 기능

### 1. 방방곡곡 — 집값 분석 사이트

지역별 아파트 매물을 검색하고 지도에서 확인할 수 있는 웹 서비스입니다.

- **메인 페이지** (`/`): 추천 아파트 매물 소개
- **매물 검색** (`/result`): 구/동 기준 지역별 아파트 매물 검색
  - 네이버 지도 API 연동으로 검색 결과 지도 표시
  - 가격·면적·세대수 조건 필터링
- **팀 소개** (`/intro`): 프로젝트 팀 소개

### 2. Data Analysis API — phonezipsa 연동

phonezipsa와 연동되는 데이터 분석용 REST API를 제공합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/sale` | 아파트 매물 상세 정보 조회 |
| GET | `/result` | 지역별 매물 검색 결과 (쿼리파라미터: `city`) |

**`/sale` API 예시**

```json
// Request
{
  "markerId": "단지/마커 ID"
}

// Response
{
  "status": "success",
  "apt": { /* 아파트 상세 정보 */ }
}
```

---

## 프로젝트 구조

```
BangBangGokGok/
├── app.py              # Flask 앱 진입점
├── controller/
│   └── MainController.py   # 라우트 정의
├── service/
│   └── MainService.py     # 네이버 부동산 API 연동 로직
├── templates/          # HTML 템플릿
├── static/             # CSS, JS 정적 파일
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 실행 방법

### 로컬 실행

```bash
pip install -r requirements.txt
python app.py
```

### Docker 실행

```bash
docker-compose up -d --build
```

실행 후 `http://localhost:5000` 에서 접속할 수 있습니다.

---

## 환경 요구사항

- Python 3.11+
- Flask 3.0+

## 외부 연동

- **네이버 부동산 API**: 지역 번호(cortarNo), 매물 목록, 상세 정보 조회
- **네이버 지도 API**: 검색 결과 지도 시각화 (클라이언트)
