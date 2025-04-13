import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.main import app
from app.models import Base, Users, Feature, Category, UserCategory, Employee
from app.utils.db_manager import db_manager

# ✅ 테스트용 SQLite DB 설정
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ DB 초기화
@pytest.fixture(scope="function")
def setup_database():
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON;"))
        Base.metadata.drop_all(bind=conn)
        Base.metadata.create_all(bind=conn)

# ✅ 더미 데이터 삽입
@pytest.fixture(scope="function")
def test_db(setup_database):
    db = TestingSessionLocal()

    # 더미 데이터 삽입
    user = Users(user_id="user123", user_name="홍길동")
    feature = Feature(feature_type="employee")
    db.add_all([user, feature])
    db.commit()

    db.refresh(user)
    db.refresh(feature)

    category = Category(feature_id=feature.feature_id, category_name="AI")
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

    job1 = Employee(
        recruit_id="rec1",
        category_id=category.category_id,
        title="AI 연구원",
        institution="OpenAI",
        start_date="20250401",
        end_date="20250430",
        recrut_se="R2030", # 신입 + 경력
        hire_type_lst="R1040", # 비정규직
        ncs_cd_lst="R600006", # 보건, 의료
        detail_url="https://example.com/openai",
        recrut_pblnt_sn=280271,
    )
    job2 = Employee(
        recruit_id="rec2",
        category_id=category.category_id,
        title="AI 엔지니어",
        institution="Naver",
        start_date="20250405",
        end_date="20250505",
        recrut_se="R2010", # 신입
        hire_type_lst="R1010", # 정규직
        ncs_cd_lst="R600002", # 경영, 회계, 사무
        detail_url="https://example.com/naver",
        recrut_pblnt_sn=280272,
    )
    db.add_all([job1, job2])
    db.commit()

    yield db

    db.rollback()
    db.close()
    Base.metadata.drop_all(bind=engine)

# ✅ DB 의존성 오버라이딩
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[db_manager.get_db] = override_get_db

# ✅ FastAPI 클라이언트
@pytest.fixture(scope="function")
def test_client():
    return TestClient(app)

# ✅ 추천 성공 테스트
def test_recruit_recommendation_success(test_client: TestClient, test_db):
    response = test_client.get("/custom-employee-information/recommendation", params={"user_id": "user123", "limit": 2})
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["institution"] in ["OpenAI", "Naver"]

# ✅ 존재하지 않는 사용자 테스트
def test_recruit_recommendation_user_not_found(test_client: TestClient, test_db):
    response = test_client.get("/custom-employee-information/recommendation", params={"user_id": "ghost"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

# ✅ 구독 카테고리가 없는 경우 테스트
def test_recruit_recommendation_no_subscriptions(test_client: TestClient, test_db):
    # 사용자의 구독을 비활성화
    db = test_db
    db.query(UserCategory).filter(UserCategory.user_id == "user123").update({"is_active": False})
    db.commit()

    response = test_client.get("/custom-employee-information/recommendation", params={"user_id": "user123"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No active category subscriptions"}

# ✅ 채용 공고가 없는 경우 테스트
def test_recruit_recommendation_no_jobs(test_client: TestClient, test_db):
    # 채용공고 전체 삭제
    db = test_db
    db.query(Employee).delete()
    db.commit()

    response = test_client.get("/custom-employee-information/recommendation", params={"user_id": "user123"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No recruitment posts found for user's interests"}
