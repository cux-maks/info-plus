"""유효성 검증 API 모듈.

이 모듈은 각 도메인에서 공통으로 사용되는 검증 로직을 함께 관리합니다.
"""

import re

from fastapi import Depends, Query
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.users import Users
from app.utils.db_manager import db_manager

db_dependency = Depends(db_manager.get_db)

def verify_exists_user(
    user_id: str = Query(..., description="User ID"),
    db: Session = db_dependency
):
    user_exists = db.query(Users).filter(Users.user_id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found.")

def verify_special_character(content: str):
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", content):
        raise HTTPException(status_code=400, detail="Special characters are not allowed.")
