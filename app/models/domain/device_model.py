from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from app.db.database import Base
from datetime import datetime


class device_model(Base):
    __tablename__ = "device_models"

    # 1. 溫濕度感應器 2. ip cam 3. 靜電環 4. 氮氣機
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    def __init__(self, name):
        self.name = name
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
