"""Feature별 카테고리 조회 API 테스트 모듈.

이 모듈은 Feature별 카테고리 조회 API의 기능을 테스트합니다.
주요 테스트 항목:
    - 존재하는 feature에 대한 카테고리 목록 조회
    - 존재하지 않는 feature에 대한 카테고리 목록 조회
    - 카테고리가 없는 feature에 대한 카테고리 목록 조회
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.main import app
from app.models import Base, Category, Feature, UserCategory, Users
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
    feature = Feature(feature_type="news")
    db.add(feature)
    db.commit()
    db.refresh(feature)  # id 생성 확인

    # 카테고리 추가
    categories = [
        Category(feature_id=feature.feature_id, category_name="IT/개발"),
        Category(feature_id=feature.feature_id, category_name="마케팅"),
        Category(feature_id=feature.feature_id, category_name="디자인"),
        Category(feature_id=feature.feature_id, category_name="경영/기획"),
        Category(feature_id=feature.feature_id, category_name="영업/제휴")
    ]
    for category in categories:
        db.add(category)
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

# 존재하는 feature에 대한 카테고리 목록 조회 성공 테스트
def test_get_categories_by_feature_success(test_db, test_client):
    """존재하는 feature에 대한 카테고리 목록 조회 성공 테스트를 수행합니다.

    Args:
        test_db: 테스트용 DB 세션 fixture
        test_client: FastAPI 테스트 클라이언트 fixture

    Returns:
        None
    """
    response = test_client.get("/user/categories/news")
    assert response.status_code == 200
    assert "IT/개발" in response.json()["message"]
    assert "마케팅" in response.json()["message"]
    assert "디자인" in response.json()["message"]
    assert "경영/기획" in response.json()["message"]
    assert "영업/제휴" in response.json()["message"]

# 존재하지 않는 feature에 대한 카테고리 목록 조회 실패 테스트
def test_get_categories_by_feature_not_found(test_db, test_client):
    """존재하지 않는 feature에 대한 카테고리 목록 조회 실패 테스트를 수행합니다.

    Args:
        test_db: 테스트용 DB 세션 fixture
        test_client: FastAPI 테스트 클라이언트 fixture

    Returns:
        None
    """
    response = test_client.get("/user/categories/NonExistentFeature")
    assert response.status_code == 404
    assert "Feature not found" in response.json()["detail"]

# 카테고리가 없는 feature에 대한 카테고리 목록 조회 테스트
def test_get_categories_by_feature_empty(test_db, test_client):
    """카테고리가 없는 feature에 대한 카테고리 목록 조회 테스트를 수행합니다.

    Args:
        test_db: 테스트용 DB 세션 fixture
        test_client: FastAPI 테스트 클라이언트 fixture

    Returns:
        None
    """
    # 새로운 feature 추가 (카테고리 없음)
    db = TestingSessionLocal()
    feature = Feature(feature_type="Movies")
    db.add(feature)
    db.commit()
    db.close()

    response = test_client.get("/user/categories/Movies")
    assert response.status_code == 200
    assert "아직 지원하는 카테고리가 없어요" in response.json()["message"]
