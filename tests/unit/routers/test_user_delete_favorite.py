"""사용자 카테고리 구독 해제 API 테스트 모듈.

이 모듈은 사용자 카테고리 구독 해제 API의 기능을 테스트합니다.
주요 테스트 항목:
    - 정상적인 구독 해제
    - 존재하지 않는 사용자 구독 해제 시도
    - 존재하지 않는 카테고리 구독 해제 시도
    - 구독하지 않은 카테고리 해제 시도
    - 이미 비활성화된 구독 해제 시도
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

# ✅ DB 세션 생성
@pytest.fixture(scope="function")
def test_db(setup_database):
    """테스트용 DB 세션을 생성하고 테스트 데이터를 삽입합니다.

    Args:
        setup_database: DB 테이블 생성 및 초기화 fixture

    Yields:
        Session: 테스트용 DB 세션
    """
    db = TestingSessionLocal()

    # ✅ 기존 데이터 삭제
    db.query(UserCategory).delete()
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

    # ✅ 두 개의 카테고리 추가 (Tech - 구독, Sports - 구독X)
    category1 = Category(feature_id=1, category_name="Tech")
    db.add(category1)
    db.commit()
    db.refresh(category1)  # ✅ id 생성 확인

    category2 = Category(feature_id=1, category_name="Sports")
    db.add(category2)
    db.commit()
    db.refresh(category2)  # ✅ id 생성 확인 (구독되지 않은 카테고리)

    subscription = UserCategory(user_id="user123", category_id=1, is_active=True)
    db.add(subscription)
    db.commit()
    db.refresh(subscription)  # ✅ id 생성 확인

    yield db  # ✅ 세션 제공

    db.commit()
    db.rollback()  # ✅ 테스트 종료 후 변경 사항 되돌리기
    db.close()  # ✅ 세션 종료
    Base.metadata.drop_all(bind=engine)  # ✅ 테스트 끝나면 DB 초기화

# ✅ FastAPI 앱에 테스트용 DB 주입
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

# ✅ 테스트 클라이언트 생성
@pytest.fixture(scope="function")
def test_client():
    """테스트용 FastAPI 클라이언트를 생성합니다.

    Returns:
        TestClient: FastAPI 테스트 클라이언트 인스턴스
    """
    return TestClient(app)

# ✅ 정상적인 구독 해제 요청 (is_active = False로 변경되는지 확인)
def test_delete_user_favorit_success(test_db, test_client):
    """정상적인 구독 해제 요청이 성공적으로 처리되는지 테스트합니다.

    Args:
        test_db: 테스트용 DB 세션 fixture
        test_client: FastAPI 테스트 클라이언트 fixture

    Returns:
        None
    """
    response = test_client.delete(
        "/user/delete/favorit",
        params={"user_id": "user123", "category_id": 1}  # ✅ params 사용
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Subscription successfully deactivated."}

    # ✅ DB에서 변경 사항 확인
    db = test_db
    db.commit()  # 🔥 변경 사항 반영

    # ✅ subscription 객체를 먼저 가져온 후 refresh()
    subscription = db.query(UserCategory).filter(
        UserCategory.user_id == "user123",
        UserCategory.category_id == 1
    ).first()

    assert subscription is not None  # ✅ 존재 여부 확인
    db.refresh(subscription)  # ✅ 변경 사항 반영
    assert subscription.is_active is False  # ✅ is_active가 False로 변경되었는지 확인

# ✅ 존재하지 않는 사용자 요청 → 404 반환
def test_delete_user_favorit_invalid_user(test_db, test_client):
    """존재하지 않는 사용자의 구독 해제 요청 시 404 에러를 반환하는지 테스트합니다.

    Args:
        test_db: 테스트용 DB 세션 fixture
        test_client: FastAPI 테스트 클라이언트 fixture

    Returns:
        None
    """
    response = test_client.delete(
        "/user/delete/favorit",
        params={"user_id": "invalid_user", "category_id": 1}  # ✅ params 사용
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}

# ✅ 존재하지 않는 카테고리 요청 → 404 반환
def test_delete_user_favorit_invalid_category(test_db, test_client):
    """존재하지 않는 카테고리의 구독 해제 요청 시 404 에러를 반환하는지 테스트합니다.

    Args:
        test_db: 테스트용 DB 세션 fixture
        test_client: FastAPI 테스트 클라이언트 fixture

    Returns:
        None
    """
    response = test_client.delete(
        "/user/delete/favorit",
        params={"user_id": "user123", "category_id": 9999}  # ✅ params 사용
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found."}

# ✅ 구독하지 않은 카테고리 삭제 요청 → 404 반환
def test_delete_user_favorit_not_subscribed(test_db, test_client):
    """구독하지 않은 카테고리의 구독 해제 요청 시 404 에러를 반환하는지 테스트합니다.

    Args:
        test_db: 테스트용 DB 세션 fixture
        test_client: FastAPI 테스트 클라이언트 fixture

    Returns:
        None
    """
    response = test_client.delete(
        "/user/delete/favorit",
        params={"user_id": "user123", "category_id": 2}  # ✅ 존재하지 않는 카테고리 ID
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Subscription not found."}

# ✅ 이미 비활성화된 구독 삭제 요청 → 400 반환
def test_delete_user_favorit_already_inactive(test_db, test_client):
    """이미 비활성화된 구독의 해제 요청 시 400 에러를 반환하는지 테스트합니다.

    Args:
        test_db: 테스트용 DB 세션 fixture
        test_client: FastAPI 테스트 클라이언트 fixture

    Returns:
        None
    """
    # ✅ 먼저 정상 삭제 요청 실행
    test_client.delete("/user/delete/favorit", params={"user_id": "user123", "category_id": 1})

    # ✅ 다시 삭제 요청하면 400 에러 발생해야 함
    response = test_client.delete(
        "/user/delete/favorit",
        params={"user_id": "user123", "category_id": 1}  # ✅ params 사용
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Subscription is already inactive."}
