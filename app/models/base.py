# app/models/base.py
"""SQLAlchemy 모델의 기본 클래스를 정의하는 모듈.

이 모듈은 모든 데이터베이스 모델의 기본이 되는 declarative base 클래스를 제공합니다.
SQLAlchemy ORM을 사용하여 데이터베이스 모델을 정의할 때 이 base 클래스를 상속받아 사용합니다.
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
"""모든 데이터베이스 모델의 기본이 되는 declarative base 클래스.

이 클래스는 SQLAlchemy의 declarative_base()를 통해 생성되며,
모든 데이터베이스 모델 클래스가 상속받아 사용하는 기본 클래스입니다.

Attributes:
    None
"""
