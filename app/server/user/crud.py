# crud
import json
import uuid
from datetime import datetime
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.domain.department import department
from app.models.domain.face import face
from app.models.domain.fasteyes_device import fasteyes_device
from app.models.domain.fasteyes_observation import fasteyes_observation
from app.models.domain.group import group
from app.models.domain.staff import staff
from app.server.authentication import Authority_Level
from app.models.domain.Error_handler import UnicornException
from app.models.domain.user import user
from app.models.schemas.user import UserPatchPasswordViewModel, UserPostViewModel, UserPatchInfoModel, \
    UserChangeSettingModel
from app.server.fasteyes_uuid.crud import get_hardwareUuid_by_deviceuuid
from app.server.staff.crud import get_staff_by_id

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def get_All_users(db: Session):
    return db.query(user).all()


def get_users_in_group(db: Session, group_id: int):
    return db.query(user).filter(user.group_id == group_id).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(user).filter(user.id == user_id).first()


def get_UserExists(db: Session, user_email: str):
    return db.query(user).filter(user.email == user_email).first()


def modefy_User(db: Session, user_db: user, userPatch: UserPatchInfoModel):
    db.begin()
    try:
        user_db.name = userPatch.name
        # user_db.address = userPatch.address
        # user_db.country = userPatch.country
        # user_db.telephone_number = userPatch.telephone_number
        # user_db.usage = userPatch.usage
        # user_db.company_scale = userPatch.company_scale
        # user_db.industry = userPatch.industry
        user_db.updated_at = datetime.now()
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modefy_User.__name__, description=str(e), status_code=500)
    return user_db


def change_user_setting(db: Session, user_id: int, userPatch: UserChangeSettingModel):
    user_db = db.query(user).filter(user.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="user not exist")
    db.begin()
    try:
        temp_info = user_db.info.copy()  # dict 是 call by Ref. 所以一定要複製一份
        if userPatch.language != -1:
            temp_info["language"] = userPatch.language
        if userPatch.email_alert != -1:
            temp_info["email_alert"] = userPatch.email_alert

        user_db.updated_at = datetime.now()
        user_db.info = temp_info
        db.commit()
        db.refresh(user_db)


    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=change_user_setting.__name__, description=str(e), status_code=500)
    return user_db


def change_user_verify_code_enable(db: Session, user_id: int, verify_code_enable: bool):
    user_db = db.query(user).filter(user.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="user not exist")
    db.begin()
    try:
        user_db.verify_code_enable = verify_code_enable
        db.commit()
        db.refresh(user_db)

    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=change_user_setting.__name__, description=str(e), status_code=500)
    return user_db


def modefy_User_Password(db: Session, user_id: int, userPatch: UserPatchPasswordViewModel):
    user_db = db.query(user).filter(user.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="user not exist")
    db.begin()
    try:
        hashed_password = get_password_hash(userPatch.new_password)
        user_db.password = hashed_password
        user_db.updated_at = datetime.now()
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modefy_User_Password.__name__, description=str(e), status_code=500)
    return user_db


def check_Email_Exist(db: Session, email: str):
    user_db = db.query(user).filter(user.email == email).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="Email does not exist")
    return user_db


def update_UserStatus(db: Session, user_id: int, status: bool):
    user_db = db.query(user).filter(user.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="user not exist")
    db.begin()
    try:
        user_db.is_enable = status
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=update_UserStatus.__name__, description=str(e), status_code=500)
    return user_db


def update_User_Verify_code_enable(db: Session, user_id: int, verify_code_enable: bool):
    user_db = db.query(user).filter(user.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="user not exist")
    db.begin()
    try:
        user_db.verify_code_enable = verify_code_enable
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=update_UserStatus.__name__, description=str(e), status_code=500)
    return user_db


def Create_User(db: Session, user_create: UserPostViewModel, group_id: int,
                level: int = Authority_Level.HRAccess.value, is_enable: bool = False):
    db.begin()
    try:
        hashed_password = get_password_hash(user_create.password)
        user_create.password = hashed_password
        db_user = user(**user_create.dict(),
                       group_id=group_id,
                       is_enable=is_enable,
                       level=level)
        db.add(db_user)
        # print("add Done")
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=Create_User.__name__, description=str(e), status_code=500)
    return db_user


def check_User_Exist(db: Session, user_id: int):
    db_user = db.query(user).filter(user.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="user is not exist")
    return db_user


def delete_user_By_User_Id(db: Session, user_id: int):
    db.begin()
    try:
        db_user = db.query(user).filter(user.id == user_id).first()
        db.delete(db_user)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_user_By_User_Id.__name__, description=str(e), status_code=500)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(user).filter(user.email == email).first()


def get_user_by_name(db: Session, name: str):
    return db.query(user).filter(user.name == name).first()


def get_user_by_name_in_group(db: Session, name: str, group_id):
    return db.query(user).filter(user.name == name, user.group_id == group_id).first()


def check_user_owner(db: Session, user_id: int, group_id: int):
    if not db.query(user).filter(user.id == user_id, user.group_id == group_id).first():
        raise HTTPException(status_code=404, detail="user is not in this group")


def change_user_level(db: Session, user_id: int, level: int):
    user_db = db.query(user).filter(user.id == user_id).first()
    if level < 2 or level > 4:
        raise UnicornException(name=change_user_level.__name__, description="權限 level 請輸入 2~4", status_code=400)
    db.begin()
    try:
        user_db.level = level
        user_db.updated_at = datetime.now()
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=change_user_level.__name__, description=str(e), status_code=500)
    return user_db


def delete_group_by_group_id(db: Session, group_id: int):
    db.begin()
    try:
        fasteyes_device_db_list = db.query(fasteyes_device).filter(fasteyes_device.group_id == group_id).all()
        for each_fasteyes_device_db in fasteyes_device_db_list:
            fasteyes_uuid = get_hardwareUuid_by_deviceuuid(db, each_fasteyes_device_db.device_uuid)
            fasteyes_uuid.is_registered = False
            fasteyes_uuid.hardware_uuid = None

        db.query(fasteyes_observation).filter(fasteyes_observation.group_id == group_id).delete()
        db.query(fasteyes_device).filter(fasteyes_device.group_id == group_id).delete()
        db.query(face).filter(face.group_id == group_id).delete()
        db.query(staff).filter(staff.group_id == group_id).delete()
        db.query(department).filter(department.group_id == group_id).delete()
        db.query(user).filter(user.group_id == group_id).delete()
        db.query(group).filter(group.id == group_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_group_by_group_id.__name__, description=str(e), status_code=500)
    return "delete Done"


def delete_user_by_user_id(db: Session, user_id: int, transfer_user_id: int):
    db.begin()
    try:
        staff_db_list = db.query(staff).filter(staff.user_id == user_id).all()
        for each_staff_db in staff_db_list:
            staff_db = get_staff_by_id(db,each_staff_db.id)
            staff_db.user_id = transfer_user_id
        user_db = db.query(user).filter(user.id == user_id).first()
        db.delete(user_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_user_by_user_id.__name__, description=str(e), status_code=500)
    return user_db
