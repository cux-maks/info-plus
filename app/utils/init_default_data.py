"""기본 데이터를 삽입하는 유틸리티 모듈.
이 모듈은 Feature, Category, Employee 테이블에 기본 데이터를 삽입하는 함수들을 포함합니다.
"""

import datetime

from app.models.category import Category
from app.models.employee import Employee
from app.models.feature import Feature
from app.models.news import News


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
    """기본 Employee(채용 공고) 데이터를 추가합니다. Category가 선행되어 있어야 함."""
    employees = [
        Employee(
            recruit_id="1",
            category_id=1,
            title="2025년도 전문계약직(야간약사) 모집공고",
            institution="국민건강보험공단 일산병원",
            start_date=datetime.date(2025, 1, 9),
            end_date=datetime.date(2025, 1, 23),
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
            start_date=datetime.date(2025, 1, 9),
            end_date=datetime.date(2025, 1, 23),
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
            start_date=datetime.date(2025, 1, 9),
            end_date=datetime.date(2025, 1, 23),
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
            start_date=datetime.date(2025, 1, 9),
            end_date=datetime.date(2025, 1, 16),
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
            start_date=datetime.date(2025, 1, 9),
            end_date=datetime.date(2025, 1, 24),
            recrut_se="R2030", # 신입 + 경력
            hire_type_lst="R1040", # 비정규직
            ncs_cd_lst="R600025", # 연구
            detail_url="https://opendata.alio.go.kr/recruit5",
            recrut_pblnt_sn=280266,
        )
    ]
    for emp in employees:
        db.add(emp)


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
            url="https://n.news.naver.com/article/092/0002294509"
        ),
        News(
            category_id=2,  # 마케팅
            title="옥천군 '옥천읍 맛집·멋집' 책자 배부",
            contents="충북 옥천군은 골목 상권 홍보와 지역상권 활성화를 위한 책자 '옥천읍 맛집·멋집'을 2000부 제작해 배부한다. 군은 다양한 먹거리가 밀집한 옥천읍의 음식점과 카페 정보를 방문객에게 안내하기 위해 옥천사랑상품권(향수OK카드) 가맹점 등록자료를 기초로 지난 8월 책자 제작을 시작했다. 두 달여간 자료 수집과 보완 작업을 거쳐 '옥천읍 맛집‧멋집' 책자를 완성했다. 책자는 옥천읍 소재 음식점 410곳, 카페 114곳을 한식‧중식‧양식‧커피음료 전문점 등 업종별로 분류해 업소의 전경 사진과 주소, 연락처, 영업시간 등의 정보를 담았다. 관광객이 많이 찾는 육영수생가, 전통문화체험관, 정지용문학관, 장계관광지 등 옥천읍 주요 관광지에 배부됐다.",
            source="아이뉴스24",
            publish_date=datetime.datetime(2023, 10, 18, 11, 2),
            category="마케팅",
            url="https://n.news.naver.com/article/031/0000780000"
        ),
        News(
            category_id=3,  # 디자인
            title="'아이폰'으로 버틴 애플…팀 쿡 '생성형 AI 당장 없지만 투자 꽤 많다'",
            contents="애플은 2일(현지시간) 3분기 실적발표를 통해 당장 생성형AI를 도입하지 않았으나 꽤 많은 투자를 하고 있다고 확신하며 조만간 그에 따른 기술 실현을 목격할 수 있을 것이라 자신했다. 애플의 3분기 매출은 전년동기대비 1% 감소한 895억달러를 기록했다. 서비스 수익은 223억 달러로 전년동기대비 16% 증가하면서 사상 최고 매출을 기록했다. 앱스토어와 광고, 아이클라우드, 애플케어, 결제 서비스 및 영상 관련 서비스는 높은 매출을 기록했고 애플뮤직 역시 최대 기록을 바꿨다. 다만, 하드웨어 측면에서는 부진했다. 그나마 아이폰이 선방했다. 3분기 아이폰 매출은 438억달러로 전년동기대비 소폭 올랐다. 하지만 올해 아이폰 총 매출은 2006억달러로 전년 2055억 대비 소폭 줄었다. 이에 대해 팀 쿡 애플 CEO는 아이폰14 대비 아이폰15 모델 판매량이 더 높기는 하나 상급 기종인 아이폰15 프로 시리즈의 공급이 제한된 것이 이유라고 분석했다. 정상적인 공급을 위해 노력하고 있으며 연말께 수요와 공급이 균형을 이룰 것으로 내다봤다. 맥의 내리막은 가파르다. 맥 매출은 76억달러로 전년동기대비 34%나 줄었다. 애플은 최근 M3 기반 맥북 프로와 아이맥을 내놓으면서 반전을 꾀하고 있다. 팀 쿡 역시 다음 분기에 맥 매출이 개선될 것이라 예견했다. 맥과 마찬가지로 아이패드의 수익 역시 감소했다. 전년동기 71억달러보다 낮은 64억달러를 기록했다. 웨어러블 매출 역시도 전년동기 96억5000만달러에서 감소한 93억2000만달러를 나타냈다. 애플은 올해 연구개발에 총 300억달러를 지출했다. 비전 프로와 AI, 머신러닝, 자체 실리콘 투자에 따라 R&D 비용은 전년대비 더 증가했다.",
            source="디지털데일리",
            publish_date=datetime.datetime(2023, 11, 3, 10, 43),
            category="디자인",
            url="https://n.news.naver.com/article/138/0002160000"
        ),
        News(
            category_id=2,  # 마케팅
            title="인플루언서 마케팅 시장 2024년 15조원 돌파...AI 기반 타겟팅 강화",
            contents="인플루언서 마케팅 시장이 2024년 15조원을 돌파할 것으로 전망된다. 최근 기업들이 AI를 활용한 인플루언서 타겟팅에 적극적으로 나서고 있다. 특히 소셜미디어 플랫폼에서의 AI 기반 콘텐츠 최적화와 인플루언서 영향력 분석이 마케팅 효과를 크게 향상시키고 있다. 시장조사업체 인사이트에 따르면, 2023년 국내 인플루언서 마케팅 시장 규모는 약 12조원으로 추정되며, 이는 전년 대비 25% 증가한 수치다. 특히 AI를 활용한 인플루언서 타겟팅과 콘텐츠 최적화 기술이 시장 성장을 주도하고 있다. 기업들은 AI를 통해 인플루언서의 영향력과 타겟 오디언스를 정밀하게 분석하고, 이를 바탕으로 마케팅 효과를 극대화하고 있다.",
            source="머니투데이",
            publish_date=datetime.datetime(2024, 1, 15, 16, 30),
            category="마케팅",
            url="https://n.news.naver.com/article/008/0004920000"
        ),
        News(
            category_id=2,  # 마케팅
            title="신분증 제시 거부하며 경찰 밀친 40대, 항소심서 '무죄'로 뒤집혀",
            contents="폭행 신고를 받고 출동한 경찰이 신분증 제시를 요구하자 가슴을 밀치며 거부한 40대가 2심에서 무죄를 선고받았다. 2일 뉴시스에 따르면 울산지법 형사1-3부(부장판사 이봉수)는 공무집행방해 혐의로 기소된 A씨에 대한 항소심에서 벌금형을 선고한 원심을 깨고 무죄를 선고했다. 2021년 6월 울산 동구의 한 상가 인근에서 '아는 오빠한테 맞았다'는 B씨의 신고를 받고 출동한 경찰관 C씨가 신분증 제시를 요구하자, A씨는 이를 거부하며 욕설과 함께 가슴 부위를 때리고 밀치는 등 공무집행을 방해한 혐의로 재판에 넘겨졌다. 1심 재판부는 '경찰관이 다가서며 몰아붙이는 상황에서 이에 대응해 폭력을 가한 사실은 인정된다'면서도 '신분 확인을 요구하는 경찰에게 욕설하고 폭행한 행위는 정당하지 않다'며 벌금 500만원을 선고했다. A씨는 1심 판결에 불복해 항소했다. 그는 법정에서 '가슴을 폭행한 사실이 없고, B씨가 신고를 철회했는데도 경찰관 C씨가 계속해서 강압적으로 신분증 제시를 요구해 위법한 직무 집행에 대항해 실랑이를 벌였다'며 무죄를 주장했다. 2심 재판부는 A씨 주장을 받아들였다. 현장 폐쇄회로(CC)TV 상에 A씨가 경찰관 C씨의 가슴 부위를 때리는 모습이 확인되지 않고, B씨가 신고를 철회해 사건 처리가 완료된 만큼 계속된 신분증 제시 요구는 정당한 공무집행으로 볼 수 없다고 본 것이다.",
            source="머니투데이",
            publish_date=datetime.datetime(2023, 8, 2, 7, 40),
            category="마케팅",
            url="https://n.news.naver.com/article/008/0004920000"
        )
    ]
    for news in news_items:
        db.add(news)
