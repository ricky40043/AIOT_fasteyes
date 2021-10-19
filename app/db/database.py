from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import class_mapper

import os

# config_path = os.path.abspath(os.path.dirname(__file__))
# print(config_path)
# SQLALCHEMY_DATABASE_URL = "sqlite:///"+ os.path.join(config_path, 'sql_app_20210304.db')
SQLALCHEMY_DATABASE_URL = "sqlite:///sql_app_20210924.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:88888888@192.168.45.51/fastapi_db_20210924"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
    # SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine, )
Base = declarative_base()


def get_db():
    db = SessionLocal()
    # db.execute("PRAGMA journal_mode = OFF")
    try:
        yield db
    finally:
        db.close()
