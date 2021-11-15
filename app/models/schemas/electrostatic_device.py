from typing import Optional

from pydantic import BaseModel

from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ElectrostaticDeviceInfoModel(Base):
    left_alarm: float
    right_alarm: float
    head_alarm: float


class ElectrostaticDevicePostModel(Base):
    info: ElectrostaticDeviceInfoModel
    name: str
    serial_number: str
    area: str

    class Config:
        schema_extra = {
            "example": {
                "name": "ElectrostaticDevice1",
                "serial_number": "jfswsad123",
                "area": "room",
                "info": {
                    "left_alarm": "60.3",
                    "right_alarm": "60.5",
                    "head_alarm": "12.8"
                }
            }
        }


class ElectrostaticDevicePatchModel(Base):
    info: ElectrostaticDeviceInfoModel
    name: str
    area: str
    class Config:
        schema_extra = {
            "example": {
                "info": {
                    "description": "str",
                    "left_alarm": "60.3",
                    "right_alarm": "60.5",
                    "head_alarm": "12.8"
                }
            }
        }