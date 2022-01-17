from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from app.db.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    serial_number = Column(String, index=True)
    area = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    # 1. 溫濕度感應器 2. ip cam 3. 靜電環 4. 氮氣機
    device_model_id = Column(Integer, ForeignKey("device_models.id"))
    info = Column(JSON)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    def __init__(self, name, user_id, group_id, device_model_id, info, serial_number, area):
        self.name = name
        self.serial_number = serial_number
        self.area = area
        self.user_id = user_id
        self.group_id = group_id
        self.device_model_id = device_model_id
        self.info = info
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

# 1.溫濕度感應器{serial_number, interval_time, alarm_temperature, alarm_humidity, battery,_alarm}
# 2.ip cam{serial_number, ip, username, password}
# 3.靜電環{description, left_alarm, right_alarm, head_alarm}
# 4.氮氣幾{serial_number, Nitrogen_alarm, Oxygen_alarm, interval_time}
