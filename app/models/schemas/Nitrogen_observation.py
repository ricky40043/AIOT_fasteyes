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
    nitrogen_pressure: float
    air_press: float
    nitrogen_flowrate: float
    oxygen_content: float

    oxygen_height: bool
    air_press_low: bool
    freeze_drier: bool
    air_system: bool
    nitrogen_press_height: bool
    nitrogen_press_low: bool
    run_status: bool
    stop_status: bool
    standby_status: bool
    maintain_status: bool


class Nitrogen_ObservationPostModel(Base):
    devicemodel_id: int
    device_id: int
    info: Nitrogen_infoModel
    group_id: int

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "devicemodel_id": 1,
    #             "staff_id": 5,
    #             "info": {
    #                 "Nitrogen": 38.0,
    #                 "Oxygen": 43,
    #                 "alarm_temperature": 40,
    #                 "alarm_humidity": 60,
    #                 "status": 1
    #             }
    #         }
    #     }