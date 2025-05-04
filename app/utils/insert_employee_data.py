from datetime import datetime, timedelta

import requests

from app.models.employee import Employee
from app.models.employee_category import EmployeeCategory
from app.models.employee_hire_type import EmployeeHireType

# ✅ NCS 코드 → 카테고리 ID 매핑 (카테고리 11~35에 해당)
NCS_CATEGORY_MAP = {
    f"R6000{str(i).zfill(2)}": 10 + i for i in range(1, 26)
}

# HireType 코드 → hire_type_id 매핑 (미리 DB에 정의되어 있어야 함)
HIRE_TYPE_CODE_TO_ID = {
    "R1010": 1,  # 정규직
    "R1020": 2,  # 계약직
    "R1030": 3,  # 무기계약직
    "R1040": 4,  # 비정규직
    "R1050": 5,  # 청년인턴
    "R1060": 6,  # 청년인턴(체험형)
    "R1070": 7,  # 청년인턴(채용형)
}

API_URL = 'http://apis.data.go.kr/1051000/recruitment/list'
API_KEY = 'BMuu6msPlcAzIRXBs9HEspNVRQlWkHKREOuOu9rPIC/20G3LoydNLbWcQR+uI31y2CHvMgyi9YpDfxkqTWtdXg=='

def format_date(date_str):
    """yyyymmdd 형식을 yyyy-mm-dd로 변환합니다."""
    try:
        return datetime.strptime(date_str, "%Y%m%d").date()
    except (ValueError, TypeError):
        return None

def fetch_and_insert_recent_jobs(days=1, db_session=None):
    """
    최근 일정 기간 동안의 채용 공고를 공공기관 API에서 조회하고 DB에 저장합니다.
    NCS 코드에 따라 여러 카테고리에 매핑하여 Employee 데이터를 다중 저장합니다.

    Args:
        days (int): 조회할 과거 일 수 (기본값: 1일 // 하루마다 특정 시점에 자동으로 공고 저장).
        db_session (Session): SQLAlchemy 세션 객체.

    API Parameters Used:
        pbancBgngYmd (str): 공고 시작일 (yyyymmdd).
        pbancEndYmd (str): 공고 종료일 (yyyymmdd).
        hireTypeLst (str): 고용형태 코드 (예: R1000).
        workRgnLst (str): 근무지 코드 (예: R3000). // 현재 사용하지 않음
        ncsCdLst (str): NCS 직무 분류 코드 (예: R6000).
        acbgCondLst (str): 학력 조건 코드 (예: R7000). // 현재 사용하지 않음

    Returns:
        int: 저장된 채용 공고 수.

    Raises:
        requests.RequestException: API 요청 실패 시 발생.
        ValueError: 날짜 포맷 오류 등 데이터 처리 중 오류 발생 시 발생.
    """
    start_date = (datetime.today() - timedelta(days=days)).strftime('%Y-%m-%d')
    end_date = datetime.today().strftime('%Y-%m-%d')

    params = {
        'serviceKey': API_KEY,
        'pbancBgngYmd': start_date,
        '_type': 'json'
    }

    response = requests.get(API_URL, params=params)
    if response.status_code != 200:
        print(f"❗ API 요청 실패: {response.status_code}")
        return 0

    try:
        result_list = response.json().get('result', [])
    except Exception as e:
        print("❗ JSON 파싱 실패:", e)
        return 0

    inserted_count = 0

    for job in result_list:
        try:
            # NCS 코드 리스트 추출 (예: "R600001,R600002,...")
            ncs_codes = job.get("ncsCdLst", "")
            ncs_code_list = ncs_codes.split(",") if ncs_codes else []

            # 고용형태 코드 리스트 추출 (예: "R1010,R1020,...")
            hire_types = job.get("hireTypeLst", "")
            hire_type_list = hire_types.split(",") if hire_types else []

            # NCS 코드 기반으로 내부 category_id 매핑
            matched_category_ids = [
                NCS_CATEGORY_MAP.get(code) for code in ncs_code_list
                if NCS_CATEGORY_MAP.get(code)
            ]

            # 매핑된 category_id가 하나도 없으면 해당 공고는 저장하지 않음
            if not matched_category_ids:
                continue

            # 채용 공고 고유번호 (recruit_id) 추출 및 정수형 변환
            recruit_id = int(job["recrutPblntSn"])

            # employee 테이블에 채용 공고 기본 정보 저장
            new_employee = Employee(
                recruit_id=recruit_id,
                title=job.get("recrutPbancTtl", ""),            # 공고 제목
                institution=job.get("instNm", ""),               # 기관명
                start_date=format_date(job.get("pbancBgngYmd")), # 시작일
                end_date=format_date(job.get("pbancEndYmd")),    # 마감일
                recrut_se=job.get("recrutSe", ""),               # 공고 구분
                detail_url=f"https://opendata.alio.go.kr/recruit?sn={recruit_id}",  # 상세 URL
                recrut_pblnt_sn=recruit_id                       # 공고번호
            )
            db_session.add(new_employee)

            # employee_category 테이블에 연결 정보 저장 (NCS → category_id)
            for category_id in matched_category_ids:
                db_session.add(EmployeeCategory(
                    recruit_id=recruit_id,
                    category_id=category_id
                ))

            # employee_hire_type 테이블에 연결 정보 저장 (고용형태 → hire_type_id)
            for hire_code in hire_type_list:
                hire_type_id = HIRE_TYPE_CODE_TO_ID.get(hire_code)
                if hire_type_id:
                    db_session.add(EmployeeHireType(
                        recruit_id=recruit_id,
                        hire_type_id=hire_type_id
                    ))

            # 정상적으로 하나의 공고 저장 완료 시 카운트 증가
            inserted_count += 1

        except Exception as e:
            # 예외 발생 시 해당 공고 저장 건너뛰고 에러 메시지 출력
            print(f"⚠️ 저장 실패: {e}")
            continue

    # 전체 커밋 (성공적으로 추가된 공고들 반영)
    db_session.commit()
    print(f"✅ {start_date}부터 {end_date} 기간까지의 채용 공고 중 \n {inserted_count}건의 채용 공고가 저장되었습니다.")
    return inserted_count
