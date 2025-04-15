"""사용자 맞춤 채용 공고 추천 API 테스트 모듈.

이 모듈은 /employee/recommend 엔드포인트의
기능을 테스트합니다.

주요 테스트 항목:
    - 사용자의 구독 카테고리를 기반으로 한 채용 공고 추천 성공
    - 존재하지 않는 사용자 처리
    - 구독 중인 카테고리가 없을 경우 처리
    - 카테고리에 해당하는 채용 공고가 없을 경우 처리
"""

import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.main import app
from app.models import Base, Category, Employee, Feature, UserCategory, Users
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
    feature = Feature(feature_type="employee")
    db.add_all([user, feature])
    db.commit()

    db.refresh(user)
    db.refresh(feature)

    category = Category(feature_id=1, category_name="AI")
    db.add(category)
    db.commit()
    db.refresh(category)

    user_category = UserCategory(user_id="user123", category_id=1, is_active=True)
    db.add(user_category)
    db.commit()
    db.refresh(user_category)

    # 채용 공고 추
    job1 = Employee(
        recruit_id="rec1",
        category_id=1,
        title="AI 연구원",
        institution="OpenAI",
        start_date=datetime.date(2025, 4, 1),
        end_date=datetime.date(2025, 4, 30),
        recrut_se="R2030", # 신입 + 경력
        hire_type_lst="R1040", # 비정규직
        ncs_cd_lst="R600006", # 보건, 의료
        detail_url="https://example.com/openai",
        recrut_pblnt_sn=280271,
    )
    job2 = Employee(
        recruit_id="rec2",
        category_id=1,
        title="AI 엔지니어",
        institution="Naver",
        start_date=datetime.date(2025, 4, 5),
        end_date=datetime.date(2025, 5, 5),
        recrut_se="R2010", # 신입
        hire_type_lst="R1010", # 정규직
        ncs_cd_lst="R600002", # 경영, 회계, 사무
        detail_url="https://example.com/naver",
        recrut_pblnt_sn=280272,
    )
    db.add_all([job1, job2])
    db.commit()

    yield db # 세션 제공

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
def test_recruit_recommendation_success(test_client: TestClient, test_db):
    """사용자의 구독 카테고리를 기반으로 채용 공고 추천이 정상적으로 수행되는지 테스트합니다.

    Args:
        test_client (TestClient): FastAPI 테스트 클라이언트
        test_db: 테스트용 DB 세션 fixture

    Returns:
        None
    """
    response = test_client.get("/employee/recommend",
    params={"user_id": "user123", "limit": 2})
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["institution"] in ["OpenAI", "Naver"]

# ✅ 존재하지 않는 사용자 테스트
def test_recruit_recommendation_user_not_found(test_client: TestClient, test_db):
    """존재하지 않는 사용자일 경우 적절한 예외가 발생하는지 테스트합니다.

    Args:
        test_client (TestClient): FastAPI 테스트 클라이언트
        test_db: 테스트용 DB 세션 fixture

    Returns:
        None
    """
    response = test_client.get("/employee/recommend", params={"user_id": "ghost"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

# ✅ 구독 카테고리가 없는 경우 테스트
def test_recruit_recommendation_no_subscriptions(test_client: TestClient, test_db):
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

    response = test_client.get("/employee/recommend", params={"user_id": "user123"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No active category subscriptions"}

# ✅ 채용 공고가 없는 경우 테스트
def test_recruit_recommendation_no_jobs(test_client: TestClient, test_db):
    """구독 중인 카테고리에 해당하는 채용 공고가 없을 경우 예외가 발생하는지 테스트합니다.

    Args:
        test_client (TestClient): FastAPI 테스트 클라이언트
        test_db: 테스트용 DB 세션 fixture

    Returns:
        None
    """
    # 채용공고 전체 삭제
    db = test_db
    db.query(Employee).delete()
    db.commit()

    response = test_client.get("/employee/recommend", params={"user_id": "user123"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No recruitment posts found for user's interests"}

# ✅ limit보다 적은 결과가 반환되는 경우 테스트
def test_recruit_recommendation_limit_less_than_requested(test_client: TestClient, test_db):
    """limit 값보다 적은 채용 공고가 존재할 때 메시지가 포함되는지 테스트합니다."""
    response = test_client.get("/employee/recommend", params={"user_id": "user123", "limit": 10})
    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    assert data["message"] == "요청한 limit 10개 중 2개의 채용공고만 조회되었습니다."
    