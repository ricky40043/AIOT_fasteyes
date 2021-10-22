from pydantic import BaseModel
from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float

from sqlalchemy.orm import relationship

from app.db.database import Base


class fasteyes_device(Base):
    __tablename__ = "fasteyes_devices"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    device_uuid = Column(Text, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    info = Column(JSON, index=True)
    uploadScreenshot = Column(Integer, index=True)
    body_temperature_threshold = Column(Float, index=True)

    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    def __init__(self, user_id, group_id, device_uuid, name, description, **kwargs):
        self.user_id = user_id
        self.group_id = group_id
        self.device_uuid = str(device_uuid)
        self.name = name
        self.description = description
        self.info = {
            "body_temperature_threshold" : "37.5",
            "uploadScreenshot" : "0"
        }
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    # def __repr__(self):
    #     return 'id={}, name={}, description={},registered_at={},updated_at={} '.format(
    #         self.id, self.name, self.description, self.registered_at, self.updated_at
    #     )
    #
    # def to_dict(self):
    #     return {
    #         'id': self.id,
    #         'name': self.name,
    #         'description': self.description,
    #         'registered_at': str(self.registered_at),
    #         'created_at': str(self.created_at),
    #         'updated_at': str(self.updated_at),
    #         'is_enable': self.is_enable,
    #         'device_uuid': self.device_uuid,
    #         'user_id': self.user_id
    #     }
