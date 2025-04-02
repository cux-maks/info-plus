import os
from dotenv import load_dotenv

# 루트 디렉터리의 .env 파일 로드
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env")
load_dotenv(env_path)

class Config:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URL = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

config = Config()
