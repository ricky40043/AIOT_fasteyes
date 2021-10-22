from typing import Optional, List

from pydantic import BaseModel, EmailStr

from datetime import datetime

from app.models.schemas.staff import StaffViewModel


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class DepartmentPostModel(Base):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "123",
            }
        }


class DepartmentPatchModel(Base):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "123",
            }
        }


class DepartmentViewModel(Base):
    id: str
    name: str
    group_id: int
    created_at: datetime
    updated_at: datetime


class Department_staffViewModel(Base):
    id: str
    name: str
    group_id: int
    created_at: datetime
    updated_at: datetime
    member: List[StaffViewModel]

