"""카테고리를 관리하는 데이터베이스 모델 모듈.

이 모듈은 시스템에서 사용되는 카테고리를 정의하고 관리하는
데이터베이스 모델을 포함합니다.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class Category(Base):
    """카테고리를 저장하는 데이터베이스 모델 클래스.

    이 클래스는 시스템에서 사용되는 카테고리를 정의하며,
    Feature 모델과 N:1 관계를 가집니다.

    Attributes:
        category_id (int): 카테고리의 고유 식별자.
        feature_id (int): 기능 유형 ID (Feature 테이블 참조).
        category_name (str): 카테고리 이름.
        created_at (datetime): 카테고리 생성 시간.
        feature (relationship): Feature 모델과의 관계 객체.
        user_category (relationship): UserCategory 모델과의 관계 객체.
        news (relationship): News 모델과의 관계 객체.
        employee (relationship): Employee 모델과의 관계 객체.
    """

    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    feature_id = Column(Integer, ForeignKey("feature.feature_id"), nullable=False)
    category_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())

    feature = relationship("Feature", back_populates="category")
    user_category = relationship("UserCategory", back_populates="category")
    news = relationship("News", back_populates="category_rel")
    employee = relationship("Employee", back_populates="category")
