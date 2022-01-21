# from typing import List
from typing import Optional

from pydantic import BaseModel, EmailStr

# from app.models.domain.item import item
from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class DeviceModelPostModel(Base):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "ricky"
            }
        }


class DeviceModelPatchModel(Base):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "ricky"
            }
        }


class DeviceModelViewModel(Base):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class DeviceViewModel(Base):
    id: int
    user_id: int
    group_id: int
    device_model_id: int
    name: str
    area: str
    serial_number: str
    info: dict
    created_at: datetime
    updated_at: datetime


class DevicePostModel(Base):
    name: str
    area: str
    serial_number: str
    info: dict

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "name": "1705EF",
    #             "info": {
    #                 "serial_number": "Temperature_humidityDevice1",
    #                 "interval_time": "10",
    #                 "alarm_temperature": "67.9",
    #                 "alarm_humidity": "45.2",
    #                 "battery_alarm": "10"
    #             }
    #         }
    #     }


class DevicePatchModel(Base):
    info: dict
    area: str
    name: str
    serial_number: str
