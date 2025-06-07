# ruff: noqa
"""기본 데이터를 삽입하는 유틸리티 모듈.
이 모듈은 Feature, Category, Employee 테이블에 기본 데이터를 삽입하는 함수들을 포함합니다.
"""

import datetime

from app.models.category import Category
from app.models.employee import Employee
from app.models.feature import Feature
from app.models.news import News
from app.models.users import Users
from app.models.hire_type import HireType
from app.models.employee_category import EmployeeCategory
from app.models.employee_hire_type import EmployeeHireType



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
        # 뉴스 관련 카테고리
        Category(category_name="IT/과학", feature=feature_news),
        Category(category_name="마케팅", feature=feature_news),
        Category(category_name="디자인", feature=feature_news),
        Category(category_name="경영/기획", feature=feature_news),
        Category(category_name="영업/제휴", feature=feature_news),
        Category(category_name="정치", feature=feature_news),
        Category(category_name="경제", feature=feature_news),
        Category(category_name="사회", feature=feature_news),
        Category(category_name="생활/문화", feature=feature_news),
        Category(category_name="세계", feature=feature_news),

        # 채용 관련 카테고리
        Category(category_name="사업관리", feature=feature_employee),
        Category(category_name="경영·회계·사무", feature=feature_employee),
        Category(category_name="금융·보험", feature=feature_employee),
        Category(category_name="교육·자연·사회과학", feature=feature_employee),
        Category(category_name="법률·경찰·소방·교도·국방", feature=feature_employee),
        Category(category_name="보건·의료", feature=feature_employee),
        Category(category_name="사회복지·종교", feature=feature_employee),
        Category(category_name="문화·예술·디자인·방송", feature=feature_employee),
        Category(category_name="운전·운송", feature=feature_employee),
        Category(category_name="영업판매", feature=feature_employee),
        Category(category_name="경비·청소", feature=feature_employee),
        Category(category_name="이용·숙박·여행·오락·스포츠", feature=feature_employee),
        Category(category_name="음식서비스", feature=feature_employee),
        Category(category_name="건설", feature=feature_employee),
        Category(category_name="기계", feature=feature_employee),
        Category(category_name="재료", feature=feature_employee),
        Category(category_name="화학", feature=feature_employee),
        Category(category_name="섬유·의복", feature=feature_employee),
        Category(category_name="전기·전자", feature=feature_employee),
        Category(category_name="정보통신", feature=feature_employee),
        Category(category_name="식품가공", feature=feature_employee),
        Category(category_name="인쇄·목재·가구·공예", feature=feature_employee),
        Category(category_name="환경·에너지·안전", feature=feature_employee),
        Category(category_name="농림어업", feature=feature_employee),
        Category(category_name="연구", feature=feature_employee),

        
        Category(category_id = 0, category_name="연구", feature=feature_employee),
    ]

    for category in categories:
        db.add(category)

def add_default_hire_type(db):
    """기본 HireType 데이터를 추가합니다."""

    hire_types = [
        HireType(
            hire_type_id=1,
            hire_type_name="정규직",
            hire_type_code="R1010"
        ),
        HireType(
            hire_type_id=2,
            hire_type_name="계약직",
            hire_type_code="R1020"
        ),
        HireType(
            hire_type_id=3,
            hire_type_name="무기계약직",
            hire_type_code="R1030"
        ),
        HireType(
            hire_type_id=4,
            hire_type_name="비정규직",
            hire_type_code="R1040"
        ),
        HireType(
            hire_type_id=5,
            hire_type_name="청년인턴",
            hire_type_code="R1050"
        ),
        HireType(
            hire_type_id=6,
            hire_type_name="청년인턴(체험형)",
            hire_type_code="R1060"
        ),
        HireType(
            hire_type_id=7,
            hire_type_name="청년인턴(채용형)",
            hire_type_code="R1070"
        ),
    ]

    for hire_type in hire_types:
        db.add(hire_type)

