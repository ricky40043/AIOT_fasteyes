from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import FILE_PATH, DEFAULT_USER
from app.models.domain.Error_handler import UnicornException
from app.models.domain.area import area
from app.models.domain.area_user import area_user
from app.models.domain.user import user


def get_All_areas(db: Session):
    return db.query(area).all()


def get_email_alert_by_id(db: Session, area_id: int):
    return db.query(area).filter(area.id == area_id).first()


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


def get_users_by_email_alert_id(db: Session, email_alert_id: int):
    area_user_db_list = db.query(area_user.user_id).filter(area_user.email_alert_id == email_alert_id).all()
    return db.query(user).filter(user.id.in_(area_user_db_list)).all()


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