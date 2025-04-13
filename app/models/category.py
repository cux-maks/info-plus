"""카테고리 정보를 관리하는 데이터베이스 모델 모듈.

이 모듈은 기능 유형별 카테고리를 정의하고 관리하는 데이터베이스 모델을 포함합니다.
Feature 모델과 UserCategory 모델과의 관계를 설정합니다.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class Category(Base):
    """카테고리 정보를 저장하는 데이터베이스 모델 클래스.

    이 클래스는 기능 유형별 카테고리 정보를 저장하며, Feature 모델과 UserCategory 모델과
    관계를 가집니다.

    Attributes:
        category_id (int): 카테고리의 고유 식별자.
        feature_id (int): 연관된 기능 유형의 ID (Feature 테이블 참조).
        category_name (str): 카테고리 이름.
        created_at (datetime): 카테고리 생성 시간.
        user_category (relationship): UserCategory 모델과의 관계 객체.
        feature (relationship): Feature 모델과의 관계 객체.
    """

    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    feature_id = Column(Integer, ForeignKey("feature.feature_id"), nullable=False)  # Feature 테이블 참조
    category_name = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # UserCategory 모델과 관계를 설정
    user_category = relationship("UserCategory", back_populates="category")
    feature = relationship("Feature", back_populates="category")  # Feature 모델과 관계 설정
    employee = relationship("Employee", back_populates="category")  # empluyee 모델과 관계 설정
