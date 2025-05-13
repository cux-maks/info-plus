import hashlib
import logging
import os
from datetime import datetime
from urllib.parse import urlparse

import requests
import yaml
from fastapi import Depends
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.news import News
from app.utils.db_manager import db_manager

logger = logging.getLogger(__name__)

NAVER_API_URL = 'https://openapi.naver.com/v1/search/news.json'
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

yaml_path = os.path.join("/app/utils/news_provider_mapping.yaml")
db_dependency = Depends(db_manager.get_db)

with open(yaml_path, "r", encoding="utf-8") as file:
    DOMAIN_TO_PROVIDER = yaml.safe_load(file)

def get_subscribed_news_list(
    limit: int = 10,
    db: Session = db_dependency
):
    categories = db.query(Category).all()
    saved_count = 0
    for category in categories:
        news_list = get_news_list_from_naver(category, limit)

        for news in news_list:
            exists = db.query(News).filter(News.news_id == news.news_id).first()
            if not exists:
                db.add(news)
                saved_count += 1

    db.commit()
    logger.info(f"{saved_count}개의 뉴스 저장 완료")

def get_news_list_from_naver(category: Category, display: int = 10, start: int = 1, sort: str = "date"):
    query = category.category_name
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort,
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    news_response = response.json()
    return parse_naver_news(news_response, category.category_id, query)

def parse_naver_news(json_data, category_id, category_name):
    news_list = []

    for item in json_data.get("items", []):
        title = item.get("title", "").replace("<b>", "").replace("</b>", "")
        originallink = item.get("originallink")
        link = item.get("link")
        description = item.get("description", "").replace("<b>", "").replace("</b>", "")
        pub_date_str = item.get("pubDate")

        try:
            publish_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
        except Exception:
            publish_date = None

        # 링크를 해시하여 고유 ID로 사용
        news_id = int(hashlib.sha256(link.encode()).hexdigest(), 16) % (10 ** 10)

        news = News(
            news_id=news_id,
            category_id=category_id,
            title=title,
            contents=description,
            source=map_news_source(originallink),
            publish_date=publish_date,
            category=category_name,
            url=link,
            original_url=originallink,
            created_at=datetime.now()
        )

        news_list.append(news)

    return news_list

# 언론사 추출 함수
def map_news_source(source_url: str) -> str:
    try:
        domain = urlparse(source_url).netloc.replace("www.", "")
        return DOMAIN_TO_PROVIDER.get(domain, "Unknown")
    except Exception:
        return "Unknown"
