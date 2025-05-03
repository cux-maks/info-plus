from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base


class EmployeeHireType(Base):
    """채용공고와 채용형태 간의 다대다 관계를 나타내는 모델 클래스.

    Attributes:
        recruit_id (int): 채용공고 ID (외래 키).
        hire_id (int): 채용형태 ID (외래 키).
        employee (relationship): Employee 테이블과의 관계.
        hire_type (relationship): HireType 테이블과의 관계.
    """

    __tablename__ = "employee_hire_type"

    recruit_id = Column(Integer, ForeignKey("employee.recruit_id"), primary_key=True)
    hire_id = Column(Integer, ForeignKey("hire_type.hire_id"), primary_key=True)

    employee = relationship("Employee", back_populates="hire_types")
    hire_type = relationship("HireType", back_populates="employees")
