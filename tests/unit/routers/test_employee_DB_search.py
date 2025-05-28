"""
사용자 맞춤 카테고리 기반 채용 공고 검색 API 테스트 모듈.

이 모듈은 /DB_search 엔드포인트의 기능을 테스트합니다.

주요 테스트 항목:
    - 정상적인 키워드 검색 및 채용 공고 반환
    - 존재하지 않는 사용자 처리
    - Elasticsearch에서 카테고리 미검색 시 기본 카테고리 처리
    - 해당 카테고리에 채용 공고가 없을 경우 처리
    - limit 파라미터 동작 확인 (최대 개수 제한 등)
"""

import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from unittest.mock import patch

from app.main import app
from app.models import (
    Base,
    Category,
    Employee,
    EmployeeCategory,
    Feature,
    Users,
    HireType,
    EmployeeHireType,
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

# 테스트 DB 세션 생성 및 테스트 데이터 삽입
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

    # 테스트 데이터 삽입
    user = Users(user_id="user123", user_name="홍길동")
    feature = Feature(feature_type="employee")
    db.add_all([user, feature])
    db.commit()

    db.refresh(user)
    db.refresh(feature)

    category = Category(feature_id=1, category_name="정보통신")
    db.add(category)
    db.commit()
    db.refresh(category)

    hire_type = HireType(hire_type_id=1, hire_type_name="정규직", hire_type_code="R1010")
    db.add(hire_type)
    db.commit()
    db.refresh(hire_type)

    # 채용 공고 추가
    job = Employee(
        recruit_id=1,
        title="정보통신 개발자",
        institution="TechCorp",
        start_date=datetime.date(2025, 5, 1),
        end_date=datetime.date(2025, 5, 31),
        recrut_se="R2010",
        detail_url="https://example.com/job1",
        recrut_pblnt_sn=123456,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    employee_category = EmployeeCategory(
        recruit_id=1,
        category_id=1, # AI 카테고리
        )
    db.add(employee_category)
    db.commit()

    employee_hire_type = EmployeeHireType(
        recruit_id=1,
        hire_type_id=1, # 정규직
        )
    db.add(employee_hire_type)
    db.commit()

    yield db # 세션 제공

    db.commit()
    db.rollback()  # 테스트 종료 후 변경 사항 되돌리기
    db.close()  # 세션 종료
    Base.metadata.drop_all(bind=engine)  # 테스트 끝나면 DB 초기화

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

@pytest.fixture(scope="function")
def client():
    """
    FastAPI 테스트 클라이언트를 생성하여 반환합니다.

    Returns:
        TestClient: FastAPI 테스트 클라이언트 인스턴스
    """
    return TestClient(app)

# 🔹 정상 검색 테스트
@patch("app.routers.employee.es.search")  # es.search 함수 패치 (실제 ES 호출 방지)
def test_search_employees_success(mock_es_search, client, test_db):
    """
    Elasticsearch에서 정상적으로 카테고리 검색 결과를 받아
    관련 채용 공고가 올바르게 반환되는지 검증하는 테스트입니다.
    """
    # Elasticsearch가 "정보통신" 카테고리 검색 결과 반환 모킹
    mock_es_search.return_value = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "category_name": "정보통신",
                        "category_id": 1,
                        "feature": "employee"
                    }
                }
            ]
        }
    }

    response = client.get("/employee/DB_search", params={"user_id": "user123", "keyword": "정보통신", "limit": 5})
    assert response.status_code == 200

    data = response.json()
    assert data["matched_category"] == "정보통신"
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "정보통신 개발자"
    assert data["results"][0]["institution"] == "TechCorp"

