from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.user import router as user_router

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

app.include_router(user_router, prefix="/user")

@app.get("/")
async def root():
    return {"message": "KakaoTalk Chatbot API is running"}
