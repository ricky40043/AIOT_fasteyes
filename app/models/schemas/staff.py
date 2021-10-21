# from typing import List
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# from app.models.domain.item import item


class Base(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class StaffInfoModel(Base):
    name: str
    email: EmailStr
    card_number: int
    national_id_number: str
    gender: int
    telephone_number: str = ""
    birthday: datetime


class StaffPostModel(Base):
    department_id: int
    serial_number: str
    info: StaffInfoModel
    status: int
    start_date: datetime

    class Config:
        schema_extra = {
            "example": {
                "department_id": "1",
                "serial_number": "400430012",
                "info":{
                    "name": "ricky",
                    "card_number": "254383204",
                    "email": "ricky@gmail.com",
                    "gender": 1,
                    "national_id_number": "string",
                    "birthday": "1993-01-01T00:00",
                    "telephone_number": "0987654321"
                },
                "start_date": "2002-12-25T00:00",
                "status": "1"
            }
        }


class StaffPatchModel(Base):
    name: Optional[str]
    serial_number: Optional[str]
    card_number: Optional[int]
    email: Optional[EmailStr]
    gender: Optional[str]
    national_id_number: Optional[str]
    birthday: Optional[datetime]
    department_id: Optional[int]
    telephone_number: Optional[str] = ""
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "name": "ricky",
                "serial_number": "1",
                "card_number": "2",
                "email": "ricky@gmail.com",
                "gender": "string",
                "national_id_number": "string",
                "birthday": "2002-12-25T00:00",
                "department_id": "1",
                "telephone_number": "0987654321",
                "start_date": "2002-12-25T00:00",
                "end_date": "2002-12-25T00:00",
                "status": "1",
            }
        }


class StaffViewModel(Base):
    id: int
    department_id: int
    group_id: int
    serial_number: str
    info: StaffInfoModel
    status: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
