from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base 

class Feature(Base):
    __tablename__ = "feature"

    feature_id = Column(Integer, primary_key=True, autoincrement=True)
    feature_type = Column(String(30))  # 뉴스, 채용 정보 등

    category = relationship("Category", back_populates="feature")  # Category 모델과 관계 설정