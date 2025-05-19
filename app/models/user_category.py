"""사용자-카테고리 관계를 관리하는 데이터베이스 모델 모듈.

이 모듈은 사용자와 카테고리 간의 다대다(N:M) 관계를 관리하는 데이터베이스 모델을 포함합니다.
사용자의 카테고리 구독 상태와 관련된 정보를 저장합니다.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserCategory(Base):
    """사용자-카테고리 관계를 저장하는 데이터베이스 모델 클래스.

    이 클래스는 사용자와 카테고리 간의 구독 관계를 저장하며, Users 모델과 Category 모델과
    관계를 가집니다.

    Attributes:
        id (int): 관계의 고유 식별자.
        user_id (str): 사용자 ID (Users 테이블 참조).
        category_id (int): 카테고리 ID (Category 테이블 참조).
        is_active (bool): 카테고리 구독 활성화 상태.
        created_at (datetime): 관계 생성 시간.
        users (relationship): Users 모델과의 관계 객체.
        category (relationship): Category 모델과의 관계 객체.
    """

    __tablename__ = "user_category"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    category_id = Column(Integer, ForeignKey("category.category_id"))  # Category 테이블 참조
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    users = relationship("Users", back_populates="user_category")  # User 모델과 관계 설정
    category = relationship("Category", back_populates="user_category")  # Category 모델과 관계 설정
