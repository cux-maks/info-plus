import requests
import json
from datetime import datetime, timedelta

from app.models.employee import Employee
from app.utils.db_manager import db_manager

# ✅ NCS 코드 → 카테고리 ID 매핑 (카테고리 11~35에 해당)
NCS_CATEGORY_MAP = {
    f"R6000{str(i).zfill(2)}": 10 + i for i in range(1, 26)
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
        start_date (str): 조회 시작일 (yyyy-mm-dd 형식).
        end_date (str): 조회 종료일 (yyyy-mm-dd 형식).
        pbancBgngYmd (str): 공고 시작일 (yyyymmdd).
        pbancEndYmd (str): 공고 종료일 (yyyymmdd).
        hireTypeLst (str): 고용형태 코드 (예: R1000).
        workRgnLst (str): 근무지 코드 (예: R3000).
        ncsCdLst (str): NCS 직무 분류 코드 (예: R6000).
        acbgCondLst (str): 학력 조건 코드 (예: R7000).

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
            # ✅ 1. 복수의 NCS 코드(직무분류코드)와 채용형태코드가 콤마로 구분되어 들어올 수 있음
            ncs_codes = job.get("ncsCdLst", "")
            ncs_code_list = ncs_codes.split(",") if ncs_codes else []  # 예: "R600001,R600005" → ["R600001", "R600005"]

            hire_types = job.get("hireTypeLst", "")
            hire_type_list = hire_types.split(",") if hire_types else []  # 예: "R1010,R1030" → ["R1010", "R1030"]

            # ✅ 2. NCS 코드들을 기반으로 해당하는 카테고리 ID 추출 (미리 정의된 매핑 딕셔너리에서 가져옴)
            matched_category_ids = [
                NCS_CATEGORY_MAP.get(code) for code in ncs_code_list
                if NCS_CATEGORY_MAP.get(code)  # None이 아닌 것만 필터링
            ]

            # ✅ 3. 매칭되는 카테고리가 하나도 없으면 skip
            if not matched_category_ids:
                continue

            # ✅ 4. 매칭된 각 카테고리에 대해 같은 공고를 복수로 저장
            for category_id in matched_category_ids:
                recruit_id = f"{job['recrutPblntSn']}_{category_id}"  # 중복 방지를 위해 공고번호 + 카테고리ID로 복합키 구성

                new_job = Employee(
                    recruit_id=recruit_id,
                    category_id=category_id,  # 복수 저장을 위한 핵심 부분
                    title=job.get("recrutPbancTtl", ""),
                    institution=job.get("instNm", ""),
                    start_date=format_date(job.get("pbancBgngYmd")),
                    end_date=format_date(job.get("pbancEndYmd")),
                    recrut_se=job.get("recrutSe", ""),
                    hire_type_lst=hire_type_list,  # PostgreSQL의 ARRAY(String)으로 저장
                    ncs_cd_lst=ncs_code_list,      # PostgreSQL의 ARRAY(String)으로 저장
                    detail_url=f"https://opendata.alio.go.kr/recruit?sn={job['recrutPblntSn']}",
                    recrut_pblnt_sn=int(job["recrutPblntSn"]),
                )

                db_session.add(new_job)  # 실제 DB에 INSERT 요청
                inserted_count += 1

        except Exception as e:
            print(f"⚠️ 저장 실패: {e}")
            continue

    db_session.commit()
    print(f"✅ 총 {inserted_count}건의 채용 공고가 저장되었습니다.")
    return inserted_count
