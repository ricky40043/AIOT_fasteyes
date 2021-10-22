from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from app.db.database import Base
from datetime import datetime


class group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    def __init__(self, name, **kwargs):
        self.name = name
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

