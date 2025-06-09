import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.main import app
from app.models import (
    Base,
    Category,
    Feature,
    News,
    Users,
)
from app.utils.db_manager import db_manager

# 테스트용 SQLite DB 설정
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB 초기화 및 테이블 생성
@pytest.fixture(scope="function")
def setup_database():
    """
    테스트용 데이터베이스를 초기화하고, 모든 테이블을 생성합니다.

    이 fixture는 테스트 함수 실행 전 매번 호출되어 데이터베이스를 깨끗한 상태로 초기화합니다.
    외래 키 제약 조건을 활성화하고, 기존 테이블은 모두 삭제 후 다시 생성합니다.

    Returns:
        None
    """
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON;"))  # 외래 키 활성화
        Base.metadata.drop_all(bind=conn)  # 기존 테이블 삭제
        Base.metadata.create_all(bind=conn)  # 테이블 생성

# 테스트용 DB 세션 및 테스트 데이터 삽입
@pytest.fixture(scope="function")
def test_db(setup_database):
    """
    테스트용 DB 세션을 생성하고 초기 데이터를 삽입합니다.

    setup_database fixture를 사용하여 DB를 초기화한 후, 테스트에 필요한
    사용자, 기능, 카테고리, 채용 공고 등의 기본 데이터를 삽입합니다.

    테스트 종료 시 세션을 롤백하고 종료하며, 모든 테이블을 삭제합니다.

    Yields:
        Session: 테스트용 SQLAlchemy DB 세션
    """
    db = TestingSessionLocal()

    # 기존 데이터 삭제
    db.query(Category).delete()
    db.query(Feature).delete()
    db.query(Users).delete()
    db.commit()

    # ✅ 테스트 데이터 삽입
    user = Users(user_id="user123", user_name="John Doe")
    db.add(user)
    db.commit()
    db.refresh(user)  # ✅ user_id 생성 확인

    feature = Feature(feature_type="News")
    db.add(feature)
    db.commit()
    db.refresh(feature)  # ✅ id 생성 확인

    category = Category(feature_id=feature.feature_id, category_name="보건")
    db.add(category)
    db.commit()
    db.refresh(category)

    news_item = News(
        news_id=1,
        category_id=category.category_id,
        title="보건 정책 변화",
        contents="테스트 뉴스 내용",
        source="뉴스타임",
        publish_date=datetime.datetime(2023, 6, 7, 9, 51),
        category="기타",
        url="http://testnews.com/article",
        original_url="http://originalsource.com/article"
    )
    db.add(news_item)
    db.commit()
    db.refresh(news_item)

    yield db

    db.commit()
    db.rollback()  # 테스트 종료 후 변경 사항 되돌리기
    db.close()  # 세션 종료
    Base.metadata.drop_all(bind=engine)  # 테스트 끝나면 DB 초기화

