"""기능 유형을 관리하는 데이터베이스 모델 모듈.

이 모듈은 시스템에서 제공하는 기능 유형(뉴스, 채용 정보 등)을 정의하고 관리하는
데이터베이스 모델을 포함합니다.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Feature(Base):
    """기능 유형을 저장하는 데이터베이스 모델 클래스.

    이 클래스는 시스템에서 제공하는 다양한 기능 유형을 정의하며,
    Category 모델과 1:N 관계를 가집니다.

    Attributes:
        feature_id (int): 기능 유형의 고유 식별자.
        feature_type (str): 기능의 유형 (예: 뉴스, 채용 정보 등).
        category (relationship): Category 모델과의 관계 객체.
    """

    __tablename__ = "feature"

    feature_id = Column(Integer, primary_key=True, autoincrement=True)
    feature_type = Column(String(30))  # 뉴스, 채용 정보 등

    category = relationship("Category", back_populates="feature")  # Category 모델과 관계 설정
