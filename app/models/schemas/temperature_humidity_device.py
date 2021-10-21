from typing import Optional

from pydantic import BaseModel

from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Temperature_humidityDevice_InfoModel(Base):
    serial_number: str
    interval_time: int
    alarm_temperature: float
    alarm_humidity: float
    battery_alarm: int


class Temperature_humidityDevicePostModel(Base):
    name: str
    info: Temperature_humidityDevice_InfoModel

    class Config:
        schema_extra = {
            "example": {
                "name": "Temperature_humidityDevice1",
                "info": {
                    "serial_number": "str",
                    "interval_time": "10",
                    "alarm_temperature": "67.9",
                    "alarm_humidity": "45.2",
                    "battery_alarm": "10"
                }
            }
        }


class Temperature_humidityDevicePatchModel(Base):
    id: int
    name: str
    info: Temperature_humidityDevice_InfoModel

    class Config:
        schema_extra = {
            "example": {
                "id": "1",
                "name": "Temperature_humidityDevice1",
                "info": {
                    "serial_number": "str",
                    "interval_time": "10",
                    "alarm_temperature": "67.9",
                    "alarm_humidity": "45.2",
                    "battery_alarm": "10"
                }
            }
        }


class Temperature_humidityDeviceViewModel(Base):
    id: int
    user_id: int
    group_id: int
    devicemodel_id: int
    name: str
    info: Temperature_humidityDevice_InfoModel
    created_at: datetime
    updated_at: datetime

