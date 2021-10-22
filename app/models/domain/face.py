from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text

from app.db.database import Base
from datetime import datetime

class face(Base):
    __tablename__ = "faces"
    id = Column(Integer, primary_key=True, index=True)
    face_uuid = Column(Text, unique=True, nullable=False)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    staff_id = Column(Integer, ForeignKey("staffs.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))

    def __init__(self, staff_id, group_id, face_uuid):
        self.staff_id = staff_id
        self.group_id = group_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.face_uuid = str(face_uuid)