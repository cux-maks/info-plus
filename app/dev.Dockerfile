FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install poetry

# Poetry 가상환경 생성하지 않도록 설정
RUN poetry config virtualenvs.create false

# 의존성 파일 복사 및 설치 (테스트 의존성 포함)
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi

# 애플리케이션 코드 복사
COPY . .

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 