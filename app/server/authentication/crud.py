import os
import shutil
from datetime import datetime
from random import random

from app.core.config import FILE_PATH, FASTEYES_OUTPUT_PATH
from app.models.domain.Error_handler import UnicornException, Error_handler
from app.models.domain.area import area
from app.models.domain.area_user import area_user
from app.models.domain.bulletin_board import bulletin_board
from app.models.domain.department import department
from app.models.domain.device import device
from app.models.domain.device_model import device_model
from app.models.domain.face import face
from app.models.domain.fasteyes_device import fasteyes_device
from app.models.domain.fasteyes_observation import fasteyes_observation
from app.models.domain.fasteyes_uuid import fasteyes_uuid
from app.models.domain.group import group
from app.models.domain.observation import observation
from app.models.domain.role import role
from app.models.domain.staff import staff
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


def clear_all_data(db: Session):
    db.begin()
    try:
        db.query(Error_handler).delete()

        db.query(area_user).delete()
        db.query(area).delete()

        db.query(face).delete()
        db.query(fasteyes_observation).delete()
        db.query(fasteyes_device).delete()
        db.query(fasteyes_uuid).delete()
        db.query(observation).delete()
        db.query(bulletin_board).delete()

        db.query(staff).delete()
        db.query(department).delete()
        db.query(device).delete()
        db.query(device_model).delete()

        db.query(role).delete()
        db.query(user).delete()
        db.query(group).delete()

        if os.path.exists(FILE_PATH):
            if os.path.exists(FILE_PATH + "observation"):
                shutil.rmtree(FILE_PATH + "observation")

            if os.path.exists(FILE_PATH + "face"):
                shutil.rmtree(FILE_PATH + "face")

        if os.path.exists(FASTEYES_OUTPUT_PATH):
            shutil.rmtree(FASTEYES_OUTPUT_PATH)

        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=clear_all_data.__name__, description=str(e), status_code=500)
    return "Done"
