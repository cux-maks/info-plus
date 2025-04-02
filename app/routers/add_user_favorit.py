from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db_manager import db_manager
from app.models.user_category import UserCategory

router = APIRouter()
db_dependency = Depends(db_manager.get_db)  # 전역 변수로 설정

class SubscriptionRequest(BaseModel):
    user_id: str = Field(..., example="user123")
    category_id: int = Field(..., example=1)

@router.post("/adduserfavorit")
def add_category(request: SubscriptionRequest, db: Session = db_dependency):
    # 중복 체크
    existing_subscription = db.query(UserCategory).filter(
        UserCategory.user_id == request.user_id,
        UserCategory.category_id == request.category_id
    ).first()

    if existing_subscription:
        raise HTTPException(status_code=400, detail="Already subscribed to this category.")

    # 구독 정보 추가
    new_subscription = UserCategory(user_id=request.user_id, category_id=request.category_id)
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return {"message": "Subscription successful!"}
