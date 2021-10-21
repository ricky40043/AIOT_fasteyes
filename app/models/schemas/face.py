# from typing import List
from typing import Optional

from pydantic import BaseModel, EmailStr

# from app.models.domain.item import item
from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class FacePostModel(Base):
    id: int
    created_at: datetime
    updated_at: datetime
    face_uuid: str
    staff_id: int


class FaceViewModel(Base):
    id: int
    created_at: datetime
    updated_at: datetime
    face_uuid: str
    staff_id: int


class FaceFeatureViewModel(Base):
    id: int
    created_at: datetime
    updated_at: datetime
    raw_face_feature: str
    face_uuid: str
    staff_id: int
