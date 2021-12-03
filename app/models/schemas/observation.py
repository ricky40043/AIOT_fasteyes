# from typing import List
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Json

# from app.models.domain.item import item
from datetime import datetime, time, date as Date


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ObservationPostModel(Base):
    info: dict

    class Config:
        schema_extra = {
            "example": {
                "info": {
                }
            }
        }


class ObservationViewModel(Base):
    id: int
    group_id: int
    device_id: int
    device_model_id: int
    info: dict
    created_at: datetime
    updated_at: datetime


class ObservationPatchViewModel(Base):
    group_id: int
    device_id: int
    devicemodel_id: int
    info: dict

    # class Config:
    #     schema_extra = {
    #         "example": {
    #         }
    #     }
