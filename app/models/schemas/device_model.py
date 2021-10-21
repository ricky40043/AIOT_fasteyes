# from typing import List
from typing import Optional

from pydantic import BaseModel, EmailStr

# from app.models.domain.item import item
from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class DevicePostModel(Base):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "ricky"
            }
        }


class DevicePatchModel(Base):
    id: int
    name: str

    class Config:
        schema_extra = {
            "example": {
                "id": "1",
                "name": "ricky"
            }
        }


class DeviceViewModel(Base):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
