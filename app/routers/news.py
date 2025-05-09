"""뉴스 관련 API 라우터 모듈.

이 모듈은 사용자의 관심 카테고리에 기반하여 관련 뉴스를 추천하는 기능을 제공합니다.
사용자의 구독 정보를 바탕으로 관련된 뉴스를 필터링하여 반환합니다.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models import News, UserCategory, Users, Category
from app.utils.db_manager import db_manager
from app.utils.news_client import get_news_list_from_naver

logger = logging.getLogger(__name__)

router = APIRouter()
db_dependency = Depends(db_manager.get_db)  # 전역 변수로 설정


@router.get("/recommend")
def get_news_recommendations(
    user_id: str = Query(..., description="추천을 받을 사용자 ID"),
    limit: int = Query(10, ge=1, le=100, description="추천 받을 뉴스 수 (최대 100개, 기본값: 10)"),
    db: Session = db_dependency
):
    """
    사용자의 관심 카테고리에 기반한 뉴스를 추천합니다.

    Args:
        user_id (str): 뉴스를 추천받을 사용자 ID.
        limit (int): 추천할 뉴스 수.
        db (Session): 데이터베이스 세션 객체.

    Returns:
        List[News]: 사용자의 관심 카테고리에 해당하는 뉴스 목록.

    Raises:
        HTTPException 404: 사용자가 존재하지 않을 경우.
        HTTPException 404: 사용자의 관심 카테고리가 없을 경우.
        HTTPException 404: 추천 가능한 뉴스가 없을 경우.
    """
    # ✅ 1. 사용자 존재 확인
    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        logger.error(f"사용자가 존재하지 않습니다. ({user_id})")
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"사용자 존재 확인: {user}")

    # ✅ 2. 사용자 관심 카테고리 조회 (활성화된 것만)
    user_categories = (
        db.query(Category)
        .join(UserCategory, Category.category_id == UserCategory.category_id)
        .filter(UserCategory.user_id == user_id, UserCategory.is_active.is_(True))
        .all()
    )
    category_ids = [uc.category_id for uc in user_categories]
    category_names = [uc.category_name for uc in user_categories]

    if not user_categories:  # 만약 활성화된 카테고리가 없다면
        logger.error(f"활성화된 카테고리가 없습니다. ({user_id})")
        raise HTTPException(status_code=404, detail="No active category subscriptions")

    logger.info(f"사용자 관심 카테고리 조회: {category_names}")

    for category in user_categories:
        get_subscribed_news_list(category, limit, db)

    # ✅ 3. 해당 카테고리의 뉴스 조회
    results = []
    for category in user_categories:
        news_list = (
            db.query(News)
            .filter(News.category_id == category.category_id)
            .order_by(News.publish_date.desc())
            .limit(limit)
            .all()
        )
        message = None
        if len(news_list) < limit:
            message = f"{category.category_name} 카테고리의 뉴스가 부족하여 {len(news_list)}개만 조회되었습니다."

        results.append({
            "category": category.category_name,
            "message": message,
            "news_list": news_list
        })

    if not any(group["news_list"] for group in results):
        logger.error(f"사용자 관심 카테고리에 해당하는 뉴스가 없습니다. ({user_id})")
        raise HTTPException(status_code=404, detail="No news found for user's interests")

    return {
        "results": results
    }

def get_subscribed_news_list(
    category: Category,
    limit: int = 10,
    db: Session = db_dependency
):
    news_list = get_news_list_from_naver(category, limit)
    saved_count = 0

    for news in news_list:
        exists = db.query(News).filter(News.news_id == news.news_id).first()
        if not exists:
            db.add(news)
            saved_count += 1

    db.commit()
    logger.info(f"{saved_count}개의 뉴스 저장 완료")
