# 카카오톡 챗봇 템플릿

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)

FastAPI와 MySQL을 사용한 카카오톡 챗봇 개발을 위한 템플릿 프로젝트입니다.

## 기술 스택

- Python 3.11
- FastAPI
- MySQL 8.0
- Poetry
- Docker & Docker Compose
- pytest
- Ruff & Black
- GitHub Actions

## 프로젝트 구조

```
├── app/
│   ├── core/
│   │   └──  __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── category.py
│   │   ├── employee_category.py
│   │   ├── employeee_hire_type.py
│   │   ├── employee.py
│   │   ├── feature.py
│   │   ├── hire_type.py
│   │   ├── news.py
│   │   ├── user_category.py
│   │   └── users.py
│   ├── routers/
│   │   ├── employee.py
│   │   ├── feature.py
│   │   ├── news.py
│   │   └── user.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── db_manager.py
│   │   ├── init_default_data.py
│   │   ├── init_elasticsearch_index.py
│   │   ├── insert_employee_data.py
│   │   ├── news_client.py
│   │   ├── news_provider_mapping.py
│   │   └── verifier.py
│   ├── dev.Dockerfile
│   ├── Dockerfile
│   ├── main.py
│   └── test.Dockerfile
├── tests/
│   └── unit/
│       ├── routers/
│       ├── test_add_employee_data.py
│       ├── test_add_user_favorit.py
│       ├── test_employee_DB_search.py
│       ├── test_employee_recommendation.py
│       ├── test_get_categories_by_feature.py
│       ├── test_get_my_category_list.py
│       ├── test_get_news_recommendations.py
│       ├── test_news_client.py
│       ├── test_news_DB_search.py
│       │── test_user_delete_favorite.py
│       └── utils/
│           ├── response_builder/
│           │   └── test_response_builder.py
│           ├── text_utils/
│           │   └── test_text_utils.py
│           └── test_data/
│               ├── response_builder_cases.json
│               ├── router_cases.json
│               └── text_utils_cases.json
├── docker/
│   └── Dockerfile
├── .env.example
├── .gitignore
├── docker-compose.yml
├── poetry.lock
├── pyproject.toml
├── pytest.ini
└── README.md
```

## 시작하기

### 사전 요구사항

- Python 3.11
- Docker & Docker Compose
- Poetry

### 설치 및 실행

1. 저장소 클론

```bash
git clone <repository-url>
cd kakaotalk-chatbot-template
```

2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 필요한 설정 수정
```

3. Docker 컨테이너 실행

```bash
docker-compose up --build
```

서버가 `http://localhost:8000`에서 실행됩니다.

### API 문서

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 개발

### 의존성 관리

새로운 패키지 추가:

```bash
poetry add <package-name>
```

개발 의존성 추가:

```bash
poetry add --group dev <package-name>
```

### 테스트

테스트 실행:

```bash
# Docker 컨테이너 내부에서 실행
docker-compose exec app poetry run pytest

# 커버리지 리포트 생성
docker-compose exec app poetry run pytest --cov=app --cov-report=term-missing
```

### 코드 품질

린팅 및 포맷팅:

```bash
# Ruff를 사용한 린팅
poetry run ruff check .

# Ruff를 사용한 자동 수정
poetry run ruff check --fix .

# Black을 사용한 포맷팅
poetry run black .
```

## GitHub Actions

프로젝트는 다음과 같은 자동화된 워크플로우를 포함합니다:

1. **Lint**: Ruff와 Black을 사용한 코드 품질 검사
2. **Test**: Docker 환경에서의 테스트 실행 및 커버리지 리포트 생성

## 환경 변수

| 변수명      | 설명                  | 기본값               |
| ----------- | --------------------- | -------------------- |
| APP_NAME    | 애플리케이션 이름     | kakaotalk-chatbot    |
| ENVIRONMENT | 실행 환경             | development          |
| DEBUG       | 디버그 모드           | True                 |
| HOST        | 서버 호스트           | 0.0.0.0              |
| PORT        | 서버 포트             | 8000                 |
| DB_HOST     | 데이터베이스 호스트   | db                   |
| DB_PORT     | 데이터베이스 포트     | 3306                 |
| DB_NAME     | 데이터베이스 이름     | chatbot              |
| DB_USER     | 데이터베이스 사용자   | user                 |
| DB_PASSWORD | 데이터베이스 비밀번호 | password             |
| SECRET_KEY  | 보안 키               | your-secret-key-here |

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m '✨feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
