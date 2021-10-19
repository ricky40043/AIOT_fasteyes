from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from app.db.database import Base


class fasteyes_observation(Base):
    __tablename__ = "fasteyes_observations"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    fasteyes_device_id = Column(Integer, ForeignKey("fasteyes_devices.id"))
    phenomenon_time = Column(DateTime, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    result = Column(Boolean, index=True)
    image_name = Column(String, index=True)
    info = Column(JSON, index=True)
    staff_id = Column(Integer, ForeignKey("staffs.id"))

    def __init__(self, group_id, fasteyes_device_id, phenomenon_time, info, result, image_name, staff_id,  **kwargs):
        self.group_id = group_id
        self.fasteyes_device_id = fasteyes_device_id
        self.phenomenon_time = phenomenon_time
        self.info = info
        self.result = result
        self.image_name = image_name
        self.staff_id = staff_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    # def __repr__(self):
    #     return 'id={}, phenomenon_time={}, result={},wear_mask={},temperature={},staff_id={},image_file_id={},device_id={}'.format(
    #         self.id, self.phenomenon_time, self.result, self.wear_mask, self.temperature, self.staff_id,
    #         self.image_file_id, self.device_id
    #     )

    def to_dict(self):
        return {
            'id': self.id,
            'phenomenon_time': str(self.phenomenon_time),
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'result': self.result,
            # 'wear_mask': self.wear_mask,
            # 'temperature': self.temperature,
            # 'threshold_temperature': self.threshold_temperature,
            # 'compensate_temperature': self.compensate_temperature,
            'info': self.info,
            'image_name': self.image_name,
            'staff_id': self.staff_id,
            'device_id': self.fasteyes_device_id,
            'group_id': self.group_id
        }
