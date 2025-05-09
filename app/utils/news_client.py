import hashlib
import os
from datetime import datetime
from app.models.news import News

import requests

NAVER_API_URL = 'https://openapi.naver.com/v1/search/news.json'
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

def fetch_naver_news(query: str, display: int = 10, start: int = 1, sort: str = "date"):
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
    return parse_naver_news_json(news_response, 1, query)

def parse_naver_news_json(json_data, category_id, category_name):
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

from urllib.parse import urlparse

# 언론사 도메인 매핑 사전
DOMAIN_TO_PROVIDER = {
    "akomnews.com": "대한한의사협회뉴스",
    "asiatoday.co.kr": "아시아투데이",
    "beyondpost.co.kr": "비욘드포스트",
    "biz.heraldcorp.com": "헤럴드경제",
    "bntnews.co.kr": "비앤티뉴스",
    "breaknews.com": "브레이크뉴스",
    "chosun.com": "조선일보",
    "coinreaders.com": "코인리더스",
    "dnews.co.kr": "디지털타임스",
    "edaily.co.kr": "이데일리",
    "fashionbiz.co.kr": "패션비즈",
    "fnnews.com": "파이낸셜뉴스",
    "hani.co.kr": "한겨레",
    "hankyung.com": "한국경제",
    "ikld.kr": "국토일보",
    "joongdo.co.kr": "중도일보",
    "khan.co.kr": "경향신문",
    "mk.co.kr": "매일경제",
    "munhwa.com": "문화일보",
    "news.tvchosun.com": "TV조선",
    "news1.kr": "뉴스1",
    "newsis.com": "뉴시스",
    "newsnjoy.or.kr": "뉴스앤조이",
    "nocutnews.co.kr": "노컷뉴스",
    "ohmynews.com": "오마이뉴스",
    "pennmike.com": "펜앤드마이크",
    "pressian.com": "프레시안",
    "seouleconews.com": "서울이코노미뉴스",
    "yna.co.kr": "연합뉴스",
    "wikitree.co.kr": "위키트리",
    "news.cpbc.co.kr": "가톨릭평화방송",
    "sisaweek.com": "시사위크",
    "fntoday.co.kr": "파이낸스투데이",
    "n.news.naver.com": "네이버 통합 뉴스",
    "edu.chosun.com": "",
    "enewstoday.co.kr": "",
    "asiatime.co.kr": "",
    "widedaily.com": "",
    "sedaily.com": "",
    "electimes": "",
}

# 언론사 추출 함수
def map_news_source(source_url: str) -> str:
    try:
        domain = urlparse(source_url).netloc.replace("www.", "")
        return DOMAIN_TO_PROVIDER.get(domain, "Unknown")
    except Exception as e:
        return "Unknown"
