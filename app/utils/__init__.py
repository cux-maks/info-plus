"""데이터베이스 연결 설정을 위한 설정 모듈.

이 모듈은 환경 변수의 로딩을 처리하고 Config 클래스를 통해 데이터베이스
설정을 제공합니다. python-dotenv를 사용하여 프로젝트 루트 디렉토리에 있는
.env 파일에서 환경 변수를 로드합니다.

이 모듈은 애플리케이션 전체에서 데이터베이스 연결 매개변수에 접근할 수 있는
중앙 집중식 설정 객체를 제공합니다.
"""
import os

from dotenv import load_dotenv

# 루트 디렉터리의 .env 파일 로드
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env")
load_dotenv(env_path)

class Config:
    """데이터베이스 연결 매개변수를 위한 설정 클래스.

    이 클래스는 환경 변수에서 로드된 모든 데이터베이스 연결 설정을 캡슐화합니다.
    데이터베이스 자격 증명과 연결 문자열에 접근할 수 있는 구조화된 방법을 제공합니다.

    Attributes:
        DB_USER (str): 환경 변수에서 가져온 데이터베이스 사용자 이름.
        DB_PASSWORD (str): 환경 변수에서 가져온 데이터베이스 비밀번호.
        DB_HOST (str): 환경 변수에서 가져온 데이터베이스 호스트 주소.
        DB_PORT (str): 환경 변수에서 가져온 데이터베이스 포트 번호.
        DB_NAME (str): 환경 변수에서 가져온 데이터베이스 이름.
        SQLALCHEMY_DATABASE_URL (str): 개별 구성 요소로부터 구성된 완전한 SQLAlchemy
            데이터베이스 URL.
    """

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

config = Config()
