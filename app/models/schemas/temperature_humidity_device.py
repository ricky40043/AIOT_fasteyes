from typing import Optional

from pydantic import BaseModel

from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Temperature_humidityDevice_InfoModel(Base):
    interval_time: int
    alarm_temperature_upper_limit: float
    alarm_temperature_lower_limit: float
    alarm_humidity_upper_limit: float
    alarm_humidity_lower_limit: float
    compensate_temperature: float
    compensate_humidity: float
    battery_alarm: int


class Temperature_humidityDevicePostModel(Base):
    info: Temperature_humidityDevice_InfoModel
    name: str
    serial_number: str
    area: str

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "name": "1705EF",
    #             "serial_number": "Temperature_humidityDevice1",
    #             "area": "room",
    #             "info": {
    #                 "interval_time": "10",
    #                 "alarm_temperature": "67.9",
    #                 "alarm_humidity": "45.2",
    #                 "battery_alarm": "10"
    #             }
    #         }
    #     }


class Temperature_humidityDevicePatchModel(Base):
    info: Temperature_humidityDevice_InfoModel
    name: str
    area: str
    serial_number: str

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "name": "Temperature_humidityDevice1",
    #             "area": "room1",
    #             "info": {
    #                 "interval_time": "10",
    #                 "alarm_temperature": "67.9",
    #                 "alarm_humidity": "45.2",
    #                 "battery_alarm": "10"
    #             }
    #         }
    #     }
