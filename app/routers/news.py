"""뉴스 관련 API 라우터 모듈.

이 모듈은 사용자의 관심 카테고리에 기반하여 관련 뉴스를 추천하는 기능을 제공합니다.
사용자의 구독 정보를 바탕으로 관련된 뉴스를 필터링하여 반환합니다.
"""

import logging

from elasticsearch import Elasticsearch
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models import Category, News, UserCategory, Users
from app.utils.db_manager import db_manager

logger = logging.getLogger(__name__)

router = APIRouter()
db_dependency = Depends(db_manager.get_db)  # 전역 변수로 설정
es = Elasticsearch("http://elasticsearch:9200")


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

    category_names = [uc.category_name for uc in user_categories]

    if not user_categories:  # 만약 활성화된 카테고리가 없다면
        logger.error(f"활성화된 카테고리가 없습니다. ({user_id})")
        raise HTTPException(status_code=404, detail="No active category subscriptions")

    logger.info(f"사용자 관심 카테고리 조회: {category_names}")

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

@router.get("/DB_search")
def search_news_by_keyword(
    user_id: str = Query(..., description="사용자 ID"),
    keyword: str = Query(..., description="검색할 카테고리 키워드 (예: '보건', '환경')"),
    limit: int = Query(10, ge=1, le=100, description="검색 결과 최대 개수 (기본값: 10, 최대: 100)"),
    db: Session = db_dependency
):
    """
    사용자가 입력한 키워드를 기반으로 가장 유사한 뉴스 카테고리를 찾고, 해당 카테고리에 속한 뉴스 기사를 반환합니다.

    Args:
        user_id (str): 검색을 수행할 사용자 ID.
        keyword (str): 검색 키워드 (카테고리명).
        limit (int): 반환할 채용 공고 수 (기본값: 10, 최대 100).
        db (Session): 데이터베이스 세션 객체.

    Returns:
        dict: {
            "matched_category": str,
            "results": List[dict]
        }
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
                                "category_name": {"query": keyword}
                            }
                        },
                        "filter": {
                            "term": {
                                "feature": "news"
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
                                    "category_name.keyword": candidate_names # 후보군 필터링
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

    # ✅ 3. 해당 카테고리의 뉴스 조회
    news_list = (
        db.query(News)
        .filter(News.category_id == category_id)
        .order_by(News.publish_date.desc())
        .limit(limit)
        .all()
    )

    # ✅ 4. 뉴스 결과 정리
    results = [
        {
            "title": news.title,
            "source": news.source,
            "publish_date": news.publish_date.isoformat(), # date → 문자열 (ISO 포맷)
            "url": news.url,
            "original_url": news.original_url
        }
        for news in news_list
    ]

    # ✅ 5. 최종 응답 반환
    return {
        "matched_category": matched_category,
        "results": results
    }
