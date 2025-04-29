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
    """테스트용 DB 테이블 생성 및 초기화"""
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON;"))  # ✅ 외래 키 활성화
        Base.metadata.drop_all(bind=conn)  # ✅ 기존 테이블 삭제
        Base.metadata.create_all(bind=conn)  # ✅ 테이블 생성

# ✅ DB 세션 생성 및 더미 데이터 삽입
@pytest.fixture(scope="function")
def test_db(setup_database):
    """각 테스트 실행 전 세션을 초기화하고 더미 데이터 삽입"""
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

    user_category = UserCategory(
        user_id=user.user_id,
        category_id=category.category_id,
        is_active=True
    )
    db.add(user_category)
    db.commit()


    yield db  # ✅ 세션 제공

    db.rollback()  # ✅ 테스트 종료 후 변경 사항 되돌리기
    db.close()  # ✅ 세션 종료
    Base.metadata.drop_all(bind=engine)  # ✅ 테스트 끝나면 DB 초기화

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

# ✅ 사용자가 존재하고 해당 사용자의 구독 카테고리 목록이 정상 반환된 경우
def test_get_category_list_success(test_client: TestClient, test_db):
    """구독 중인 카테고리 목록 정상 조회 테스트"""
    response = test_client.get("/user/user123")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["category_name"] == "Tech"

# ✅ 사용자가 없을 경우: 404 응답
def test_get_category_list_user_not_found(test_client: TestClient, test_db):
    """존재하지 않는 사용자에 대한 조회 테스트"""
    response = test_client.get("/user/invalid_user")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}
