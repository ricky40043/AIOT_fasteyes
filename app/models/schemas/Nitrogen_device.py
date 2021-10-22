from typing import Optional

from pydantic import BaseModel

from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class NitrogenDevice_InfoModel(Base):
    serial_number: str
    interval_time: int
    Nitrogen_alarm: float
    Oxygen_alarm: float


class NitrogenDevicePostModel(Base):
    name: str
    info: NitrogenDevice_InfoModel

    class Config:
        schema_extra = {
            "example": {
                "name": "NitrogenDevice1",
                "info": {
                    "serial_number": "str",
                    "interval_time": "10",
                    "Nitrogen_alarm": "67.9",
                    "Oxygen_alarm": "45.2"
                }
            }
        }


class NitrogenDevicePatchModel(Base):
    id: int
    name: str
    info: NitrogenDevice_InfoModel

    class Config:
        schema_extra = {
            "example": {
                "id": "1",
                "name": "Temperature_humidityDevice1",
                "info": {
                    "serial_number": "str",
                    "interval_time": "10",
                    "Nitrogen_alarm": "67.9",
                    "Oxygen_alarm": "45.2"
                }
            }
        }


class NitrogenDeviceViewModel(Base):
    id: int
    user_id: int
    group_id: int
    devicemodel_id: int
    name: str
    info: NitrogenDevice_InfoModel
    created_at: datetime
    updated_at: datetime