def add_default_employees(db):
    """기본 Employee(채용 공고) 데이터를 추가합니다. Category가 선행되어 있어야 함."""
    employees = [
        Employee(
            recruit_id=1,
            title="2025년도 전문계약직(야간약사) 모집공고",
            institution="국민건강보험공단 일산병원",
            start_date=datetime.date(2025, 1, 9),
            end_date=datetime.date(2025, 1, 23),
            recrut_se="R2030", # 신입 + 경력
            detail_url="https://nhimc.recruiter.co.kr/appsite/company/index",
            recrut_pblnt_sn=280272,
        ),
        Employee(
            recruit_id=2,
            title="한전MCS(주) 2025년 상반기 신규채용",
            institution="한전MCS(주)",
            start_date=datetime.date(2025, 1, 9),
            end_date=datetime.date(2025, 1, 23),
            recrut_se="R2010", # 신입
            detail_url="https://recruit.incruit.com/kepcomcs",
            recrut_pblnt_sn=280269,
        ),
        Employee(
            recruit_id=3,
            title="한국보건사회연구원 행정인턴(장애인 제한경쟁) 채용 공고",
            institution="한국보건사회연구원",
            start_date=datetime.date(2025, 1, 9),
            end_date=datetime.date(2025, 1, 23),
            recrut_se="R2010", # 신입
            detail_url="https://kihasa.recruiter.co.kr/appsite/company/index",
            recrut_pblnt_sn=280268,
        ),
        Employee(
            recruit_id=4,
            title="채용형 인턴 채용공고(주택관리공단 충북지사)",
            institution="주택관리공단(주)",
            start_date=datetime.date(2025, 1, 9),
            end_date=datetime.date(2025, 1, 16),
            recrut_se="R2030", # 신입 + 경력
            detail_url="https://opendata.alio.go.kr/recruit4",
            recrut_pblnt_sn=280267,
        ),
        Employee(
            recruit_id=5,
            title="한국형사·법무정책연구원 2025년도 제1차 채용공고[위촉조사연구원(육아휴직대체)]",
            institution="한국형사·법무정책연구원",
            start_date=datetime.date(2025, 1, 9),
            end_date=datetime.date(2025, 1, 24),
            recrut_se="R2030", # 신입 + 경력
            detail_url="https://opendata.alio.go.kr/recruit5",
            recrut_pblnt_sn=280266,
        )
    ]
    for emp in employees:
        db.add(emp)

def add_default_employee_hire_type(db):
    """기본 EmployeeHireType 데이터를 추가합니다. Employee가 선행되어 있어야 함."""

    employee_hire_types = [
        EmployeeHireType(
            recruit_id=1,
            hire_type_id=4 # 비정규직
        ),
        EmployeeHireType(
            recruit_id=2,
            hire_type_id=1 # 정규직
        ),
        EmployeeHireType(
            recruit_id=3,
            hire_type_id=6 # 청년인턴(체험형)
        ),
        EmployeeHireType(
            recruit_id=4,
            hire_type_id=7 # 청년인턴(채용형)
        ),
        EmployeeHireType(
            recruit_id=5,
            hire_type_id=4 # 비정규직
        )
    ]

    for emp_hire in employee_hire_types:
        db.add(emp_hire)

def add_default_employee_category(db):
    """기본 EmployeeCategory 데이터를 추가합니다. Employee가 선행되어 있어야 함."""

    employee_categories = [
        EmployeeCategory(
            recruit_id=1,
            category_id=16 # 보건.의료
        ),
        EmployeeCategory(
            recruit_id=2,
            category_id=25  # 기계
        ),
        EmployeeCategory(
            recruit_id=2,
            category_id=29  # 전기.전자
        ),
        EmployeeCategory(
            recruit_id=3,
            category_id=12 # 경영.회계.사무
        ),
        EmployeeCategory(
            recruit_id=4,
            category_id=24 # 건설
        ),
        EmployeeCategory(
            recruit_id=4,
            category_id=25 # 기계
        ),
        EmployeeCategory(
            recruit_id=4,
            category_id=29 # 전기.전자
        ),
        EmployeeCategory(
            recruit_id=4,
            category_id=30 # 정보통신
        ),
        EmployeeCategory(
            recruit_id=4,
            category_id=33 # 환경.에너지.안전
        ),
        EmployeeCategory(
            recruit_id=5,
            category_id=35 # 연구
        ),
    ]

    for emp_cat in employee_categories:
        db.add(emp_cat)


