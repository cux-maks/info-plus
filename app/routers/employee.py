"""채용 관련 API 라우터 모듈.

이 모듈은 사용자의 관심 카테고리에 기반하여 관련 채용 공고를 추천하는 기능을 제공합니다.
사용자의 구독 정보를 바탕으로 관련된 채용 공고를 필터링하여 반환합니다.
"""


from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models import Employee, UserCategory, Users
from app.utils.db_manager import db_manager

router = APIRouter()
db_dependency = Depends(db_manager.get_db)  # 전역 변수로 설정


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
        .filter(Employee.category_id.in_(category_ids))
        .order_by(
            Employee.start_date.desc(),   # 최신 시작일 우선
            Employee.end_date.asc()       # 마감일이 빠를수록 우선
        )
        .limit(limit)
        .all()
    )
    if not jobs:
        raise HTTPException(status_code=404, detail="No recruitment posts found for user's interests")

    # ✅ 4. limit보다 적게 조회된 경우 메시지 추가
    message = None
    if len(jobs) < limit:
        message = f"요청한 limit {limit}개 중 {len(jobs)}개의 채용공고만 조회되었습니다."

    return {
        "results": jobs,
        "message": message
    }
