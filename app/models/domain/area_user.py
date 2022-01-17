from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from app.db.database import Base
from datetime import datetime


class area_user(Base):
    __tablename__ = "area_users"
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, index=True)

    def __init__(self, area_id, user_id):
        self.area_id = area_id
        self.user_id = user_id
        self.created_at = datetime.now()
