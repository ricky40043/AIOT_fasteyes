# from typing import List
from typing import Optional

from pydantic import BaseModel, EmailStr, Json

# from app.models.domain.item import item
from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class FasteyesPostOutputModel(Base):
    time: bool = True
    name: bool = True
    department: bool = True
    observation_ID: bool = True
    wear_mask: bool = True
    temperature: bool = True
    threshold_temperature: bool = True
    compensate_temperature: bool = True
    device_ID: bool = True
    result: bool = True
    output_time: bool = True

    class Config:
        schema_extra = {
            "example": {
                "time": True,
                "name": True,
                "department": True,
                "observation_ID": True,
                "wear_mask": True,
                "temperature": True,
                "threshold_temperature": True,
                "compensate_temperature": True,
                "device_ID": True,
                "result": True,
                "output_time": True
            }

        }


class FasteyesOutputViewModel(Base):
    id: int
    group_id: int
    time: bool
    name: bool
    department: bool
    observation_ID: bool
    wear_mask: bool
    temperature: bool
    threshold_temperature: bool
    compensate_temperature: bool
    device_ID: bool
    result: bool
    output_time: bool


class ObservationPatchViewModel(Base):
    time: Optional[bool] = True
    name: Optional[bool] = True
    department: Optional[bool] = True
    observation_ID: Optional[bool] = True
    wear_mask: Optional[bool] = True
    temperature: Optional[bool] = True
    threshold_temperature: Optional[bool] = True
    compensate_temperature: Optional[bool] = True
    device_ID: Optional[bool] = True
    result: Optional[bool] = True
    output_time: Optional[bool] = True

    class Config:
        schema_extra = {
            "example": {
                "time": True,
                "name": True,
                "department": True,
                "observation_ID": True,
                "wear_mask": True,
                "temperature": True,
                "threshold_temperature": True,
                "compensate_temperature": True,
                "device_ID": True,
                "result": True,
                "output_time": True
            }
        }