# ✅ FastAPI 의존성 오버라이드 설정
def override_get_db():
    """
    FastAPI 의존성 오버라이드용 함수.

    테스트용 DB 세션을 생성하여 반환하며,
    사용 후 세션을 안전하게 종료합니다.

    Yields:
        Session: 테스트용 SQLAlchemy DB 세션
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[db_manager.get_db] = override_get_db

# FastAPI 테스트 클라이언트
@pytest.fixture(scope="function")
def client():
    """
    FastAPI 테스트 클라이언트를 생성하여 반환합니다.

    Returns:
        TestClient: FastAPI 테스트 클라이언트 인스턴스
    """
    return TestClient(app)

# 정상 검색 테스트
@patch("app.routers.news.es.search")
def test_search_news_success(mock_es_search, client, test_db):
    """
    Elasticsearch에서 정상적으로 카테고리 검색 결과를 받아
    관련 채용 공고가 올바르게 반환되는지 검증하는 테스트입니다.
    """
    mock_es_search.side_effect = [
        {
            "hits": {
                "hits": [{
                    "_source": {
                        "category_name": "보건",
                        "category_id": 1,
                        "feature": "news"
                    }
                }]
            }
        },
        {
            "hits": {
                "hits": [{
                    "_source": {
                        "category_name": "보건",
                        "category_id": 1,
                        "feature": "news"
                    }
                }]
            }
        }
    ]

    response = client.get("/news/DB_search", params={"user_id": "user123", "keyword": "보건", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["matched_category"] == "보건"
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "보건 정책 변화"
    assert data["results"][0]["source"] == "뉴스타임"

# ✅ 사용자 미존재 테스트
def test_search_news_user_not_found(client, setup_database):
    """
    존재하지 않는 사용자 ID로 검색 요청 시
    404 에러 및 'User not found' 메시지가 반환되는지 확인합니다.
    """
    response = client.get("/news/DB_search", params={"user_id": "unknown", "keyword": "보건"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# ✅ 키워드 미일치 → 기본 카테고리 '기타' 처리
@patch("app.routers.news.es.search")
def test_search_news_no_matching_category(mock_es_search, client, test_db):
    """
    Elasticsearch에서 키워드에 해당하는 카테고리가 검색되지 않을 때
    기본값 '기타' 카테고리로 처리되고 빈 결과가 반환되는지 검증합니다.
    """
    mock_es_search.return_value = {"hits": {"hits": []}}
    response = client.get("/news/DB_search", params={"user_id": "user123", "keyword": "미확인키워드"})
    assert response.status_code == 200
    data = response.json()
    assert data["matched_category"] == "기타"
    assert data["results"] == []

# ✅ ES는 결과 줬지만 DB에 해당 category_id가 없음
@patch("app.routers.news.es.search")
def test_search_news_category_not_in_db(mock_es_search, client, test_db):
    """
    Elasticsearch에서는 검색 결과를 반환했지만,
    해당 category_id가 DB에 존재하지 않는 경우 빈 결과를 반환하는지 확인.
    """
    mock_es_search.return_value = {
        "hits": {
            "hits": [{
                "_source": {
                    "category_name": "존재하지않음",
                    "category_id": 9999,
                    "feature": "news"
                }
            }]
        }
    }
    response = client.get("/news/DB_search", params={"user_id": "user123", "keyword": "존재하지않음"})
    assert response.status_code == 200
    data = response.json()
    assert data["matched_category"] == "존재하지않음"
    assert data["results"] == []

# ✅ limit 파라미터 유효성 검증
@patch("app.routers.news.es.search")
def test_search_news_limit_param(mock_es_search, client, test_db):
    """
    뉴스 검색 시 limit 파라미터의 기본값, 지정값, 최대값 초과 시
    각각 올바르게 처리되는지 검증합니다.
    - 기본 limit 사용 (10)
    - limit 지정 사용
    - 최대값(100) 초과 시 422 에러 발생 확인
    """
    mock_es_search.return_value = {
        "hits": {
            "hits": [{
                "_source": {
                    "category_name": "보건",
                    "category_id": 1,
                    "feature": "news"
                }
            }]
        }
    }

    # 기본 limit = 10
    response = client.get("/news/DB_search", params={"user_id": "user123", "keyword": "보건"})
    assert response.status_code == 200
    assert "results" in response.json()

    # limit = 1
    response = client.get("/news/DB_search", params={"user_id": "user123", "keyword": "보건", "limit": 1})
    assert response.status_code == 200
    assert len(response.json()["results"]) <= 1

    # limit > 100 초과 → 422
    response = client.get("/news/DB_search", params={"user_id": "user123", "keyword": "보건", "limit": 101})
    assert response.status_code == 422

# ✅ Elasticsearch 연결 실패 시
@patch("app.routers.news.es.search", side_effect=ConnectionError)
def test_search_news_es_connection_error(mock_es_search, client, test_db):
    """
    Elasticsearch 연결 실패 시
    500 에러와 'Elasticsearch 연결 실패' 메시지가 반환되는지 확인합니다.
    """
    response = client.get("/news/DB_search", params={"user_id": "user123", "keyword": "보건"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Elasticsearch 연결 실패"}

# ✅ Elasticsearch 기타 예외 발생 시
@patch("app.routers.news.es.search", side_effect=Exception("ES 오류"))
def test_search_news_es_other_error(mock_es_search, client, test_db):
    """
    Elasticsearch 검색 중 알 수 없는 예외 발생 시
    500 에러와 예외 메시지가 포함된 응답이 반환되는지 검증합니다.
    """
    response = client.get("/news/DB_search", params={"user_id": "user123", "keyword": "보건"})
    assert response.status_code == 500
    assert "ES 오류" in response.json()["detail"]
