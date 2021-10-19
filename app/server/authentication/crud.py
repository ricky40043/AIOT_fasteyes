import os
import shutil
from datetime import datetime
from random import random

from app.models.domain.Error_handler import UnicornException
from app.models.domain.user import user
from app.server.authentication import create_random_password
from app.server.user.crud import get_password_hash

from fastapi import HTTPException
from sqlalchemy.orm import Session


# def change_user_level_to_hr(db: Session, user_id: int, level: int):
#     user_db = db.query(user).filter(user.id == user_id).first()
#     if level < 1 or level > 5:
#         raise UnicornException(name=change_user_level_to_hr.__name__, description="權限 level 請輸入 1~5", status_code=400)
#     db.begin()
#     try:
#         user_db.level = level
#         user_db.updated_at = datetime.now()
#         db.commit()
#         db.refresh(user_db)
#     except Exception as e:
#         db.rollback()
#         print(str(e))
#         raise UnicornException(name=change_user_level_to_hr.__name__, description=str(e), status_code=500)
#     return user_db
#
#


def check_user_email_enable(db: Session, user_email: str):
    user_db = db.query(user).filter(user.email == user_email).first()
    if user_db.is_enable:
        raise HTTPException(status_code=202, detail="user 已啟用了")


def set_user_enable(db: Session, user_email: str):
    user_db = db.query(user).filter(user.email == user_email).first()
    db.begin()
    try:
        user_db.is_enable = True
        user_db.updated_at = datetime.now()
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=set_user_enable.__name__, description=str(e), status_code=500)
    return user_db


def create_and_set_user_password(db: Session, user_email: str):
    user_db = db.query(user).filter(user.email == user_email).first()
    password = create_random_password()
    hashed_password = get_password_hash(password)

    db.begin()
    try:
        user_db.password = hashed_password
        user_db.updated_at = datetime.now()
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_and_set_user_password.__name__, description=str(e), status_code=500)
    return password

# def clear_all_data(db: Session):
#     db.begin()
#     try:
#         db.query(observation).delete()
#         # db.query(face_feature).delete()
#         db.query(face).delete()
#         db.query(deviceSetting).delete()
#         db.query(device).delete()
#         db.query(hardwareUuid).delete()
#         db.query(deviceUuid).delete()
#         db.query(staff).delete()
#         db.query(department).delete()
#         db.query(company).delete()
#         db.query(user).delete()
#
#         if os.path.exists(file_path):
#             if os.path.exists(file_path + "observation"):
#                 shutil.rmtree(file_path + "observation")
#
#             if os.path.exists(file_path + "face"):
#                 shutil.rmtree(file_path + "face")
#
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         print(str(e))
#         raise UnicornException(name=clear_all_data.__name__, description=str(e), status_code=500)
#     return "Done"
