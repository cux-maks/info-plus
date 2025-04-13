"""채용 정보를 관리하는 데이터베이스 모델 모듈.

이 모듈은 채용 공고 데이터를 저장하고, 카테고리와의 외래 키 관계를 정의합니다.
사용자 맞춤 추천, 공고 목록 제공 등에 사용됩니다.
"""

from sqlalchemy import Column, String, Integer, Date, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class Employee(Base):
    """채용 공고 정보를 저장하는 데이터베이스 모델 클래스.

    채용 공고의 제목, 기관, 기간, 형태 등 주요 정보를 포함하며,
    카테고리(category_id)와 외래 키로 연결됩니다.

    Attributes:
        recruit_id (str): 채용 공고의 고유 ID.
        category_id (int): 카테고리 테이블의 외래 키.
        title (str): 채용 공고 제목.
        institution (str): 채용 기관명.
        start_date (date): 공고 시작일.
        end_date (date): 공고 마감일.
        recrut_se (str): 경력 구분 (신입/경력).
        hire_type_lst (str): 채용 형태 목록.
        ncs_cd_lst (str): NCS 직무 코드 목록.
        detail_url (str): 공고 상세보기 URL.
        recrut_pblnt_sn (int): 채용 공고 고유 번호 (숫자 ID).
        created_at (datetime): 데이터 저장 시각 (자동 생성).
        category (relationship): Category 모델과의 관계.
    """

    __tablename__ = "employee"

    recruit_id = Column(String(50), primary_key=True)  # 채용 고유 ID
    category_id = Column(Integer, ForeignKey("category.category_id"), nullable=False)  # 외래 키
    title = Column(String(255), nullable=False)  # 채용 제목
    institution = Column(String(100), nullable=False)  # 기관명
    start_date = Column(String(100), nullable=False) # 공고 시작일
    end_date = Column(String(100), nullable=False) # 공고 마감일
    recrut_se = Column(String(100), nullable=True)  # 신입/경력
    hire_type_lst = Column(String(100), nullable=True)  # 정규직/계약직 등
    ncs_cd_lst = Column(String(100), nullable=True)  # 직무 코드
    detail_url = Column(String(255), nullable=True)  # 상세 링크
    recrut_pblnt_sn = Column(Integer, nullable=False, unique=True)  # ALIO 공고 고유번호
    created_at = Column(TIMESTAMP, server_default=func.now())  # 등록 시각

    category = relationship("Category", back_populates="employee")  # 역방향 참조
