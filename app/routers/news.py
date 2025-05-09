"""뉴스 관련 API 라우터 모듈.

이 모듈은 사용자의 관심 카테고리에 기반하여 관련 뉴스를 추천하는 기능을 제공합니다.
사용자의 구독 정보를 바탕으로 관련된 뉴스를 필터링하여 반환합니다.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models import News, UserCategory, Users
from app.utils.db_manager import db_manager
from app.utils.news_client import fetch_naver_news

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
        db.query(UserCategory.category_id)
        .filter(UserCategory.user_id == user_id, UserCategory.is_active.is_(True))
        .all()
    )
    if not user_categories:  # 만약 활성화된 카테고리가 없다면
        logger.error(f"활성화된 카테고리가 없습니다. ({user_id})")
        raise HTTPException(status_code=404, detail="No active category subscriptions")

    logger.info(f"사용자 관심 카테고리 조회: {user_categories}")

    category_ids = [uc.category_id for uc in user_categories]

    # ✅ 3. 해당 카테고리의 뉴스 조회
    news = (
        db.query(News)
        .filter(News.category_id.in_(category_ids))
        .order_by(
            News.publish_date.desc()  # 최신 뉴스 우선
        )
        .limit(limit)
        .all()
    )
    if not news:
        logger.error(f"사용자 관심 카테고리에 해당하는 뉴스가 없습니다. ({user_id}, {category_ids})")
        raise HTTPException(status_code=404, detail="No news found for user's interests")

    logger.info(f"사용자 관심 카테고리에 해당하는 뉴스 조회: {news}")

    # ✅ 4. limit보다 적게 조회된 경우 메시지 추가
    message = None
    if len(news) < limit:
        message = (
            f"뉴스 데이터가 부족하여, 요청하신 뉴스 {limit}개 중 "
            f"{len(news)}개의 뉴스만 조회되었습니다."
        )

    return {
        "results": news,
        "message": message
    }

@router.post("/fetch-and-save/")
def fetch_and_save_news(
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "date",
    db: Session = db_dependency
):
    news_list = fetch_naver_news(query, display, start, sort)
    saved_count = 0

    for news in news_list:
        # 기존 DB에 news_id가 있는지 확인
        exists = db.query(News).filter(News.news_id == news.news_id).first()
        if not exists:
            db.add(news)
            saved_count += 1

    db.commit()
    return {"message": "뉴스 저장 완료", "count": saved_count}
