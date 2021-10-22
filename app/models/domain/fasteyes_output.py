from pydantic import BaseModel
from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey,JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


class fasteyes_output(Base):
    __tablename__ = "fasteyes_output"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    time = Column(Boolean, index=True)
    department = Column(Boolean, index=True)
    name = Column(Boolean, index=True)
    observation_ID = Column(Boolean, index=True)
    wear_mask = Column(Boolean, index=True)
    temperature = Column(Boolean, index=True)
    threshold_temperature = Column(Boolean, index=True)
    compensate_temperature = Column(Boolean, index=True)
    device_ID = Column(Boolean, index=True)
    result = Column(Boolean, index=True)
    output_time = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    def __init__(self, user_id, group_id, time, department, name, observation_ID,
                 wear_mask, temperature, threshold_temperature, compensate_temperature,
                 device_ID, result, output_time, updated_at, **kwargs):
        self.user_id = user_id
        self.group_id = group_id
        self.time = time
        self.name = name
        self.department = department
        self.observation_ID = observation_ID
        self.wear_mask = wear_mask
        self.temperature = temperature
        self.threshold_temperature = threshold_temperature
        self.compensate_temperature = compensate_temperature
        self.device_ID = device_ID
        self.result = result
        self.output_time = output_time
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
