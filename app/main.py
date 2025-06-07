"""KakaoTalk Chatbot API 서버 모듈.

이 모듈은 KakaoTalk 챗봇 API 서버의 메인 진입점입니다.
FastAPI를 사용하여 RESTful API 엔드포인트를 제공합니다.

이 모듈은 다음과 같은 기능을 제공합니다:
- CORS 미들웨어 설정
- 사용자 관련 라우터 등록
- 기본 루트 엔드포인트 제공
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.employee import router as employee_router
from app.routers.feature import router as feature_router
from app.routers.news import router as news_router
from app.routers.user import router as user_router
from app.utils.init_elasticsearch_index import create_category_index


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 실행할 코드
    create_category_index()
    yield
    # 서버 종료 시 실행할 코드 (필요 시 여기에 정리 작업 가능)

app = FastAPI(
    title="KakaoTalk Chatbot API",
    description="KakaoTalk Chatbot Template API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/user")
app.include_router(employee_router, prefix="/employee")
app.include_router(news_router, prefix="/news")
app.include_router(feature_router, prefix="/feature")
@app.post("/")
async def root():
    """루트 엔드포인트 핸들러.
    API 서버가 정상적으로 실행 중임을 확인하기 위한 기본 엔드포인트입니다.
    Returns:
        dict: 서버 상태 메시지를 포함하는 딕셔너리.
    """
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "안녕하세요. 테스트용 응답입니다."
                    }
                }
            ]
        }
    }
