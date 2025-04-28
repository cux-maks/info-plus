"""뉴스 정보를 관리하는 데이터베이스 모델 모듈.

이 모듈은 뉴스 정보를 저장하고 관리하는 데이터베이스 모델을 정의합니다.
카테고리와의 관계를 설정하여 뉴스의 분류를 관리합니다.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class News(Base):
    """뉴스 정보를 저장하는 데이터베이스 모델 클래스.

    이 클래스는 뉴스의 기본 정보를 저장하며, Category 모델과 N:1 관계를 가집니다.

    Attributes:
        news_id (int): 뉴스의 고유 식별자.
        category_id (int): 뉴스 카테고리 ID.
        title (str): 뉴스 제목.
        contents (str): 뉴스 본문 관련 텍스트.
        source (str): 제공 기관.
        publish_date (date): 뉴스 작성일.
        category (str): 뉴스의 카테고리.
        url (str): 뉴스 URL.
        created_at (datetime): 데이터베이스에 저장된 시간.
        category (relationship): Category 모델과의 관계 객체.
    """

    __tablename__ = "news"

    news_id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("category.category_id"))
    title = Column(String(255), nullable=False)
    contents = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)
    publish_date = Column(DateTime, nullable=False)
    category = Column(String(50), nullable=False)
    url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())

    category_rel = relationship("Category", back_populates="news")