# 🔹 사용자 미존재 테스트
def test_search_employees_user_not_found(client, setup_database):
    """
    존재하지 않는 사용자 ID로 검색 요청 시
    404 에러 및 'User not found' 메시지가 반환되는지 확인합니다.
    """
    response = client.get("/employee/DB_search", params={"user_id": "unknown", "keyword": "정보통신"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

# 🔹 Elasticsearch에서 카테고리 미검색 시 기본값 처리 테스트
@patch("app.routers.employee.es.search")
def test_search_employees_no_category_found(mock_es_search, client, test_db):
    """
    Elasticsearch에서 키워드에 해당하는 카테고리가 검색되지 않을 때
    기본값 '기타' 카테고리로 처리되고 빈 결과가 반환되는지 검증합니다.
    """
    mock_es_search.return_value = {"hits": {"hits": []}}  # 검색 결과 없음

    response = client.get("/employee/DB_search", params={"user_id": "user123", "keyword": "없는카테고리"})
    assert response.status_code == 200
    data = response.json()
    assert data["matched_category"] == "기타"
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 0  # 기본 category_id=0 이므로 관련 공고 없음

# 🔹 해당 카테고리에 채용 공고가 없을 경우
@patch("app.routers.employee.es.search")
def test_search_employees_no_jobs_in_category(mock_es_search, client, test_db):
    """
    검색된 카테고리는 존재하나 해당 카테고리에 등록된 채용 공고가 없을 때
    빈 결과 리스트가 반환되는지 확인하는 테스트입니다.
    """
    # 검색된 카테고리 ID를 존재하나, 해당 카테고리에 공고 없음
    mock_es_search.return_value = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "category_name": "정보통신",
                        "category_id": 9999,  # 존재하지 않는 카테고리ID
                        "feature": "employee"
                    }
                }
            ]
        }
    }

    response = client.get("/employee/DB_search", params={"user_id": "user123", "keyword": "정보통신"})
    assert response.status_code == 200
    data = response.json()
    assert data["matched_category"] == "정보통신"
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 0

# 🔹 limit 파라미터 테스트 (최대 100, 기본 10 등)
@patch("app.routers.employee.es.search")
def test_search_employees_limit_param(mock_es_search, client, test_db):
    """
    검색 시 limit 파라미터의 기본값, 지정값, 최대값 초과 시
    각각 올바르게 처리되는지 검증합니다.
    - 기본 limit 사용
    - limit 지정 사용
    - 최대값(100) 초과 시 422 에러 발생 확인
    """
    mock_es_search.return_value = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "category_name": "정보통신",
                        "category_id": 1,
                        "feature": "employee"
                    }
                }
            ]
        }
    }

    # 기본 limit=10
    response = client.get("/employee/DB_search", params={"user_id": "user123", "keyword": "정보통신"})
    assert response.status_code == 200

    # limit=1 지정
    response = client.get("/employee/DB_search", params={"user_id": "user123", "keyword": "정보통신", "limit": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= 1

    # limit가 최대 100 초과 시도 (FastAPI에서 자동 검증되어 422 에러가 발생할 것)
    response = client.get("/employee/DB_search", params={"user_id": "user123", "keyword": "정보통신", "limit": 101})
    assert response.status_code == 422  # 유효성 검증 실패


# 🔹 Elasticsearch 연결 실패 예외 테스트
@patch("app.routers.employee.es.search", side_effect=ConnectionError)
def test_search_employees_es_connection_error(mock_es_search, client, test_db):
    """
    Elasticsearch 연결 실패 시
    500 에러와 'Elasticsearch 연결 실패' 메시지가 반환되는지 확인합니다.
    """
    response = client.get("/employee/DB_search", params={"user_id": "user123", "keyword": "정보통신"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Elasticsearch 연결 실패"}

# 🔹 Elasticsearch 기타 예외 테스트
@patch("app.routers.employee.es.search", side_effect=Exception("ES 오류"))
def test_search_employees_es_other_error(mock_es_search, client, test_db):
    """
    Elasticsearch 검색 중 알 수 없는 예외 발생 시
    500 에러와 예외 메시지가 포함된 응답이 반환되는지 검증합니다.
    """
    response = client.get("/employee/DB_search", params={"user_id": "user123", "keyword": "정보통신"})
    assert response.status_code == 500
    assert "ES 오류" in response.json()["detail"]
