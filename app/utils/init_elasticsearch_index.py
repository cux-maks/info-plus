"""
Elasticsearch에 카테고리 정보를 색인하는 모듈입니다.
이 모듈은 사전에 정의된 카테고리 리스트(CATEGORIES)를 기반으로
Elasticsearch 'categories' 인덱스를 생성하고, 자동완성 기능을 지원하기 위해
edge_ngram 분석기를 적용한 매핑을 설정합니다.
주요 기능은 인덱스 삭제 후 재생성 및 초기 데이터 삽입입니다.
"""
from elasticsearch import Elasticsearch

es = Elasticsearch("http://elasticsearch:9200")

CATEGORIES = [
    {"category_id": 1, "category_name": "IT/과학", "feature": "news"},
    {"category_id": 2, "category_name": "마케팅", "feature": "news"},
    {"category_id": 3, "category_name": "디자인", "feature": "news"},
    {"category_id": 4, "category_name": "경영/기획", "feature": "news"},
    {"category_id": 5, "category_name": "영업/제휴", "feature": "news"},
    {"category_id": 6, "category_name": "정치", "feature": "news"},
    {"category_id": 7, "category_name": "경제", "feature": "news"},
    {"category_id": 8, "category_name": "사회", "feature": "news"},
    {"category_id": 9, "category_name": "생활/문화", "feature": "news"},
    {"category_id": 10, "category_name": "세계", "feature": "news"},
    {"category_id": 11, "category_name": "사업관리", "feature": "employee"},
    {"category_id": 12, "category_name": "경영·회계·사무", "feature": "employee"},
    {"category_id": 13, "category_name": "금융·보험", "feature": "employee"},
    {"category_id": 14, "category_name": "교육·자연·사회과학", "feature": "employee"},
    {"category_id": 15, "category_name": "법률·경찰·소방·교도·국방", "feature": "employee"},
    {"category_id": 16, "category_name": "보건·의료", "feature": "employee"},
    {"category_id": 17, "category_name": "사회복지·종교", "feature": "employee"},
    {"category_id": 18, "category_name": "문화·예술·디자인·방송", "feature": "employee"},
    {"category_id": 19, "category_name": "운전·운송", "feature": "employee"},
    {"category_id": 20, "category_name": "영업판매", "feature": "employee"},
    {"category_id": 21, "category_name": "경비·청소", "feature": "employee"},
    {"category_id": 22, "category_name": "이용·숙박·여행·오락·스포츠", "feature": "employee"},
    {"category_id": 23, "category_name": "음식서비스", "feature": "employee"},
    {"category_id": 24, "category_name": "건설", "feature": "employee"},
    {"category_id": 25, "category_name": "기계", "feature": "employee"},
    {"category_id": 26, "category_name": "재료", "feature": "employee"},
    {"category_id": 27, "category_name": "화학", "feature": "employee"},
    {"category_id": 28, "category_name": "섬유·의복", "feature": "employee"},
    {"category_id": 29, "category_name": "전기·전자", "feature": "employee"},
    {"category_id": 30, "category_name": "정보통신", "feature": "employee"},
    {"category_id": 31, "category_name": "식품가공", "feature": "employee"},
    {"category_id": 32, "category_name": "인쇄·목재·가구·공예", "feature": "employee"},
    {"category_id": 33, "category_name": "환경·에너지·안전", "feature": "employee"},
    {"category_id": 34, "category_name": "농림어업", "feature": "employee"},
    {"category_id": 35, "category_name": "연구", "feature": "employee"},
]

def create_category_index():
    """
    Elasticsearch에 'categories' 인덱스를 생성하고,
    사전에 정의된 CATEGORIES 리스트의 데이터를 색인한다.
    기존에 'categories' 인덱스가 존재하면 삭제 후 새로 생성한다.
    인덱스 매핑은 다음과 같다:
    - category_id: 정수형
    - category_name: 텍스트, edge_ngram 기반 자동완성(analyzer: autocomplete) 적용
    - feature: 키워드형, 카테고리 구분용 (예: 'news', 'employee')
    """
    index_name = "categories"

    if es.indices.exists(index="categories"):
        es.indices.delete(index="categories")
        print(f"🗑️ 기존 Elasticsearch 인덱스 '{index_name}' 삭제 완료")

    index_body = {
        "settings": {
            "analysis": {
                "tokenizer": {
                    "edge_ngram_tokenizer": {
                        "type": "edge_ngram",
                        "min_gram": 2,
                        "max_gram": 10,
                        "token_chars": ["letter", "digit"]
                    }
                },
                "analyzer": {
                    "autocomplete": {
                        "type": "custom",
                        "tokenizer": "edge_ngram_tokenizer",
                        "filter": ["lowercase"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "category_id": {"type": "integer"},
                "category_name": {
                    "type": "text",
                    "analyzer": "autocomplete",  # 색인 시 edge_ngram 기반 분석
                    "search_analyzer": "standard"  # 검색 시 표준 분석기 사용
                },
                "feature": {"type": "keyword"}
            }
        }
    }

    try:
        es.indices.create(index=index_name, body=index_body)
        print(f"✅ Elasticsearch 인덱스 '{index_name}' 생성 완료")
    except Exception as e:
        print(f"❌ 인덱스 생성 실패: {e}")
        return

    success_count = 0
    for cat in CATEGORIES:
        try:
            es.index(index=index_name, document=cat)
            success_count += 1
        except Exception as e:
            print(f"⚠️ 색인 실패 (카테고리: {cat['category_name']}): {e}")

    print(f"📦 총 {success_count}개의 카테고리가 '{index_name}' 인덱스에 색인됨")

if __name__ == "__main__":
    """
    메인 실행 시 create_category_index() 함수를 호출하여
    Elasticsearch에 'categories' 인덱스를 생성하고 초기 데이터를 색인한다.
    """
    create_category_index()
