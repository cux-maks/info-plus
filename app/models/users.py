from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import Base 

class Users(Base):
    __tablename__ = "users"

    user_id = Column(String(30), primary_key=True)  # 카카오톡 user_key
    user_name = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=func.now())

    # UserCategory 모델과 관계를 설정
    user_category = relationship("UserCategory", back_populates="users")