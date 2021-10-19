from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from app.db.database import Base
from datetime import datetime


class department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))

    def __init__(self, name, group_id):
        self.name = name
        self.group_id = group_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'group_id': self.group_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
        }
