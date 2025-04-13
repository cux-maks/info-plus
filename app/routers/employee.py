from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models import Users, UserCategory, Category, Employee
from app.utils.db_manager import db_manager

router = APIRouter(prefix="/recruit", tags=["Recruit"])

@router.get("/recommendation")
def get_recruit_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1),
    db: Session = Depends(db_manager.get_db)
):
    # ✅ 1. 사용자 존재 확인
    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ 2. 사용자 관심 카테고리 조회
    user_categories = (
        db.query(UserCategory.category_id)
        .filter(UserCategory.user_id == user_id, UserCategory.is_active == True)
        .all()
    )
    if not user_categories:
        raise HTTPException(status_code=404, detail="No active category subscriptions")

    category_ids = [uc.category_id for uc in user_categories]

    # ✅ 3. 해당 카테고리의 채용 공고 조회
    jobs = (
        db.query(Employee)
        .filter(Employee.category_id.in_(category_ids))
        .limit(limit)
        .all()
    )
    if not jobs:
        raise HTTPException(status_code=404, detail="No recruitment posts found for user's interests")

    return jobs
