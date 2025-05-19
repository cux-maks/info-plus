"""사용자 정보를 관리하는 데이터베이스 모델 모듈.

이 모듈은 사용자의 기본 정보를 저장하고 관리하는 데이터베이스 모델을 정의합니다.
카카오톡 사용자 정보를 기반으로 하며, 사용자 카테고리와의 관계를 설정합니다.
"""

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class Users(Base):
    """사용자 정보를 저장하는 데이터베이스 모델 클래스.

    이 클래스는 사용자의 기본 정보를 저장하며, UserCategory 모델과 1:N 관계를 가집니다.

    Attributes:
        user_id (str): 사용자의 고유 식별자 (카카오톡 user_key).
        user_name (str): 사용자의 이름.
        created_at (datetime): 사용자 계정 생성 시간.
        user_category (relationship): UserCategory 모델과의 관계 객체.
    """

    __tablename__ = "users"

    user_id = Column(String(30), primary_key=True)  # 카카오톡 user_key
    user_name = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=func.now())

    # UserCategory 모델과 관계를 설정
    user_category = relationship("UserCategory", back_populates="users")
