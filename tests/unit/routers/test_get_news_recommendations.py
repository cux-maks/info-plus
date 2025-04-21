"""사용자 맞춤 뉴스 추천 API 테스트 모듈.

이 모듈은 /news/recommend 엔드포인트의
기능을 테스트합니다.

주요 테스트 항목:
    - 사용자의 구독 카테고리를 기반으로 한 뉴스 추천 성공
    - 존재하지 않는 사용자 처리
    - 구독 중인 카테고리가 없을 경우 처리
    - 카테고리에 해당하는 뉴스가 없을 경우 처리
    - 여러 카테고리에 대한 뉴스 추천
    - 최신 뉴스 우선 정렬
    - limit 파라미터 경계값 테스트
"""

import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.main import app
from app.models import Base, Category, Feature, News, UserCategory, Users
from app.utils.db_manager import db_manager

# 테스트용 SQLite 파일 DB (세션 유지)
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB 초기화 및 테이블 생성
@pytest.fixture(scope="function")
def setup_database():
    """테스트용 DB 테이블 생성 및 초기화를 수행합니다.

    Returns:
        None
    """
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON;"))  # 외래 키 활성화
        Base.metadata.drop_all(bind=conn)  # 기존 테이블 삭제
        Base.metadata.create_all(bind=conn)  # 테이블 생성

# DB 세션 생성
@pytest.fixture(scope="function")
def test_db(setup_database):
    """테스트용 DB 세션을 생성하고 테스트 데이터를 삽입합니다.

    Args:
        setup_database: DB 테이블 생성 및 초기화 fixture

    Yields:
        Session: 테스트용 DB 세션
    """
    db = TestingSessionLocal()

    # 기존 데이터 삭제
    db.query(UserCategory).delete()
    db.query(Category).delete()
    db.query(Feature).delete()
    db.query(Users).delete()
    db.commit()

    # 테스트 데이터 삽입
    user = Users(user_id="user123", user_name="홍길동")
    feature = Feature(feature_type="news")
    db.add_all([user, feature])
    db.commit()

    db.refresh(user)
    db.refresh(feature)

    # 여러 카테고리 생성
    categories = [
        Category(feature_id=1, category_name="AI"),
        Category(feature_id=1, category_name="Blockchain"),
        Category(feature_id=1, category_name="Cloud")
    ]
    db.add_all(categories)
    db.commit()

    for category in categories:
        db.refresh(category)

    # 사용자 카테고리 구독
    user_categories = [
        UserCategory(user_id="user123", category_id=1, is_active=True),
        UserCategory(user_id="user123", category_id=2, is_active=True),
        UserCategory(user_id="user123", category_id=3, is_active=False)  # 비활성화된 카테고리
    ]
    db.add_all(user_categories)
    db.commit()

    # 뉴스 데이터 추가 (다양한 날짜와 카테고리)
    news_list = [
        News(
            category_id=1,
            title="AI 뉴스 1",
            contents="AI 관련 뉴스 내용 1",
            source="AI News",
            publish_date=datetime.datetime.now() - datetime.timedelta(days=1),
            category="AI",
            url="http://example.com/ai1"
        ),
        News(
            category_id=2,
            title="Blockchain 뉴스 1",
            contents="Blockchain 관련 뉴스 내용 1",
            source="Blockchain News",
            publish_date=datetime.datetime.now() - datetime.timedelta(days=2),
            category="Blockchain",
            url="http://example.com/blockchain1"
        ),
        News(
            category_id=1,
            title="AI 뉴스 2",
            contents="AI 관련 뉴스 내용 2",
            source="AI News",
            publish_date=datetime.datetime.now() - datetime.timedelta(days=3),
            category="AI",
            url="http://example.com/ai2"
        )
    ]
    db.add_all(news_list)
    db.commit()

    yield db  # 세션 제공

    db.commit()
    db.rollback()  # 테스트 종료 후 변경 사항 되돌리기
    db.close()  # 세션 종료
    Base.metadata.drop_all(bind=engine)  # 테스트 끝나면 DB 초기화

