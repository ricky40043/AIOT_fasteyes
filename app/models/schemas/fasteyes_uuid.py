# from typing import List
from typing import Optional

from pydantic import BaseModel, EmailStr

from datetime import datetime



class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class FasteyesUuidSearchModel(Base):
    hardwareuuid: str

    class Config:
        schema_extra = {
            "example": {
                "hardwareuuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        }


class FasteysesUuidPostModel(Base):
    creator: str
    product_number: Optional[str]


class FasteyesUuidChangeModel(Base):
    hardware_uuid: str
    device_uuid: str

    class Config:
        schema_extra = {
            "example": {
                "hardware_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "device_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        }


class FasteysesUuidViewModel(Base):
    id: int
    uuid: str
    hardware_uuid: str
    creator: str
    product_number: Optional[str]
    is_registered: bool
    registered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# class HardwareUuid_and_DeviceViewModel(Base):
#     Hardware: HardwareUuidViewModel
#     Device: Optional[DeviceViewModel]
