from sqlalchemy import  Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base


class EmployeeCategory(Base):
    """채용공고와 카테고리 간의 다대다 관계를 나타내는 모델 클래스.

    Attributes:
        recruit_id (str): 채용공고 ID (외래 키).
        category_id (int): 카테고리 ID (외래 키).
        employee (relationship): Employee 테이블과의 관계.
        category (relationship): Category 테이블과의 관계.
    """
    
    __tablename__ = "employee_category"

    recruit_id = Column(Integer, ForeignKey("employee.recruit_id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("category.category_id"), primary_key=True)

    employee = relationship("Employee", back_populates="categories")
    category = relationship("Category", back_populates="employee_categories")
