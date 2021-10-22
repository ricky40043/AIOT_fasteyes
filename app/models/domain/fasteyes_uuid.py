from pydantic import BaseModel
from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey

from app.db.database import Base

class fasteyes_uuid(Base):
    __tablename__ = "fasteyes_uuids"
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(Text, index=True)
    hardware_uuid = Column(Text, index=True)
    creator = Column(String, index=True)
    product_number = Column(String, index=True)
    is_registered = Column(Boolean, index=True)
    registered_at = Column(DateTime, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    def __init__(self, uuid, hardware_uuid, creator, product_number):
        self.uuid = str(uuid)
        self.hardware_uuid = str(hardware_uuid)
        self.creator = creator
        self.product_number = product_number
        self.is_registered = False
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    # def __repr__(self):
    #     return 'id={}, uuid={}, creator={},created_at={},updated_at={},is_registered={},device_uuid={} '.format(
    #         self.id, self.uuid, self.creator, self.created_at, self.updated_at, self.is_registered, self.device_uuid
    #     )
