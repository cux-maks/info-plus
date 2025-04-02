from app.utils.response_builder import (
    add_quick_replies,
    create_basic_card_response,
    create_simple_text_response,
)
from app.utils.text_utils import (
    contains_any_keywords,
    create_formatted_list,
    extract_keywords,
)

__all__ = [
    'create_simple_text_response',
    'create_basic_card_response',
    'add_quick_replies',
    'extract_keywords',
    'contains_any_keywords',
    'create_formatted_list'
]


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
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

config = Config()
