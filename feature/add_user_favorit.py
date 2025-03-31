from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()
router = APIRouter()

# DB 연결 함수
def get_db_connection():
    db_name = os.getenv("DB_NAME")  # 환경 변수에서 DB 이름 가져오기
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# 요청 데이터 검증용 Pydantic 모델
class SubscriptionRequest(BaseModel):
    user_id: str = Field(..., example="user123")
    category_id: int = Field(..., example=1)

# 사용자 카테고리 구독 API
@router.post("/adduserfavorit", responses={
    200: {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {"message": "Subscription successful!"}
            }
        }
    },
    400: {
        "description": "Already subscribed to this category",
        "content": {
            "application/json": {
                "example": {"detail": "Already subscribed to this category."}
            }
        }
    }
})
def add_category(request: SubscriptionRequest):
    db = get_db_connection()
    cursor = db.cursor()

    # 중복 체크
    cursor.execute(
        "SELECT * FROM user_category WHERE user_id = %s AND category_id = %s",
        (request.user_id, request.category_id)
    )
    existing_subscription = cursor.fetchone()

    if existing_subscription:
        db.close()
        raise HTTPException(status_code=400, detail="Already subscribed to this category.")

    # 구독 정보 추가
    cursor.execute(
        "INSERT INTO user_category (user_id, category_id, is_active, created_at) VALUES (%s, %s, %s, NOW())",
        (request.user_id, request.category_id, True)
    )

    db.commit()
    db.close()
    return {"message": "Subscription successful!"}