"""사용자 맞춤 뉴스 추천 API 테스트 모듈.

이 모듈은 news_client의 기능을 테스트합니다.

주요 테스트 항목:
    - 외부 네이버 뉴스 API의 Response를 json -> news 파싱
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.news import News
from app.utils.news_client import parse_naver_news

# 테스트용 SQLite 파일 DB (세션 유지)
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def sample_json():
    return {
        "items": [
            {
                "title": "<b>테스트 뉴스 제목</b>",
                "originallink": "https://example.com/original",
                "link": "https://example.com/news1",
                "description": "<b>테스트 내용입니다.</b>",
                "pubDate": "Mon, 13 May 2024 15:00:00 +0900"
            }
        ]
    }


def test_parse_naver_news_basic(sample_json):
    category_id = 1
    category_name = "테스트"

    result = parse_naver_news(sample_json, category_id, category_name)

    assert isinstance(result, list)
    assert len(result) == 1

    news = result[0]
    assert isinstance(news, News)
    assert news.title == "테스트 뉴스 제목"
    assert news.contents == "테스트 내용입니다."
    assert news.category_id == category_id
    assert news.category == category_name
    assert news.url == "https://example.com/news1"
    assert news.original_url == "https://example.com/original"
    assert news.source is not None
    assert isinstance(news.publish_date, datetime)
    assert news.publish_date.utcoffset() == timedelta(hours=9)
    assert isinstance(news.news_id, int)
    assert len(str(news.news_id)) <= 10  # 최대 10자리

