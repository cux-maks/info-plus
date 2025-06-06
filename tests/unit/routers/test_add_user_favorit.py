"""사용자 카테고리 구독 추가 API 테스트 모듈.

이 모듈은 사용자 카테고리 구독 추가 API의 기능을 테스트합니다.
주요 테스트 항목:
    - 새로운 카테고리 구독 추가 성공
    - 중복 카테고리 구독 방지
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.main import app
from app.models import Base, Category, Feature, UserCategory, Users
from app.utils.db_manager import db_manager

# ✅ 테스트용 SQLite 파일 DB (세션 유지)
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ DB 초기화 및 테이블 생성
@pytest.fixture(scope="function")
def setup_database():
    """테스트용 DB 테이블 생성 및 초기화를 수행합니다.

    Returns:
        None
    """
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON;"))  # ✅ 외래 키 활성화
        Base.metadata.drop_all(bind=conn)  # ✅ 기존 테이블 삭제
        Base.metadata.create_all(bind=conn)  # ✅ 테이블 생성

# ✅ DB 세션 생성 및 더미 데이터 삽입
@pytest.fixture(scope="function")
def test_db(setup_database):
    """테스트용 DB 세션을 생성하고 더미 데이터를 삽입합니다.

    Args:
        setup_database: DB 테이블 생성 및 초기화 fixture

    Yields:
        Session: 테스트용 DB 세션
    """
    db = TestingSessionLocal()

    # ✅ 기존 데이터 삭제 후 초기화
    db.query(UserCategory).delete()
    db.query(Category).delete()
    db.query(Feature).delete()
    db.query(Users).delete()
    db.commit()

    # ✅ 더미 데이터 추가 (한 번만 수행)
    user = Users(user_id="user123", user_name="John Doe")
    feature = Feature(feature_type="News")
    db.add_all([user, feature])
    db.commit()

    db.refresh(user)
    db.refresh(feature)

    category = Category(feature_id=feature.feature_id, category_name="Tech")
    db.add(category)
    db.commit()
    db.refresh(category)

    yield db  # ✅ 세션 제공

    db.rollback()  # ✅ 테스트 종료 후 변경 사항 되돌리기
    db.close()  # ✅ 세션 종료
    Base.metadata.drop_all(bind=engine)  # ✅ 테스트 끝나면 DB 초기화

# ✅ 테스트용 FastAPI 의존성 주입 함수 (DB 세션 주입)
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

# ✅ FastAPI 앱에 테스트용 DB 주입
app.dependency_overrides[db_manager.get_db] = override_get_db

# ✅ 테스트 클라이언트 생성
@pytest.fixture(scope="function")
def test_client():
    """테스트용 FastAPI 클라이언트를 생성합니다.

    Returns:
        TestClient: FastAPI 테스트 클라이언트 인스턴스
    """
    return TestClient(app)

# ✅ 새로운 카테고리 구독이 성공적으로 추가되는지 확인
def test_add_user_favorit_success(test_db, test_client):
    """새로운 카테고리 구독이 성공적으로 추가되는지 테스트합니다.

    Args:
        test_db: 테스트용 DB 세션 fixture
        test_client: FastAPI 테스트 클라이언트 fixture

    Returns:
        None
    """
    response = test_client.post(
        "/user/subscribe",
        json={"user_id": "user123", "category_id": 1}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Subscription successful!"}

# ✅ 이미 구독한 카테고리를 다시 추가하면 400 에러 반환 확인
def test_add_user_favorit_duplicate(test_db, test_client):
    """이미 구독한 카테고리를 다시 추가할 때 중복 구독 방지 테스트를 수행합니다.

    Args:
        test_db: 테스트용 DB 세션 fixture
        test_client: FastAPI 테스트 클라이언트 fixture

    Returns:
        None
    """
    response1 = test_client.post("/user/subscribe", json={"user_id": "user123", "category_id": 1})
    assert response1.status_code == 200  # ✅ 첫 번째 요청은 성공

    response2 = test_client.post("/user/subscribe", json={"user_id": "user123", "category_id": 1})
    assert response2.status_code == 400  # ✅ 두 번째 요청은 중복 에러
    assert response2.json() == {"detail": "Category 1 is already subscribed."}
