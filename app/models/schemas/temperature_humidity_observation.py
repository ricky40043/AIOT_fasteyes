# from typing import List
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Json

# from app.models.domain.item import item
from datetime import datetime, time, date as Date


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class temperature_humidity_infoModel(Base):
    temperature: float
    humidity: float
    index: int
    alarm_temperature: bool
    alarm_humidity: bool
    battery: int
    status: int


class temperature_humidity_ObservationPostModel(Base):
    info: temperature_humidity_infoModel
    devicemodel_id: int
    device_id: int
    group_id: int

    class Config:
        schema_extra = {
            "example": {
                "devicemodel_id": 1,
                "staff_id": 5,
                "info": {
                    "temperature": 38.0,
                    "humidity": 43,
                    "index": 432,
                    "alarm_temperature": False,
                    "alarm_humidity": True,
                    "battery": 99,
                    "status": 0
                }
            }
        }