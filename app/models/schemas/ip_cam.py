from typing import Optional

from pydantic import BaseModel

from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Ip_CamInfoModel(Base):
    serial_number: str
    ip: str
    username: str
    password: str


class Ip_CamPostModel(Base):
    name: str
    info: Ip_CamInfoModel

    class Config:
        schema_extra = {
            "example": {
                "name": "NitrogenDevice1",
                "info": {
                    "serial_number": "str",
                    "ip": "192.168.1.1",
                    "username": "sumi",
                    "password": "12345678"
                }
            }
        }


class Ip_CamDevicePatchModel(Base):
    id: int
    name: str
    info: Ip_CamInfoModel

    class Config:
        schema_extra = {
            "example": {
                "id": "1",
                "name": "Temperature_humidityDevice1",
                "info": {
                    "serial_number": "str",
                    "ip": "192.168.1.1",
                    "username": "sumi",
                    "password": "12345678"
                }
            }
        }


class Ip_CamDeviceViewModel(Base):
    id: int
    user_id: int
    group_id: int
    devicemodel_id: int
    name: str
    info: Ip_CamInfoModel
    created_at: datetime
    updated_at: datetime
