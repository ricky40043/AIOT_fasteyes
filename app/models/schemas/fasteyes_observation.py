# from typing import List
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Json

# from app.models.domain.item import item
from datetime import datetime, time , date as Date


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ObservationInfoModel(Base):
    wear_mask: int
    temperature: float
    threshold_temperature: float
    compensate_temperature: float


class ObservationPostModel(Base):
    phenomenon_time: datetime
    result: bool
    info: ObservationInfoModel
    image_name: str
    staff_id: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "phenomenon_time": "1994-05-27T00:00",
                "result": False,
                "image_name": "image_name",
                "staff_id": 5,
                "info": {
                    "wear_mask": 1,
                    "temperature": 37.3,
                    "threshold_temperature": 37.5,
                    "compensate_temperature": 0,
                }

            }
        }


class ObservationViewModel(Base):
    id: int
    group_id: int
    fasteyes_device_id: int
    phenomenon_time: datetime
    result: bool
    info: ObservationInfoModel
    image_name: str
    created_at: datetime
    updated_at: datetime


class ObservationPatchViewModel(Base):
    staff_id: int

    class Config:
        schema_extra = {
            "example": {
                "staff_id": 3
            }
        }


class attendancePostModel(Base):
    working_time_1: time
    working_time_2: time
    working_time_off_1: time
    working_time_off_2: time


class attendance_dateModel(Base):
    staff_id: int
    punch_in: Optional[datetime]
    punch_out: Optional[datetime]
    # staff_name: str
    # staff_serial_number: str
    punch_in_temperature: Optional[float]
    punch_out_temperature: Optional[float]
    punch_in_temperature_result: Optional[bool]
    punch_out_temperature_result: Optional[bool]


class attendanceViewModel(Base):
    date: Date
    attendance: List[attendance_dateModel]
