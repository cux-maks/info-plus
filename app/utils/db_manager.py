"""데이터베이스 연결 및 관리를 위한 유틸리티 모듈.
이 모듈은 PostgreSQL 데이터베이스 연결을 설정하고, 테이블 생성을 관리하며,
기본 데이터를 초기화하는 기능을 제공합니다.
"""

import os
import time

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker

from app.models.base import Base
from app.models.category import Category
from app.models.feature import Feature

load_dotenv()

class DBManager:
    """PostgreSQL 데이터베이스 연결 및 관리를 위한 클래스.
    이 클래스는 데이터베이스 연결을 설정하고, 세션을 관리하며,
    테이블 생성 및 기본 데이터 초기화 기능을 제공합니다.
    """

    def __init__(self):
        """DBManager 클래스의 초기화 메서드.
        환경 변수에서 데이터베이스 연결 정보를 가져와 PostgreSQL에 연결을 시도합니다.
        연결이 실패할 경우 최대 1000번까지 재시도합니다.
        Raises:
            RuntimeError: 모든 재시도 후에도 데이터베이스 연결에 실패한 경우.
        """
        db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        self.engine = None
        for _ in range(1000):
            try:
                self.engine = create_engine(db_url, echo=True)
                # 연결 테스트
                with self.engine.connect():
                    break
            except OperationalError:
                print("❗ PostgreSQL 연결 실패... 재시도 중")
                time.sleep(2)

        if self.engine is None:
            raise RuntimeError("🚨 DB 연결 실패: 재시도 후에도 연결되지 않음")
        self.SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

    def init_db(self):
        """데이터베이스 테이블을 초기화합니다.
        Base 클래스에 정의된 모든 모델에 해당하는 테이블이 없는 경우 자동으로 생성합니다.
        """
        Base.metadata.create_all(self.engine)

    def get_db(self):
        """데이터베이스 세션을 생성하고 반환하는 제너레이터 함수.
        Yields:
            Session: SQLAlchemy 세션 객체.
        Note:
            이 함수는 컨텍스트 매니저로 사용되어야 하며, 사용 후 자동으로 세션이 닫힙니다.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def init_default_data(self):
        """기본 데이터를 데이터베이스에 초기화합니다.
        Feature와 Category 모델에 대한 기본 데이터를 생성합니다.
        이미 데이터가 존재하는 경우 IntegrityError가 발생하며, 이 경우 롤백됩니다.
        """
        db = next(self.get_db())
        try:
            # Feature 기본 데이터
            features = [
                Feature(feature_type="news"),
                Feature(feature_type="employee")
            ]
            for feature in features:
                db.add(feature)

            # Category 기본 데이터
            categories = [
                Category(category_name="IT/개발", feature=features[0]),
                Category(category_name="마케팅", feature=features[0]),
                Category(category_name="디자인", feature=features[0]),
                Category(category_name="경영/기획", feature=features[0]),
                Category(category_name="영업/제휴", feature=features[0]),
                Category(category_name="인사/채용", feature=features[1]),
                Category(category_name="재무/회계", feature=features[1]),
                Category(category_name="법무/법률", feature=features[1]),
                Category(category_name="생산/제조", feature=features[1]),
                Category(category_name="물류/유통", feature=features[1])
            ]
            for category in categories:
                db.add(category)

            db.commit()
            print("✨ 기본 데이터가 성공적으로 추가되었습니다.")
        except IntegrityError:
            db.rollback()
            print("ℹ️ 기본 데이터가 이미 존재합니다.")
        finally:
            db.close()

# 전역 DBManager 인스턴스 생성 및 초기화
db_manager = DBManager()
db_manager.init_db()
db_manager.init_default_data()
