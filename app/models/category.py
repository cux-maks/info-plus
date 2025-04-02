from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    feature_id = Column(Integer, ForeignKey("feature.feature_id"), nullable=False)  # Feature 테이블 참조
    category_name = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # UserCategory 모델과 관계를 설정
    user_category = relationship("UserCategory", back_populates="category")
    feature = relationship("Feature", back_populates="category")  # Feature 모델과 관계 설정
