# BangBangGokGok (방방곡곡)

Flask 기반 통합 서비스 — **방방곡곡**(집값 분석) + **phonezipsa**(폰 등급/가격 예측) API

---

## 주요 기능

### 1. 방방곡곡 — 집값 분석 사이트

서울 지역 아파트 매물을 조건별로 검색하고 지도에서 확인할 수 있는 웹 서비스입니다.

| 경로 | 설명 |
|------|------|
| `/` | 방방곡곡 메인으로 리다이렉트 |
| `/index` | 메인 — 럭셔리 아파트·상승 확률 UP 아파트 추천 |
| `/search` | 매물 검색 (구, 가격, 평수, 연식, 역세권 조건) |
| `/result` | 검색 결과 지도 표시 (네이버 지도 API) |
| `/intro` | 팀 소개 |
| `/favorites` | 관심목록 |
| `/sale` (POST) | 아파트 매물 상세 조회 API |

### 2. phonezipsa — 폰 등급/가격 예측 API

스마트폰 이미지를 분석해 등급 및 예상 가격을 제공합니다.

| 경로 | 설명 |
|------|------|
| `/phone` | phonezipsa 메인으로 리다이렉트 |
| `/phone/index` | 폰 등급 예측 페이지 |
| `/phone/api/grade` (POST) | 이미지 기반 등급·가격 예측 API |

---

## 프로젝트 구조

```
BangBangGokGok/
├── app.py                    # Flask 앱 진입점
├── controller/
│   ├── MainController.py     # 방방곡곡 라우트
│   └── PhoneController.py    # phonezipsa 라우트
├── service/
│   ├── MainService.py        # 네이버 부동산 API, 지역·매물 조회
│   ├── AnalysisService.py    # 럭셔리·회귀분석 아파트 추출
│   ├── RecoService.py        # 유사도 기반 매물 추천
│   └── PhoneService.py       # 폰 이미지 등급·가격 예측 (TensorFlow, PostgreSQL)
├── model/                    # AI 모델 (별도 준비 필요)
│   ├── front_model.keras     # 앞면 등급 분류
│   ├── back_model.keras      # 뒷면 등급 분류
│   └── time_series_model.keras  # 가격 시계열 예측
├── resources/
│   └── csv/
│       └── data.csv          # 아파트 데이터 (방방곡곡 분석용)
├── static/
│   ├── css/
│   └── json/
│       └── favorites.json    # 관심목록 저장
├── templates/
├── data/
│   └── images/               # 업로드된 폰 이미지 (Docker 볼륨)
├── Dockerfile
├── docker-compose.yml          # Flask 기본
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
# Flask 실행
docker-compose up -d --build

```

실행 후:
- 방방곡곡: `http://localhost:5000/index`
- phonezipsa: `http://localhost:5000/phone/index`

---

## 환경 요구사항

### 방방곡곡

- Python 3.12+
- Flask, scikit-learn, pandas, requests

### phonezipsa

- PostgreSQL (DB: `phone`, `real_price`, `phone_model`, `gemini_template` 테이블)
- 모델 파일: `model/front_model.keras`, `back_model.keras`, `time_series_model.keras`
- Google Gemini API 키 (AI 문구 생성)
- 업로드 이미지 경로: `/app/data/images` (또는 `./data/images` 마운트)

### 환경 변수 (phonezipsa DB 연동)

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `DATABASE_HOST` | `postgres-db` | PostgreSQL 호스트 |
| `DATABASE_PORT` | `5432` | PostgreSQL 포트 |
| `DATABASE_NAME` | `postgres` | DB 이름 |
| `DATABASE_USER` | `postgres` | DB 사용자 |
| `DATABASE_PASSWORD` | `postgres` | DB 비밀번호 |
| `LOG_LEVEL` | `INFO` | 로그 레벨 (DEBUG/INFO/WARNING/ERROR) |

`.env` 파일에는 실제 값(호스트, 비밀번호 등)을 넣고, 버전 관리는 값이 비어 있는 `sample.env`만 커밋합니다.
컨테이너 환경에서는 `docker-compose.yml`과 같이 `postgres-db`라는 PostgreSQL 컨테이너/서비스 이름을 `DATABASE_HOST`로 사용합니다.

---

## 외부 연동

- **네이버 부동산 API**: 지역(cortarNo), 매물 목록, 상세 정보
- **네이버 지도 API**: 검색 결과 지도 시각화 (클라이언트)
- **Google Gemini API**: 폰 매물 AI 문구 생성 (phonezipsa)
