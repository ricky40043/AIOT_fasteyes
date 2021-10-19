# from typing import List
from typing import Optional

from pydantic import BaseModel, EmailStr

# from app.models.domain.item import item
from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class FasteyesDevicePostViewModel(Base):
    name: str
    description: str
    device_uuid: str

    class Config:
        schema_extra = {
            "example": {
                "name": "ricky4004",
                "description": "string",
                "device_uuid": "b61fc353-54ba-463c-aab7-0687f705b419"
            }
        }


class FasteyesDevicePatchModel(Base):
    name: str
    description: str

    class Config:
        schema_extra = {
            "example": {
                "name": "ricky4004",
                "description": "string"
            }
        }


class FasteyesDeviceSettingChangeModel(Base):
    uploadScreenshot: Optional[int] = -1
    body_temperature_threshold: Optional[float] = -1

    class Config:
        schema_extra = {
            "example": {
                "uploadScreenshot": "1",
                "body_temperature_threshold": "37.5",
            }
        }


#
# class DevicePatchUserIdViewModel(Base):
#     user_id: str
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "user_id": "456",
#             }
#         }

#
# class DeviceSettingViewModel(Base):
#     id: int
#     device_id: int
#     created_at: datetime
#     updated_at: datetime
#     email_alert: bool
#     body_temperature_threshold: float
#     uploadScreenshot: int

# class FasteyesDeviceInfoViewModel(Base):
#     uploadScreenshot: int
#     body_temperature_threshold: float


class FasteyesDeviceViewModel(Base):
    id: int
    group_id : int
    device_uuid: str
    name: str
    description: str = ""
    user_id: int
    created_at: datetime
    updated_at: datetime
    info: FasteyesDeviceSettingChangeModel

# class Device_and_Setting_ViewModel(UserBase):
#     Device: DeviceViewModel
#     Setting: DeviceSettingViewModel
