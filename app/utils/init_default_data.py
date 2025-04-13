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
            recruit_id="1",
            category_id=1,
            title="2025년도 전문계약직(야간약사) 모집공고",
            institution="국민건강보험공단 일산병원",
            start_date="20250109",
            end_date="20250123",
            recrut_se="R2030", # 신입 + 경력
            hire_type_lst="R1040", # 비정규직
            ncs_cd_lst="R600006", # 보건.의료
            detail_url="https://nhimc.recruiter.co.kr/appsite/company/index",
            recrut_pblnt_sn=280272,
        ),
        Employee(
            recruit_id="2",
            category_id=2,
            title="한전MCS(주) 2025년 상반기 신규채용",
            institution="한전MCS(주)",
            start_date="20250109",
            end_date="20250123",
            recrut_se="R2010", # 신입
            hire_type_lst="R1010", # 정규직
            ncs_cd_lst="R600015, R600019", # 기계,전기.전자
            detail_url="https://recruit.incruit.com/kepcomcs",
            recrut_pblnt_sn=280269,
        ),
        Employee(
            recruit_id="3",
            category_id=1,
            title="한국보건사회연구원 행정인턴(장애인 제한경쟁) 채용 공고",
            institution="한국보건사회연구원",
            start_date="20250109",
            end_date="20250123",
            recrut_se="R2010", # 신입
            hire_type_lst="R1060", # 청년인턴(체험형)
            ncs_cd_lst="R600002", # 경영.회계.사무
            detail_url="https://kihasa.recruiter.co.kr/appsite/company/index",
            recrut_pblnt_sn=280268,
        ),
        Employee(
            recruit_id="4",
            category_id=3,
            title="채용형 인턴 채용공고(주택관리공단 충북지사)",
            institution="주택관리공단(주)",
            start_date="20250109",
            end_date="20250116",
            recrut_se="R2030", # 신입 + 경력
            hire_type_lst="R1070", # 청년인턴(채용형)
            ncs_cd_lst="R600014,R600015,R600019,R600020,R600023", # 건설,기계,전기.전자,정보통신,환경.에너지.안전
            detail_url="https://opendata.alio.go.kr/recruit4",
            recrut_pblnt_sn=280267,
        ),
        Employee(
            recruit_id="RECR20250405",
            category_id=2,
            title="한국형사·법무정책연구원 2025년도 제1차 채용공고[위촉조사연구원(육아휴직대체)]",
            institution="한국형사·법무정책연구원",
            start_date="20250109",
            end_date="20250124",
            recrut_se="R2030", # 신입 + 경력
            hire_type_lst="R1040", # 비정규직
            ncs_cd_lst="R600025", # 연구
            detail_url="https://opendata.alio.go.kr/recruit5",
            recrut_pblnt_sn=280266,
        )
    ]
    for emp in employees:
        db.add(emp)
