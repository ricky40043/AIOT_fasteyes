from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from app.db.database import Base
from datetime import datetime


class area(Base):
    __tablename__ = "areas"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    name = Column(String, index=True)
    send_mail = Column(Boolean, index=True)
    use_image = Column(Boolean, index=True)
    created_at = Column(DateTime, index=True)

    def __init__(self, group_id, name):
        self.group_id = group_id
        self.name = name
        self.send_mail = False
        self.use_image = False
        self.created_at = datetime.now()
