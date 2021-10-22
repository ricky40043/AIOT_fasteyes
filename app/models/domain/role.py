from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from app.db.database import Base
from datetime import datetime


class role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, index=True)
    users_id = Column(Integer, ForeignKey("device_models.id"))
    groups_id = Column(Integer, ForeignKey("groups.id"))

    def __init__(self, name):
        self.name = name
        self.created_at = datetime.now()
