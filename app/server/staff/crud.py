# crud
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import FILE_PATH, DEFAULT_USER
from app.models.domain.Error_handler import UnicornException
from app.models.domain.staff import staff
from app.models.schemas.staff import StaffPostModel, StaffPatchModel


def get_All_staffs(db: Session):
    return db.query(staff).all()


def get_staff_by_id(db: Session, staff_id: int):
    return db.query(staff).filter(staff.id == staff_id).first()


def check_staff_id_by_group_id(db: Session, staff_id: int, group_id: int):
    return db.query(staff).filter(staff.group_id == group_id, staff.id == staff_id).first()


def get_staff_by_SerialNumber(db: Session, SerialNumber: str, group_id: int) -> object:
    return db.query(staff).filter(staff.group_id == group_id, staff.serial_number == SerialNumber).first()


def get_staff_by_group(db: Session, group_id: int, status: Optional[int] = -1, department_id: Optional[int] = -1):
    if status == -1 and department_id == -1:
        return db.query(staff).filter(staff.group_id == group_id).order_by(staff.id).all()
    elif status != -1 and department_id != -1:
        return db.query(staff).filter(staff.group_id == group_id).filter(staff.status == status,
                                                                         staff.department_id == department_id).order_by(
            staff.id).all()
    else:
        if status != -1:
            return db.query(staff).filter(staff.group_id == group_id).filter(staff.status == status).order_by(
                staff.id).all()
        else:
            return db.query(staff).filter(staff.group_id == group_id).filter(
                staff.department_id == department_id).order_by(staff.id).all()


def get_user_by_serveral_number_in_group(db: Session, serial_number: str, group_id: int):
    return db.query(staff).filter(staff.group_id == group_id, staff.serial_number == serial_number).first()


def create_staff(db: Session, StaffIn: StaffPostModel, user_id: int, group_id: int):
    db.begin()
    try:
        StaffIn.info.birthday = str(StaffIn.info.birthday)
        db_staff = staff(**StaffIn.dict(), user_id=user_id, group_id=group_id)
        db.add(db_staff)
        db.commit()
        db.refresh(db_staff)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_staff.__name__, description=str(e), status_code=500)
    return db_staff


def modefy_Staff_Info(db: Session, staff_id: int, staffPatch: StaffPatchModel):
    Staff_db = db.query(staff).filter(staff.id == staff_id).first()
    db.begin()
    try:
        temp_info = Staff_db.info.copy()  # dict 是 call by Ref. 所以一定要複製一份
        print(staffPatch.dict())
        if staffPatch.name:
            temp_info["name"] = staffPatch.name
        if staffPatch.gender:
            temp_info["gender"] = staffPatch.gender
        if staffPatch.card_number:
            temp_info["card_number"] = staffPatch.card_number
        if staffPatch.telephone_number:
            temp_info["telephone_number"] = staffPatch.telephone_number
        if staffPatch.email:
            temp_info["email"] = staffPatch.email
        if staffPatch.national_id_number:
            temp_info["national_id_number"] = staffPatch.national_id_number
        if staffPatch.birthday:
            temp_info["birthday"] = str(staffPatch.birthday)
        if staffPatch.department_id:
            Staff_db.department_id = staffPatch.department_id
        if staffPatch.start_date:
            Staff_db.start_date = staffPatch.start_date
        if staffPatch.end_date:
            Staff_db.end_date = staffPatch.end_date
        Staff_db.status = staffPatch.status
        Staff_db.updated_at = datetime.now()
        Staff_db.info = temp_info
        db.commit()
        db.refresh(Staff_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modefy_Staff_Info.__name__, description=str(e), status_code=500)
    return Staff_db


def delete_Staff_by_Staff_id(db: Session, staff_id: int):
    Staff_db = db.query(staff).filter(staff.id == staff_id).first()
    db.begin()
    try:
        db.delete(Staff_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_Staff_by_Staff_id.__name__, description=str(e), status_code=500)
    return Staff_db


def get_default_staff_id(db: Session):
    return db.query(staff).filter(staff.serial_number == DEFAULT_USER).first()
