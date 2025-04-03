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
    db.query(Users).delete()
    db.query(Feature).delete()
    db.query(Category).delete()
    db.query(UserCategory).delete()
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

    category = Category(feature_id = 1, category_name = "Tech")
    db.add(category)
    db.commit()
    db.refresh(category)  # ✅ id 생성 확인

    yield db  # ✅ 세션 제공

    db.rollback()  # ✅ 테스트 종료 후 변경 사항 되돌리기
    db.close()  # ✅ 세션 종료

# ✅ 테스트용 FastAPI 의존성 주입 함수 (DB 세션 주입)
def override_get_db():
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
    """테스트용 FastAPI 클라이언트"""
    return TestClient(app)

# ✅ 새로운 카테고리 구독이 성공적으로 추가되는지 확인
def test_add_user_favorit_success(test_db, test_client):
    response = test_client.post(
        "/user/add/favorit",
        json={"user_id": "user123", "category_id": 1}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Subscription successful!"}

# ✅ 이미 구독한 카테고리를 다시 추가하면 400 에러 반환 확인
def test_add_user_favorit_duplicate(test_db, test_client):
    test_client.post("/user/add/favorit", json={"user_id": "user123", "category_id": 1})

    response = test_client.post("/user/add/favorit", json={"user_id": "user123", "category_id": 1})

    assert response.status_code == 400
    assert response.json() == {"detail": "Already subscribed to this category."}
