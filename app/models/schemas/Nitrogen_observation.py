# from typing import List
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Json

# from app.models.domain.item import item
from datetime import datetime, time, date as Date


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Nitrogen_infoModel(Base):
    Nitrogen: float
    Oxygen: float
    alarm_Nitrogen: bool
    alarm_Oxygen: bool
    status: int


class Nitrogen_ObservationPostModel(Base):
    devicemodel_id: int
    device_id: int
    info: Nitrogen_infoModel
    group_id: int

    class Config:
        schema_extra = {
            "example": {
                "devicemodel_id": 1,
                "staff_id": 5,
                "info": {
                    "Nitrogen": 38.0,
                    "Oxygen": 43,
                    "alarm_temperature": 40,
                    "alarm_humidity": 60,
                    "status": 1
                }
            }
        }