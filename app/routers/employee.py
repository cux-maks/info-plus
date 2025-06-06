"""채용 관련 API 라우터 모듈.

이 모듈은 사용자의 관심 카테고리에 기반하여 관련 채용 공고를 추천하는 기능을 제공합니다.
사용자의 구독 정보를 바탕으로 관련된 채용 공고를 필터링하여 반환합니다.
"""

from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models import Employee, EmployeeCategory, UserCategory, Users
from app.utils.db_manager import db_manager

router = APIRouter()
db_dependency = Depends(db_manager.get_db)  # 전역 변수로 설정
es = Elasticsearch("http://elasticsearch:9200")

@router.get("/recommend")
def get_recruit_recommendations(
    user_id: str = Query(..., description="추천을 받을 사용자 ID"),
    limit: int = Query(10, ge=1, le=100, description="추천 받을 채용 공고 수 (최대 100개, 기본값: 10)"),
    db: Session = db_dependency
):
    """
    사용자의 관심 카테고리에 기반한 채용 공고를 추천합니다.

    Args:
        user_id (str): 채용 공고를 추천받을 사용자 ID.
        limit (int): 추천할 채용 공고 수.
        db (Session): 데이터베이스 세션 객체.

    Returns:
        List[Employee]: 사용자의 관심 카테고리에 해당하는 채용 공고 목록.

    Raises:
        HTTPException 404: 사용자가 존재하지 않을 경우.
        HTTPException 404: 사용자의 관심 카테고리가 없을 경우.
        HTTPException 404: 추천 가능한 채용 공고가 없을 경우.
    """
    # ✅ 1. 사용자 존재 확인
    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ 2. 사용자 관심 카테고리 조회 (활성화된 것만)
    user_categories = (
        db.query(UserCategory.category_id)
        .filter(UserCategory.user_id == user_id, UserCategory.is_active.is_(True))
        .all()
    )
    if not user_categories: # 만약 활성화된 카테고리가 없다면
        raise HTTPException(status_code=404, detail="No active category subscriptions")

    category_ids = [uc.category_id for uc in user_categories]

    # ✅ 3. 해당 카테고리의 채용 공고 조회
    jobs = (
        db.query(Employee)
        .join(EmployeeCategory, Employee.recruit_id == EmployeeCategory.recruit_id)
        .filter(EmployeeCategory.category_id.in_(category_ids))
        .order_by(
            Employee.start_date.desc(),
            Employee.end_date.asc()
        )
        .limit(limit)
        .all()
    )
    if not jobs:
        raise HTTPException(status_code=404, detail="No recruitment posts found for user's interests")

    # ✅ 4. limit보다 적게 조회된 경우 메시지 추가
    message = None
    if len(jobs) < limit:
      message = (
          f"채용공고 데이터가 부족하여, 요청하신 채용공고 {limit}개 중 "
          f"{len(jobs)}개의 채용공고만 조회되었습니다."
      )

    return {
        "results": jobs,
        "message": message
    }

@router.get("/DB_search")
def search_employees(
    user_id: str = Query(..., description="사용자 ID"),
    keyword: str = Query(..., description="검색할 카테고리 키워드 (예: '정보통신', '디자인')"),
    limit: int = Query(10, ge=1, le=100, description="검색 결과 최대 개수 (기본값: 10, 최대: 100)"),
    db: Session = db_dependency
):
    """
    사용자가 입력한 키워드를 기반으로 가장 유사한 카테고리를 찾고, 해당 카테고리에 속한 채용 공고를 반환합니다.

    Args:
        user_id (str): 검색을 수행할 사용자 ID.
        keyword (str): 검색 키워드 (카테고리명).
        limit (int): 반환할 채용 공고 수 (기본값: 10, 최대 100).
        db (Session): 데이터베이스 세션 객체.

    Returns:
        dict: 매칭된 카테고리명과 해당 카테고리에 속한 채용 공고 목록.
            - matched_category (str): 검색 키워드와 가장 유사한 카테고리명.
            - results (List[dict]): 채용공고 목록 (제목, 기관, 시작일, 종료일, 상세 URL 포함).

    Raises:
        HTTPException 404: 사용자가 존재하지 않는 경우.
        HTTPException 500: Elasticsearch 연결 실패 또는 기타 오류 발생 시.
    """

    # ✅ 1. 사용자 존재 여부 확인
    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # ✅ 2-1. match_phrase_prefix로 후보군 검색 (자동완성 역할)
        prefix_result = es.search(
            index="categories",
            body={
                "size": 10,
                "query": {
                    "bool": {
                        "must": {
                            "match_phrase_prefix": {
                                "category_name": {
                                    "query": keyword
                                }
                            }
                        },
                        "filter": {
                            "term": {
                                "feature": "employee"
                            }
                        }
                    }
                }
            }
        )
        prefix_hits = prefix_result.get("hits", {}).get("hits", [])
        if not prefix_hits:
            # 후보군 없으면 바로 기타 처리
            matched_category = "기타"
            category_id = 0
        else:
            candidate_names = [hit["_source"]["category_name"] for hit in prefix_hits]

            # ✅ 2-2. BM25 기반 match 쿼리로 후보군 중 가장 유사한 카테고리 검색
            bm25_result = es.search(
                index="categories",
                body={
                    "size": 1,
                    "query": {
                        "bool": {
                            "must": {
                                "match": {
                                    "category_name": {
                                        "query": keyword,
                                        "operator": "and"
                                    }
                                }
                            },
                            "filter": {
                                "terms": {
                                    "category_name.keyword": candidate_names  # 후보군 필터링
                                }
                            }
                        }
                    }
                }
            )
            bm25_hits = bm25_result.get("hits", {}).get("hits", [])
            if bm25_hits:
                matched_source = bm25_hits[0]["_source"]
                matched_category = matched_source["category_name"]
                category_id = matched_source["category_id"]
            else:
                # BM25가 후보군 중 적합한 것을 못 찾으면 prefix 후보 중 1순위 반환
                matched_category = prefix_hits[0]["_source"]["category_name"]
                category_id = prefix_hits[0]["_source"]["category_id"]

    except ConnectionError as e:
        raise HTTPException(status_code=500, detail="Elasticsearch 연결 실패") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    # ✅ 3. 해당 카테고리에 속한 채용 공고 최신순 조회
    jobs = (
        db.query(Employee)
        .join(EmployeeCategory, Employee.recruit_id == EmployeeCategory.recruit_id)
        .filter(EmployeeCategory.category_id == category_id)
        .order_by(Employee.start_date.desc())
        .limit(limit)
        .all()
    )

    # ✅ 4. 결과를 JSON 형태로 정리
    results = [
        {
            "title": job.title,
            "institution": job.institution,
            "start_date": job.start_date.isoformat(),  # date → 문자열 (ISO 포맷)
            "end_date": job.end_date.isoformat(),
            "url": job.detail_url
        }
        for job in jobs
    ]

    # ✅ 5. 최종 응답 반환
    return {
        "matched_category": matched_category,
        "results": results
    }
