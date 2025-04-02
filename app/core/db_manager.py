import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.models.base import Base 

load_dotenv()

class DBManager:
    def __init__(self):
        db_url = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        self.engine = create_engine(db_url, echo=True)
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
