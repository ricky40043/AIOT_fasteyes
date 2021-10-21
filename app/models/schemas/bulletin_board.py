# from typing import List
from typing import Optional

from pydantic import BaseModel, EmailStr

# from app.models.domain.item import item
from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Bulletin_boardPostModel(Base):
    text: str
    picture_name: str
    picture_or_text: bool

    class Config:
        schema_extra = {
            "example": {
                "text": "ricky",
                "picture_name": "picture_name",
                "picture_or_text": False
            }
        }


class Bulletin_boardPatchModel(Base):
    text: str
    picture_name: str
    picture_or_text: bool

    class Config:
        schema_extra = {
            "example": {
                "text": "ricky",
                "picture_name": "picture_name",
                "picture_or_text": False
            }
        }


class Bulletin_boardViewModel(Base):
    id: int
    group_id: int
    text: str
    picture_name: str
    picture_or_text: bool
    created_at: datetime
    updated_at: datetime
