"""기능 관련 API 라우터 모듈.

이 모듈은 기능 관리와 관련된 API 엔드포인트를 제공합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.feature import Feature
from app.utils.db_manager import db_manager

router = APIRouter()
db_dependency = Depends(db_manager.get_db)  # 전역 변수로 설정

@router.get("/{feature_id}")
def get_categories_by_feature(
    feature_id: str = Path(...),
    db: Session = db_dependency
):
    """특정 기능에 해당하는 카테고리 목록을 조회하는 엔드포인트입니다.

    Args:
        feature_id (str): 카테고리를 조회할 기능 유형.
        db (Session): 데이터베이스 세션.

    Returns:
        dict: 카테고리 목록을 포함한 메시지가 담긴 JSON 응답.

    Raises:
        HTTPException 404: 요청한 기능이 존재하지 않는 경우.
    """
    existing_feature = db.query(Feature).filter(Feature.feature_type == feature_id).first()
    if not existing_feature:
        raise HTTPException(status_code=404, detail=f"Feature not found. ({feature_id})")

    categories = db.query(Category).filter(Category.feature_id == existing_feature.feature_id).all()

    message = f"**{feature_id}**에서 사용 가능한 카테고리 목록\n\n"
    if categories:
        message += ', '.join([category.category_name for category in categories])
    else:
        message += "아직 지원하는 카테고리가 없어요. 🥲"

    return {"message": message}
