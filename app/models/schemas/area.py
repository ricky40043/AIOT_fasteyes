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
    use_image: Optional[bool] = False


class Area_UsersViewModel(Base):
    id: int
    created_at: datetime
    area_id: int
    user_id: int

#
# class Area_patch_Model(Base):
#     send_mail: Optional[bool] = -1
#     name: Optional[str] = -1
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "send_mail": False,
#                 "name": "1F",
#             }
#         }
