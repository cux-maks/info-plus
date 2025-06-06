"""사용자 관련 API 라우터 모듈.

이 모듈은 사용자의 카테고리 구독 관리와 관련된 API 엔드포인트를 제공합니다.
사용자가 카테고리를 구독하거나 구독을 해제하는 기능과 특정 기능에 따른 카테고리 목록을 조회하는 기능을 포함합니다.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.user_category import UserCategory
from app.utils.db_manager import db_manager
from app.utils.verifier import verify_exists_user

router = APIRouter()
db_dependency = Depends(db_manager.get_db)  # 전역 변수로 설정

class SubscriptionRequest(BaseModel):
    """카테고리 구독 요청을 위한 데이터 모델.
    Attributes:
        user_id (str): 구독을 요청하는 사용자의 ID.
        category_id (int): 구독하려는 카테고리의 ID.
    """
    user_id: str = Field(..., example="user123")
    category_id: int = Field(..., example=1)

@router.post("/subscribe")
def add_category(request: SubscriptionRequest, db: Session = db_dependency):
    """사용자가 특정 카테고리를 구독하는 엔드포인트입니다.

    Args:
        request (SubscriptionRequest): 구독 요청 정보를 담은 객체.
        db (Session): 데이터베이스 세션.

    Returns:
        dict: 구독 성공 메시지를 포함한 JSON 응답.

    Raises:
        HTTPException 400: 이미 해당 카테고리를 구독 중인 경우.
    """
    verify_exists_user(request.user_id, db)

    category = db.query(Category).filter_by(category_id=request.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category {request.category_id} not found.")

    # 중복 체크
    existing_subscription = db.query(UserCategory).filter(
        UserCategory.user_id == request.user_id,
        UserCategory.category_id == request.category_id
    ).first()

    if existing_subscription:
        raise HTTPException(status_code=400, detail=f"Category {request.category_id} is already subscribed.")

    # 구독 정보 추가
    new_subscription = UserCategory(user_id=request.user_id, category_id=request.category_id)
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return {"message": "Subscription successful!"}

@router.delete("/subscribe")
def delete_category(
    user_id: str = Query(..., description="User ID"),
    category_id: int = Query(..., description="Category ID"),
    db: Session = db_dependency
):
    """
    사용자의 특정 카테고리 구독을 해제하는 엔드포인트입니다.

    Args:
        user_id (str): 구독을 해제할 사용자의 ID.
        category_id (int): 사용자가 구독 해제할 카테고리의 ID.
        db (Session): 데이터베이스 세션.

    Returns:
        dict: 구독 해제 성공 메시지를 포함한 JSON 응답.

    Raises:
        HTTPException 404: 사용자가 존재하지 않는 경우.
        HTTPException 404: 카테고리가 존재하지 않는 경우.
        HTTPException 404: 해당 사용자의 구독 정보가 없는 경우.
        HTTPException 400: 이미 구독이 비활성화된 경우.
    """

    # 1️⃣ 사용자가 실제 존재하는지 확인
    verify_exists_user(user_id, db)

    category = db.query(Category).filter_by(category_id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category ID {category_id} not found.")

    # 2️⃣ 요청한 카테고리가 실제 존재하는지 확인
    category_exists = db.query(Category).filter(Category.category_id == category_id).first()
    if not category_exists:
        raise HTTPException(status_code=404, detail="Category not found.")

    # 3️⃣ 기존 구독이 있는지 확인
    existing_subscription = db.query(UserCategory).filter(
        UserCategory.user_id == user_id,
        UserCategory.category_id == category_id
    ).first()

    if not existing_subscription:
        raise HTTPException(status_code=404, detail=f"Category ID {category_id} is not subscribed.")

    if not existing_subscription.is_active:
        raise HTTPException(status_code=400, detail=f"Category ID {category_id} is already unsubscribed.")

    # 4️⃣ is_active 값을 False로 변경 (Soft Delete)
    existing_subscription.is_active = False
    db.commit()
    db.refresh(existing_subscription)

    return {"message": "Subscription successfully deactivated."}

class GetCategoryRequest(BaseModel):
    user_id: str = Field(..., example="user123")

class CategoryResponse(BaseModel):
    feature_name: str
    category_name: str

    class Config:
        orm_mode = True

@router.get("/{user_id}", response_model=List[CategoryResponse])
def get_user_categories(
    user_id: str = Path(...),
    db: Session = db_dependency
):
    """
    사용자의 구독 중인 카테고리 목록을 조회하는 API입니다.

    Args:
        user_id (str): 사용자 ID
        db (Session): DB 세션

    Returns:
        List[CategoryResponse]: 구독 중인 카테고리 목록
    """
    # 사용자 존재 여부 확인
    verify_exists_user(user_id, db)

    # 해당 사용자의 활성화된 구독 목록 조회
    subscriptions = (
        db.query(UserCategory)
        .filter(UserCategory.user_id == user_id, UserCategory.is_active)
        .all()
    )

    # UserCategory 인스턴스의 category 필드를 통해 카테고리 정보 접근
    return [
        CategoryResponse(
            feature_name=sub.category.feature.feature_type,
            category_name=sub.category.category_name
        )
        for sub in subscriptions if sub.category is not None and sub.category.feature is not None
    ]
