# from typing import List
from typing import Optional

from pydantic import BaseModel, EmailStr

from datetime import datetime


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class Area_ViewModel(Base):
    id: int
    created_at: datetime
    group_id: int
    name: str
    send_mail: bool


class Area_UsersViewModel(Base):
    id: int
    created_at: datetime
    area_id: int
    user_id: int
