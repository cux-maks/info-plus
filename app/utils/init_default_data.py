"""기본 데이터를 삽입하는 유틸리티 모듈.
이 모듈은 Feature, Category, Employee 테이블에 기본 데이터를 삽입하는 함수들을 포함합니다.
"""

from sqlalchemy.exc import IntegrityError
from app.models.feature import Feature
from app.models.category import Category
from app.models.employee import Employee


def add_default_features(db):
    """기본 Feature 데이터를 추가합니다."""
    features = [
        Feature(feature_type="news"),
        Feature(feature_type="employee")
    ]
    for feature in features:
        db.add(feature)


def add_default_categories(db):
    """기본 Category 데이터를 추가합니다. Feature가 선행되어 있어야 함."""
    feature_news = db.query(Feature).filter_by(feature_type="news").first()
    feature_employee = db.query(Feature).filter_by(feature_type="employee").first()

    categories = [
        Category(category_name="IT/개발", feature=feature_news),
        Category(category_name="마케팅", feature=feature_news),
        Category(category_name="디자인", feature=feature_news),
        Category(category_name="경영/기획", feature=feature_news),
        Category(category_name="영업/제휴", feature=feature_news),
        Category(category_name="인사/채용", feature=feature_employee),
        Category(category_name="재무/회계", feature=feature_employee),
        Category(category_name="법무/법률", feature=feature_employee),
        Category(category_name="생산/제조", feature=feature_employee),
        Category(category_name="물류/유통", feature=feature_employee)
    ]
    for category in categories:
        db.add(category)


def add_default_employees(db):
    """기본 Employee(채용 공고) 데이터를 추가합니다."""
    employees = [
        Employee(
            recruit_id="RECR20250401",
            category_id=1,
            title="데이터 분석가 채용",
            institution="한국정보화진흥원",
            start_date="2025-04-01",
            end_date="2025-04-15",
            recrut_se="경력",
            hire_type_lst="정규직",
            ncs_cd_lst="20010101",
            detail_url="https://opendata.alio.go.kr/recruit1",
            recrut_pblnt_sn=101001,
        ),
        Employee(
            recruit_id="RECR20250402",
            category_id=2,
            title="프론트엔드 개발자 모집",
            institution="공공데이터진흥원",
            start_date="2025-04-03",
            end_date="2025-04-17",
            recrut_se="신입",
            hire_type_lst="계약직",
            ncs_cd_lst="20010102",
            detail_url="https://opendata.alio.go.kr/recruit2",
            recrut_pblnt_sn=101002,
        ),
        Employee(
            recruit_id="RECR20250403",
            category_id=1,
            title="AI 모델링 전문가",
            institution="국가과학기술연구회",
            start_date="2025-04-05",
            end_date="2025-04-20",
            recrut_se="경력",
            hire_type_lst="정규직",
            ncs_cd_lst="20010103",
            detail_url="https://opendata.alio.go.kr/recruit3",
            recrut_pblnt_sn=101003,
        ),
        Employee(
            recruit_id="RECR20250404",
            category_id=3,
            title="백엔드 엔지니어 채용",
            institution="한국전자통신연구원",
            start_date="2025-04-07",
            end_date="2025-04-21",
            recrut_se="경력",
            hire_type_lst="정규직",
            ncs_cd_lst="20010104",
            detail_url="https://opendata.alio.go.kr/recruit4",
            recrut_pblnt_sn=101004,
        ),
        Employee(
            recruit_id="RECR20250405",
            category_id=2,
            title="UX/UI 디자이너 채용",
            institution="한국문화정보원",
            start_date="2025-04-08",
            end_date="2025-04-22",
            recrut_se="신입",
            hire_type_lst="계약직",
            ncs_cd_lst="20010105",
            detail_url="https://opendata.alio.go.kr/recruit5",
            recrut_pblnt_sn=101005,
        )
    ]
    for emp in employees:
        db.add(emp)
