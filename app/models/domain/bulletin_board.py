from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, JSON, Boolean
from app.db.database import Base
from datetime import datetime


class bulletin_board(Base):
    __tablename__ = "bulletin_boards"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    picture_name = Column(String, index=True)
    picture_or_text = Column(Boolean, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    is_used = Column(Boolean, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    def __init__(self, device_id, group_id, device_model_id, info):
        self.device_id = device_id
        self.group_id = group_id
        self.device_model_id = device_model_id
        self.info = info
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

