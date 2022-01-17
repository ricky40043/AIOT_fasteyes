from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from app.db.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

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

    def __init__(self, text, group_id, picture_name, picture_or_text, **kwargs):
        self.group_id = group_id
        self.text = text
        self.picture_name = picture_name
        self.picture_or_text = picture_or_text
        self.is_used = False
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

