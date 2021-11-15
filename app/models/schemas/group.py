# from typing import List
from typing import Optional

from pydantic import BaseModel, EmailStr

# from app.models.domain.item import item
from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class GroupPostModel(Base):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "ricky"
            }
        }


class GroupPatchModel(Base):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "ricky"
            }
        }


class GroupViewModel(Base):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
