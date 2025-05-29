import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from huggingface_hub import login
from elasticsearch import Elasticsearch
import requests  # 추가

# 환경변수 로딩
load_dotenv()
hf_token = os.getenv("HUGGINGFACE_TOKEN")

# Hugging Face 로그인 (모델 로딩 전)
if hf_token:
    login(token=hf_token)

# 모델 로드 (384차원 벡터 출력)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Elasticsearch 연결
es = Elasticsearch("http://localhost:9200")

# 인덱스명
INDEX_NAME = "categories"

# 카테고리 목록 (생략)

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

def check_index_exists(index_name: str) -> bool:
    """
    Elasticsearch에서 특정 인덱스가 존재하는지 여부를 확인한다.

    Args:
        index_name (str): 확인할 Elasticsearch 인덱스명.

    Returns:
        bool: 인덱스가 존재하면 True, 존재하지 않으면 False.
    """
    url = f"http://localhost:9200/{index_name}"
    try:
        response = requests.head(url)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            print(f"[⚠️] 인덱스 체크 예상치 못한 상태 코드: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"[❌] 인덱스 체크 실패: {e}")
        return False

def create_category_index():
    """
    Elasticsearch에 'categories' 인덱스를 생성하고,
    카테고리 데이터를 384차원 임베딩 벡터와 함께 색인한다.

    기존 인덱스가 존재할 경우 삭제 후 새로 생성한다.

    - edge_ngram tokenizer와 analyzer를 설정하여
      카테고리명에 대해 부분검색이 가능하도록 한다.
    - 'category_vector' 필드에는 SentenceTransformer로 생성한 벡터를 저장한다.
    """
    # 기존 인덱스 삭제 (REST 호출로 존재 여부 체크)
    if check_index_exists(INDEX_NAME):
        try:
            es.indices.delete(index=INDEX_NAME)
            print(f"[ℹ️] 기존 인덱스 '{INDEX_NAME}' 삭제 완료")
        except Exception as e:
            print(f"[❌] 인덱스 삭제 실패: {e}")
            return

    # 인덱스 생성
    try:
        es.indices.create(
            index=INDEX_NAME,
            body={
                "settings": {
                    "analysis": {
                        "tokenizer": {
                            "edge_ngram_tokenizer": {
                                "type": "edge_ngram",
                                "min_gram": 1,
                                "max_gram": 20,
                                "token_chars": ["letter", "digit"]
                            }
                        },
                        "analyzer": {
                            "edge_ngram_analyzer": {
                                "tokenizer": "edge_ngram_tokenizer",
                                "filter": ["lowercase"]
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "category_id": {"type": "integer"},
                        "feature": {"type": "keyword"},
                        "category_name": {
                            "type": "text",
                            "analyzer": "edge_ngram_analyzer",
                            "search_analyzer": "standard"
                        },
                        "category_vector": {
                            "type": "dense_vector",
                            "dims": 384
                        }
                    }
                }
            }
        )
        print(f"[✅] 인덱스 '{INDEX_NAME}' 생성 완료")
    except Exception as e:
        print("[❌] 인덱스 생성 실패:", e)
        return

    # 데이터 색인
    for cat in CATEGORIES:
        embedding = model.encode(cat["category_name"]).tolist()
        doc = {
            **cat,
            "category_vector": embedding
        }
        try:
            es.index(index=INDEX_NAME, document=doc)
        except Exception as e:
            print(f"[❌] 문서 색인 실패 (category_id={cat['category_id']}): {e}")

if __name__ == "__main__":
    create_category_index()
