from typing import Optional

from pydantic import BaseModel

from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class NitrogenDevice_InfoModel(Base):
    interval_time: int
    Nitrogen_alarm: float
    Oxygen_alarm: float


class NitrogenDevicePostModel(Base):
    info: NitrogenDevice_InfoModel
    name: str
    area: str
    serial_number: str

    class Config:
        schema_extra = {
            "example": {
                "name": "NitrogenDevice1",
                "area": "room",
                "serial_number": "Erw34512",
                "info": {
                    "interval_time": "10",
                    "Nitrogen_alarm": "67.9",
                    "Oxygen_alarm": "45.2"
                }
            }
        }


class NitrogenDevicePatchModel(Base):
    info: NitrogenDevice_InfoModel
    name: str
    area: str

    class Config:
        schema_extra = {
            "example": {
                "name": "NitrogenDevice1",
                "area": "room",
                "info": {
                    "serial_number": "str",
                    "interval_time": "10",
                    "Nitrogen_alarm": "67.9",
                    "Oxygen_alarm": "45.2"
                }
            }
        }


# class NitrogenDeviceViewModel(Base):
#     id: int
#     user_id: int
#     group_id: int
#     devicemodel_id: int
#     name: str
#     info: NitrogenDevice_InfoModel
#     created_at: datetime
#     updated_at: datetime

