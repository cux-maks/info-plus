"""일반 사용자 정보를 관리하는 데이터베이스 모델 모듈.

이 모듈은 일반 사용자의 기본 정보와 인증 정보를 저장하고 관리하는 데이터베이스 모델을 정의합니다.
"""

from sqlalchemy import Boolean, Column, DateTime, String, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    """일반 사용자 정보를 저장하는 데이터베이스 모델 클래스.

    이 클래스는 사용자의 기본 정보와 인증 정보를 저장합니다.

    Attributes:
        username (str): 사용자의 로그인 아이디.
        email (str): 사용자의 이메일 주소.
        hashed_password (str): 해시 처리된 비밀번호.
        is_active (bool): 계정 활성화 상태.
        is_superuser (bool): 관리자 권한 여부.
        created_at (datetime): 계정 생성 시간.
    """

    __tablename__ = "user"

    username = Column(String(30), primary_key=True)
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now()) 