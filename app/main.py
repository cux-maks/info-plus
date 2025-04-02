from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.message import router as kakao_router
from app.routers.user import router as add_user_favorit_router

app = FastAPI(
    title="KakaoTalk Chatbot API",
    description="KakaoTalk Chatbot Template API",
    version="0.1.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(kakao_router)
app.include_router(add_user_favorit_router, prefix="/user")  # add_user_favorit 라우터 등록


@app.get("/")
async def root():
    return {"message": "KakaoTalk Chatbot API is running"}
