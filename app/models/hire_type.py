from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class HireType(Base):
    """채용 형태 정보를 저장하는 테이블 모델 클래스.

    Attributes:
        hire_id (int): 채용 형태 ID.
        hire_name (str): 채용 형태 이름 (예: 정규직, 계약직 등).
        employees (relationship): EmployeeHireType 테이블과의 관계.
    """

    __tablename__ = "hire_type"

    hire_type_id = Column(Integer, primary_key=True, autoincrement=True)
    hire_type_name = Column(String(10), nullable=False)
    hire_type_code = Column(String(10), nullable=False, unique=True)

    employees = relationship("EmployeeHireType", back_populates="hire_type", cascade="all, delete-orphan")
