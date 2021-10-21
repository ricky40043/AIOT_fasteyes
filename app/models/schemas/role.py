# from typing import List
from typing import Optional

from pydantic import BaseModel, EmailStr

# from app.models.domain.item import item
from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class RolePostModel(Base):
    group_id: int
    device_model_id: int

    class Config:
        schema_extra = {
            "example": {
                "group_id": "1",
                "device_model_id": "1"
            }
        }


class RoleViewModel(Base):
    id: int
    group_id: int
    device_model_id: int
    created_at: datetime
