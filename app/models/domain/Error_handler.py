from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from app.db.database import Base
from datetime import datetime


class Error_handler(Base):
    __tablename__ = "Error_handler"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    status_code = Column(Integer, index=True)
    happend_at = Column(DateTime, index=True)

    def __init__(self, name, description, status_code):
        self.name = name
        self.description = description
        self.status_code = status_code
        self.happend_at = datetime.now()


class UnicornException(Exception):
    def __init__(self, name: str, status_code: int, description):
        self.name = name
        self.status_code = status_code
        self.description = description
