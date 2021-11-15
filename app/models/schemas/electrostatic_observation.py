# from typing import List
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Json

# from app.models.domain.item import item
from datetime import datetime, time, date as Date


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class electrostatic_infoModel(Base):
    left: float
    right: float
    head: float
    alarm_left: bool
    alarm_right: bool
    alarm_head: bool
    result: bool
    staff_id: int


class electrostatic_ObservationPostModel(Base):
    info: electrostatic_infoModel
    devicemodel_id: int
    device_id: int
    group_id: int

    class Config:
        schema_extra = {
            "example": {
                "devicemodel_id": 1,
                "staff_id": 5,
                "info": {
                    "left": 38.0,
                    "right": 43.0,
                    "head": 56.0,
                    "alarm_left": 38.0,
                    "alarm_right": 43.0,
                    "alarm_head": 56.0,
                    "result": False,
                    "staff_id": 1
                }
            }
        }