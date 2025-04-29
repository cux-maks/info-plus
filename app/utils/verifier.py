"""유효성 검증 API 모듈.

이 모듈은 각 도메인에서 공통으로 사용되는 검증 로직을 함께 관리합니다.
"""

import re

from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.users import Users
from app.utils.db_manager import db_manager

db_dependency = Depends(db_manager.get_db)

def verify_exists_user(
    user_id: str = Query(..., description="User ID"),
    db: Session = db_dependency
):
    """사용자가 특정 카테고리를 구독하는 엔드포인트입니다.

        Args:
            user_id: 검증 받을 사용자 객체
            db (Session): 데이터베이스 세션.

        Returns:
            None

        Raises:
            HTTPException 404: 존재하지 않는 사용자일 경우.
    """

    user_exists = db.query(Users).filter(Users.user_id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found.")

def verify_special_character(content: str):
    """사용자가 특정 카테고리를 구독하는 엔드포인트입니다.

        Args:
            content: 검증 받을 문자열 객체

        Returns:
            None

        Raises:
            HTTPException 400: 특수 기호가 문장에 포함되어 있을 경우.
    """
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", content):
        raise HTTPException(status_code=400, detail="Special characters are not allowed.")
