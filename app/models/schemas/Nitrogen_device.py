from typing import Optional

from pydantic import BaseModel

from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class NitrogenDevice_InfoModel(Base):
    alarm_Nitrogen_lower_limit: float
    alarm_Nitrogen_upper_limit: float
    alarm_Oxygen_lower_limit: float
    alarm_Oxygen_upper_limit: float
    Nitrogen_Flow_lower_limit: float
    Nitrogen_Flow_upper_limit: float
    Nitrogen_content_Oxygen_lower_limit: float
    Nitrogen_content_Oxygen_upper_limit: float
    ip: str
    port: str
    position_x: Optional[int] = -1
    position_y: Optional[int] = -1

class NitrogenDevicePostModel(Base):
    info: NitrogenDevice_InfoModel
    name: str
    area: str
    serial_number: str

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "name": "NitrogenDevice1",
    #             "area": "room",
    #             "serial_number": "Erw34512",
    #             "info": {
    #                 "alarm_Nitrogen_lower_limit": 1,
    #                 "alarm_Nitrogen_upper_limit": 2,
    #                 "alarm_Oxygen_lower_limit": 1,
    #                 "alarm_Oxygen_upper_limit": 2
    #             }
    #         }
    #     }


class NitrogenDevicePatchModel(Base):
    info: NitrogenDevice_InfoModel
    name: str
    area: str
    serial_number: str

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "name": "NitrogenDevice1",
    #             "area": "room",
    #             "info": {
    #                 "alarm_Nitrogen_lower_limit": 1,
    #                 "alarm_Nitrogen_upper_limit": 2,
    #                 "alarm_Oxygen_lower_limit": 1,
    #                 "alarm_Oxygen_upper_limit": 2
    #             }
    #         }
    #     }
