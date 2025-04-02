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
@pytest.fixture(scope="session")
def setup_database():
    """테스트용 DB 테이블 생성 및 초기화"""
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON;"))  # ✅ 외래 키 활성화
        Base.metadata.drop_all(bind=conn)  # ✅ 기존 테이블 삭제
        Base.metadata.create_all(bind=conn)  # ✅ 테이블 생성

# ✅ DB 세션 생성
@pytest.fixture(scope="function")
def test_db(setup_database):
    """각 테스트 실행 전 세션을 초기화"""
    db = TestingSessionLocal()

    # ✅ 기존 데이터 삭제
    db.query(UserCategory).delete()
    db.query(Users).delete()
    db.query(Feature).delete()
    db.query(Category).delete()
    db.commit()

    # ✅ 테스트 데이터 삽입
    user = Users(user_id="user123", user_name="John Doe")
    db.add(user)
    db.commit()

    feature = Feature(feature_type="News")
    db.add(feature)
    db.commit()

    category = Category(id=1, feature_id=feature.id, category_name="Tech")
    db.add(category)
    db.commit()

    subscription = UserCategory(user_id="user123", category_id=1, is_active=True)
    db.add(subscription)
    db.commit()

    yield db  # ✅ 세션 제공

    db.rollback()  # ✅ 테스트 종료 후 변경 사항 되돌리기
    db.close()  # ✅ 세션 종료

# ✅ FastAPI 앱에 테스트용 DB 주입
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[db_manager.get_db] = override_get_db

# ✅ 테스트 클라이언트 생성
@pytest.fixture(scope="function")
def test_client():
    """테스트용 FastAPI 클라이언트"""
    return TestClient(app)

# ✅ 정상적인 구독 해제 요청 (is_active = False로 변경되는지 확인)
def test_delete_user_favorit_success(test_db, test_client):
    response = test_client.delete(
        "/delete/favorit",
        json={"user_id": "user123", "category_id": 1}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Subscription successfully deactivated."}

    # ✅ DB에서 확인
    db = test_db
    subscription = db.query(UserCategory).filter(
        UserCategory.user_id == "user123",
        UserCategory.category_id == 1
    ).first()
    assert subscription.is_active is False

# ✅ 존재하지 않는 사용자 요청 → 404 반환
def test_delete_user_favorit_invalid_user(test_db, test_client):
    response = test_client.delete(
        "/delete/favorit",
        json={"user_id": "invalid_user", "category_id": 1}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}

# ✅ 존재하지 않는 카테고리 요청 → 404 반환
def test_delete_user_favorit_invalid_category(test_db, test_client):
    response = test_client.delete(
        "/delete/favorit",
        json={"user_id": "user123", "category_id": 9999}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found."}

# ✅ 구독하지 않은 카테고리 삭제 요청 → 404 반환
def test_delete_user_favorit_not_subscribed(test_db, test_client):
    response = test_client.delete(
        "/delete/favorit",
        json={"user_id": "user123", "category_id": 2}  # 존재하지 않는 카테고리 ID
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Subscription not found."}

# ✅ 이미 비활성화된 구독 삭제 요청 → 400 반환
def test_delete_user_favorit_already_inactive(test_db, test_client):
    # ✅ 먼저 정상 삭제 요청 실행
    test_client.delete("/delete/favorit", json={"user_id": "user123", "category_id": 1})

    # ✅ 다시 삭제 요청하면 400 에러 발생해야 함
    response = test_client.delete(
        "/delete/favorit",
        json={"user_id": "user123", "category_id": 1}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Subscription is already inactive."}
