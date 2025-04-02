import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import OperationalError
import time

from app.models.base import Base

load_dotenv()

class DBManager:
    def __init__(self):
        db_url = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        self.engine = None
        for i in range(10):
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
        """ 테이블이 없으면 자동 생성 """
        Base.metadata.create_all(self.engine)

    def get_db(self):
        """ 세션을 생성하고 반환 """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

db_manager = DBManager()
db_manager.init_db()
