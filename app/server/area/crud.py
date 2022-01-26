from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from app.core.config import FILE_PATH, DEFAULT_USER
from app.models.domain.Error_handler import UnicornException
from app.models.domain.area import area
from app.models.domain.area_user import area_user
from app.models.domain.user import user
import cv2
from starlette.responses import StreamingResponse
import io

from app.server.area import upload_image, delete_image


def get_All_areas(db: Session):
    return db.query(area).all()


def get_area_by_id(db: Session, area_id: int):
    return db.query(area).filter(area.id == area_id).first()


def get_area_by_group_id(db: Session, group_id: int):
    return db.query(area).filter(area.group_id == group_id).order_by(area.id).all()


def get_area_by_group_id_and_name(db: Session, group_id: int, name: str):
    return db.query(area).filter(area.group_id == group_id,
                                 area.name == name).first()


def create_area(db: Session, group_id: int, name: str):
    db.begin()
    try:
        db_area = area(group_id=group_id, name=name)
        db.add(db_area)
        db.commit()
        db.refresh(db_area)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_area.__name__, description=str(e), status_code=500)
    return db_area


def modify_area(db: Session, area_id: int, name: str, send_mail: bool):
    db_area = db.query(area).filter(area.id == area_id).first()
    db.begin()
    try:
        if name != -1:
            db_area.name = name
        if send_mail != -1:
            db_area.send_mail = send_mail
        db.commit()
        db.refresh(db_area)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_area.__name__, description=str(e), status_code=500)
    return db_area


def delete_area_by_id(db: Session, area_id: int):
    db.begin()
    try:
        area_db = db.query(area).filter(area.id == area_id).first()
        delete_image(area_db.group_id, area_id)
        db.delete(area_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_area_by_id.__name__, description=str(e), status_code=500)
    return "delete done"


def delete_area_by_group_id(db: Session, group_id: int):
    db.begin()
    try:
        db.query(area).filter(area.group_id == group_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_area_by_group_id.__name__, description=str(e), status_code=500)
    return "delete area Done"


###################################################################################################################

def get_All_area_users(db: Session):
    return db.query(area_user).all()


def get_users_by_area_id(db: Session, area_id: int):
    area_user_db_list = db.query(area_user).filter(area_user.area_id == area_id).all()
    area_user_id_list = [item.user_id for item in area_user_db_list]
    return db.query(user).filter(user.id.in_(area_user_id_list)).all()


def get_area_user_by_area_id_and_user_id(db: Session, area_id: int, user_id: int):
    return db.query(area_user).filter(area_user.area_id == area_id, area_user.user_id == user_id).first()


def create_area_user(db: Session, area_id: int, user_id: int):
    db.begin()
    try:
        db_area_user = area_user(area_id=area_id, user_id=user_id)
        db.add(db_area_user)
        db.commit()
        db.refresh(db_area_user)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_area_user.__name__, description=str(e), status_code=500)
    return db_area_user


def delete_area_user_by_area_id(db: Session, area_id: int):
    db.begin()
    try:
        db.query(area_user).filter(area_user.area_id == area_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_area_user_by_area_id.__name__, description=str(e), status_code=500)
    return "delete email_alert_user Done"


def delete_area_user_by_id(db: Session, area_user_id: int):
    db.begin()
    try:
        area_user_db = db.query(area_user).filter(area_user.id == area_user_id).first()
        db.delete(area_user_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_area_user_by_id.__name__, description=str(e), status_code=500)
    return "delete email_alert_user Done"


def delete_area_user_by_user_id(db: Session, user_id: int):
    db.begin()
    try:
        db.query(area_user).filter(area_user.user_id == user_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_area_user_by_user_id.__name__, description=str(e), status_code=500)
    return "delete email_alert_user Done"


def delete_area_user_by_area_id(db: Session, area_id: int):
    db.begin()
    try:
        db.query(area_user).filter(area_user.area_id == area_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_area_user_by_user_id.__name__, description=str(e), status_code=500)
    return "delete email_alert_user Done"


def delete_area_user_by_area_id_and_user_id(db: Session, area_id: int, user_id: int):
    db.begin()
    try:
        area_user_db = db.query(area_user).filter(area_user.area_id == area_id, area_user.user_id == user_id).first()
        db.delete(area_user_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_area_user_by_id.__name__, description=str(e), status_code=500)
    return "delete email_alert_user Done"


def get_area_image(db: Session, area_id):
    area_db = db.query(area).filter(area.id == area_id).first()

    if not area_db:
        raise UnicornException(name=get_area_image.__name__, description="area is not exist",
                               status_code=400)
    if not area_db.use_image:
        raise UnicornException(name=get_area_image.__name__, description="area use_image is false",
                               status_code=400)

    file_name = FILE_PATH + "area/group" + str(area_db.group_id) + "/area" + str(
        area_db.id) + ".jpg"
    cv2img = cv2.imread(file_name)

    if cv2img is None:
        raise UnicornException(name=get_area_image.__name__, description="area image not exist",
                               status_code=400)

    res, im_png = cv2.imencode(".jpg", cv2img)
    return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")


def upload_area_image(db: Session, area_id, image: UploadFile = File(...)):
    area_db = db.query(area).filter(area.id == area_id).first()
    db.begin()
    try:
        upload_image(area_db.group_id, area_db.id, image)
        area_db.use_image = True
        db.add(area_db)
        db.commit()
        db.refresh(area_db)

    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=upload_area_image.__name__, description=str(e), status_code=500)
    finally:
        image.file.close()
    return area_db


def delete_area_image(db: Session, area_id: int):
    area_db = db.query(area).filter(area.id == area_id).first()
    db.begin()
    try:
        area_db.use_image = False
        db.add(area_db)
        db.commit()
        db.refresh(area_db)

    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_area_image.__name__, description=str(e), status_code=500)
    return area_db