def add_default_news(db):
    """기본 News 데이터를 추가합니다. Category가 선행되어 있어야 함."""
    news_items = [
        News(
            category_id=1,  # IT/개발
            title="로보락, 로봇청소기 'S7 맥스 울트라' 출시…154만원",
            contents="청소가전 전문기업 로보락은 신제품 올인원 로봇청소기 '로보락 S7 맥스 울트라'를 출시한다고 7일 밝혔다. 로보락 S7 맥스 울트라는 지난해 출시한 '로보락 S7 맥스V 울트라'보다 흡입력을 높였다. 제품은 5천500Pa 흡입력과 분당 최대 3천 번 진동하는 음파진동 물걸레 시스템을 갖췄다. 신제품은 라이다 내비게이션을 탑재해 집을 빠르게 스캔하고 '리액티브 테크' 장애물 회피 시스템으로 사물 충돌을 방지한다. 절벽 감지 센서로 위험 지역을 파악하고 AI가 로봇청소기가 갇히기 쉬운 장소를 자동으로 탐지해 진입 금지 구역을 제안한다. 제품은 본체 유지관리 기기인 엠티 워시 필 도크 내 듀얼 열풍건조 기능을 추가했다. 패드 세척이 진행되는 바닥 면도 자동 건조한다. 도크는 세척 브러시가 좌우 양방향으로 움직이며 물걸레 패드와 바닥 면을 자동 세척해준다. 제품은 로봇청소기 자동 물 채움 기능을 지원해 최대 300m2 면적을 물걸레질할 수 있다. 또한 자동 먼지비움 기능으로 최대 7주까지 먼지통을 비우지 않아도 된다. 신제품은 화이트 컬러로 출시했다. 가격은 154만원이다. 기존 'S7 맥스V 울트라'보다 5만원 저렴해졌다.",
            source="ZD넷코리아",
            publish_date=datetime.datetime(2023, 6, 7, 9, 51),
            category="IT/개발",
            url="https://n.news.naver.com/article/092/0002294509",
            original_url="https://n.news.naver.com/article/138/0002160000",
        ),
        News(
            category_id=2,  # 마케팅
            title="옥천군 '옥천읍 맛집·멋집' 책자 배부",
            contents="충북 옥천군은 골목 상권 홍보와 지역상권 활성화를 위한 책자 '옥천읍 맛집·멋집'을 2000부 제작해 배부한다. 군은 다양한 먹거리가 밀집한 옥천읍의 음식점과 카페 정보를 방문객에게 안내하기 위해 옥천사랑상품권(향수OK카드) 가맹점 등록자료를 기초로 지난 8월 책자 제작을 시작했다. 두 달여간 자료 수집과 보완 작업을 거쳐 '옥천읍 맛집‧멋집' 책자를 완성했다. 책자는 옥천읍 소재 음식점 410곳, 카페 114곳을 한식‧중식‧양식‧커피음료 전문점 등 업종별로 분류해 업소의 전경 사진과 주소, 연락처, 영업시간 등의 정보를 담았다. 관광객이 많이 찾는 육영수생가, 전통문화체험관, 정지용문학관, 장계관광지 등 옥천읍 주요 관광지에 배부됐다.",
            source="아이뉴스24",
            publish_date=datetime.datetime(2023, 10, 18, 11, 2),
            category="마케팅",
            url="https://n.news.naver.com/article/031/0000780000",
            original_url="https://n.news.naver.com/article/138/0002160000",
        ),
        News(
            category_id=3,  # 디자인
            title="'아이폰'으로 버틴 애플…팀 쿡 '생성형 AI 당장 없지만 투자 꽤 많다'",
            contents="애플은 2일(현지시간) 3분기 실적발표를 통해 당장 생성형AI를 도입하지 않았으나 꽤 많은 투자를 하고 있다고 확신하며 조만간 그에 따른 기술 실현을 목격할 수 있을 것이라 자신했다. 애플의 3분기 매출은 전년동기대비 1% 감소한 895억달러를 기록했다. 서비스 수익은 223억 달러로 전년동기대비 16% 증가하면서 사상 최고 매출을 기록했다. 앱스토어와 광고, 아이클라우드, 애플케어, 결제 서비스 및 영상 관련 서비스는 높은 매출을 기록했고 애플뮤직 역시 최대 기록을 바꿨다. 다만, 하드웨어 측면에서는 부진했다. 그나마 아이폰이 선방했다. 3분기 아이폰 매출은 438억달러로 전년동기대비 소폭 올랐다. 하지만 올해 아이폰 총 매출은 2006억달러로 전년 2055억 대비 소폭 줄었다. 이에 대해 팀 쿡 애플 CEO는 아이폰14 대비 아이폰15 모델 판매량이 더 높기는 하나 상급 기종인 아이폰15 프로 시리즈의 공급이 제한된 것이 이유라고 분석했다. 정상적인 공급을 위해 노력하고 있으며 연말께 수요와 공급이 균형을 이룰 것으로 내다봤다. 맥의 내리막은 가파르다. 맥 매출은 76억달러로 전년동기대비 34%나 줄었다. 애플은 최근 M3 기반 맥북 프로와 아이맥을 내놓으면서 반전을 꾀하고 있다. 팀 쿡 역시 다음 분기에 맥 매출이 개선될 것이라 예견했다. 맥과 마찬가지로 아이패드의 수익 역시 감소했다. 전년동기 71억달러보다 낮은 64억달러를 기록했다. 웨어러블 매출 역시도 전년동기 96억5000만달러에서 감소한 93억2000만달러를 나타냈다. 애플은 올해 연구개발에 총 300억달러를 지출했다. 비전 프로와 AI, 머신러닝, 자체 실리콘 투자에 따라 R&D 비용은 전년대비 더 증가했다.",
            source="디지털데일리",
            publish_date=datetime.datetime(2023, 11, 3, 10, 43),
            category="디자인",
            url="https://n.news.naver.com/article/138/0002160000",
            original_url="https://n.news.naver.com/article/138/0002160000",
        ),
    ]
    for news in news_items:
        db.add(news)


def add_default_user(db):
    """기본 사용자 데이터를 추가합니다."""
    admin_user = Users(
        user_id="admin",
        user_name="admin",
        created_at=datetime.datetime.now()
    )
    db.add(admin_user)
