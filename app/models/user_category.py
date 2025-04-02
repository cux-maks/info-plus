from sqlalchemy import Column, Integer, String, ForeignKey, Boolean,  DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import Base 
from datetime import datetime

class UserCategory(Base):
    __tablename__ = "user_category"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    category_id = Column(Integer, ForeignKey("category.category_id"))  # Category 테이블 참조
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    users = relationship("Users", back_populates="user_category")  # User 모델과 관계 설정
    category = relationship("Category", back_populates="user_category")  # Category 모델과 관계 설정