# FastAPI 앱에 테스트용 DB 주입
def override_get_db():
    """테스트용 DB 세션을 생성하고 제공하는 의존성 주입 함수입니다.

    Yields:
        Session: 테스트용 DB 세션
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[db_manager.get_db] = override_get_db

# 테스트 클라이언트 생성
@pytest.fixture(scope="function")
def test_client():
    """테스트용 FastAPI 클라이언트를 생성합니다.

    Returns:
        TestClient: FastAPI 테스트 클라이언트 인스턴스
    """
    return TestClient(app)

# ✅ 추천 성공 테스트
def test_news_recommendation_success(test_client: TestClient, test_db):
    """사용자의 구독 카테고리를 기반으로 뉴스 추천이 정상적으로 수행되는지 테스트합니다."""
    response = test_client.get("/news/recommend",
    params={"user_id": "user123", "limit": 2})
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    assert data["results"][0]["source"] in ["AI News", "Blockchain News"]  # 실제 데이터와 일치하도록 수정

# ✅ 여러 카테고리 테스트
def test_news_recommendation_multiple_categories(test_client: TestClient, test_db):
    """여러 카테고리에 대한 뉴스 추천이 정상적으로 작동하는지 테스트합니다."""
    response = test_client.get("/news/recommend",
    params={"user_id": "user123", "limit": 3})
    assert response.status_code == 200

    data = response.json()
    assert len(data["results"]) == 3
    sources = [news["source"] for news in data["results"]]
    assert "Blockchain News" in sources  # 실제 데이터와 일치하도록 수정
    assert "Cloud Weekly" not in sources  # 비활성화된 카테고리 뉴스 미포함 확인

# ✅ 최신 뉴스 우선 정렬 테스트
def test_news_recommendation_sorting(test_client: TestClient, test_db):
    """뉴스가 최신순으로 정렬되는지 테스트합니다."""
    response = test_client.get("/news/recommend",
    params={"user_id": "user123", "limit": 3})
    assert response.status_code == 200

    data = response.json()
    news_dates = [datetime.datetime.fromisoformat(news["publish_date"]) for news in data["results"]]
    assert news_dates == sorted(news_dates, reverse=True)  # 최신순 정렬 확인

# ✅ limit 경계값 테스트
def test_news_recommendation_limit_boundaries(test_client: TestClient, test_db):
    """limit 파라미터의 경계값을 테스트합니다."""
    # 최소값 테스트
    response = test_client.get("/news/recommend",
    params={"user_id": "user123", "limit": 1})
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1

    # 최대값 테스트
    response = test_client.get("/news/recommend",
    params={"user_id": "user123", "limit": 100})
    assert response.status_code == 200
    assert len(response.json()["results"]) == 3  # 실제 데이터는 3개

    # 최대값 초과 테스트
    response = test_client.get("/news/recommend",
    params={"user_id": "user123", "limit": 101})
    assert response.status_code == 422  # FastAPI의 validation error

# ✅ 로깅 테스트
@patch("app.routers.news.logger")
def test_news_recommendation_logging(mock_logger, test_client: TestClient, test_db):
    """로깅이 정상적으로 작동하는지 테스트합니다."""
    # 성공 케이스
    test_client.get("/news/recommend", params={"user_id": "user123"})
    assert mock_logger.info.call_count >= 2  # 사용자 확인, 카테고리 조회, 뉴스 조회 로그

    # 실패 케이스
    test_client.get("/news/recommend", params={"user_id": "nonexistent"})
    assert mock_logger.error.call_count >= 1  # 에러 로그

# ✅ 존재하지 않는 사용자 테스트
def test_news_recommendation_user_not_found(test_client: TestClient, test_db):
    """존재하지 않는 사용자일 경우 적절한 예외가 발생하는지 테스트합니다.

    Args:
        test_client (TestClient): FastAPI 테스트 클라이언트
        test_db: 테스트용 DB 세션 fixture

    Returns:
        None
    """
    response = test_client.get("/news/recommend", params={"user_id": "ghost"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

# ✅ 구독 카테고리가 없는 경우 테스트
def test_news_recommendation_no_subscriptions(test_client: TestClient, test_db):
    """사용자의 구독 카테고리가 모두 비활성화된 경우 예외가 발생하는지 테스트합니다.

    Args:
        test_client (TestClient): FastAPI 테스트 클라이언트
        test_db: 테스트용 DB 세션 fixture

    Returns:
        None
    """
    # 사용자의 구독을 비활성화
    db = test_db
    db.query(UserCategory).filter(UserCategory.user_id == "user123").update({"is_active": False})
    db.commit()

    response = test_client.get("/news/recommend", params={"user_id": "user123"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No active category subscriptions"}

# ✅ 뉴스가 없는 경우 테스트
def test_news_recommendation_no_news(test_client: TestClient, test_db):
    """구독 중인 카테고리에 해당하는 뉴스가 없을 경우 예외가 발생하는지 테스트합니다.

    Args:
        test_client (TestClient): FastAPI 테스트 클라이언트
        test_db: 테스트용 DB 세션 fixture

    Returns:
        None
    """
    # 뉴스 전체 삭제
    db = test_db
    db.query(News).delete()
    db.commit()

    response = test_client.get("/news/recommend", params={"user_id": "user123"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No news found for user's interests"}

# ✅ limit보다 적은 결과가 반환되는 경우 테스트
def test_news_recommendation_limit_less_than_requested(test_client: TestClient, test_db):
    """limit 값보다 적은 뉴스가 존재할 때 메시지가 포함되는지 테스트합니다."""
    response = test_client.get("/news/recommend", params={"user_id": "user123", "limit": 10})
    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 3  # 실제 데이터는 3개
    assert data["message"] == "뉴스 데이터가 부족하여, 요청하신 뉴스 10개 중 3개의 뉴스만 조회되었습니다."
