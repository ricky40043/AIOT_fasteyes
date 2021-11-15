from typing import Optional

from pydantic import BaseModel

from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Ip_CamInfoModel(Base):
    ip: str
    port: str
    username: str
    password: str
    stream_name: str

    class Config:
        schema_extra = {
            "example": {
                "stream_name": "live1s1.sdp",
                "ip": "192.168.45.64",
                "port": "554",
                "username": "root",
                "password": "a1234567"
            }
        }


class Ip_CamPostModel(Base):
    info: Ip_CamInfoModel
    name: str
    area: str
    serial_number: str

    class Config:
        schema_extra = {
            "example": {
                "info": {
                    "stream_name": "live1s1.sdp",
                    "ip": "192.168.45.64",
                    "port": "554",
                    "username": "root",
                    "password": "a1234567"
                }
            }
        }


class Ip_CamDevicePatchModel(Base):
    name: str
    area: str
    info: Ip_CamInfoModel

    class Config:
        schema_extra = {
            "example": {
                "name": "ip_cam1",
                "info": {
                    "serial_number": "ip_cam1",
                    "stream_name": "live1s1.sdp",
                    "ip": "192.168.45.64",
                    "port": "554",
                    "username": "root",
                    "password": "a1234567"
                }
            }
        }


# class Ip_CamDeviceViewModel(Base):
#     id: int
#     user_id: int
#     group_id: int
#     devicemodel_id: int
#     name: str
#     info: Ip_CamInfoModel
#     created_at: datetime
#     updated_at: datetime
