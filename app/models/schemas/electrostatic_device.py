from typing import Optional

from pydantic import BaseModel

from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ElectrostaticDeviceInfoModel(Base):
    description: str
    left_alarm: float
    right_alarm: float
    head_alarm: float


class ElectrostaticDevicePostModel(Base):
    name: str
    info: ElectrostaticDeviceInfoModel

    class Config:
        schema_extra = {
            "example": {
                "name": "ElectrostaticDevice1",
                "info": {
                    "description": "str",
                    "left_alarm": "60.3",
                    "right_alarm": "60.5",
                    "head_alarm": "12.8"
                }
            }
        }


class ElectrostaticDevicePatchModel(Base):
    id: int
    name: str
    info: ElectrostaticDeviceInfoModel

    class Config:
        schema_extra = {
            "example": {
                "id": "1",
                "name": "ElectrostaticDevice1",
                "info": {
                    "serial_number": "str",
                    "ip": "192.168.1.1",
                    "username": "sumi",
                    "password": "12345678"
                }
            }
        }


class ElectrostaticDeviceViewModel(Base):
    id: int
    user_id: int
    group_id: int
    devicemodel_id: int
    name: str
    info: ElectrostaticDeviceInfoModel
    created_at: datetime
    updated_at: datetime
