# crud
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.domain.Error_handler import UnicornException
from app.models.domain.device import device
from fastapi import HTTPException

from app.server.device_model import DeviceType


def get_All_devices(db: Session):
    return db.query(device).all()


def get_device_by_group_id_and_device_model_id(db: Session, group_id: int, device_model_id: int,
                                               area: Optional[str] = ""):
    if area == "":
        return db.query(device).filter(device.group_id == group_id, device.device_model_id == device_model_id).all()
    else:
        return db.query(device).filter(device.group_id == group_id, device.device_model_id == device_model_id,
                                       device.area == area).all()


def get_device_by_id(db: Session, id: int):
    return db.query(device).filter(device.id == id).first()


def check_device_owner(db: Session, device_id: int, user_id: int):
    return db.query(device).filter(device.id == device_id, device.user_id == user_id).first()


def get_device_by_id_and_group_id(db: Session, id: int, group_id: int):
    return db.query(device).filter(device.id == id, device.group_id == group_id).first()


def check_name_repeate(db: Session, name: str, device_model_id: int, group_id: int, device_id: Optional[int] = -1):
    device_by_name = get_device_by_name(db, name, device_model_id, group_id)
    if device_by_name:
        if device_by_name.id != device_id:
            raise HTTPException(status_code=400, detail="device name is exist")


def get_device_by_name(db: Session, name: str, device_model_id: int, group_id: int):
    return db.query(device).filter(device.name == name, device.device_model_id == device_model_id,
                                   device.group_id == group_id).first()


def check_serial_number_repeate(db: Session, serial_number: str, device_model_id: int, group_id: int,
                                device_id: Optional[int] = -1):
    device_db = db.query(device).filter(device.serial_number == serial_number,
                                        device.device_model_id == device_model_id,
                                        device.group_id == group_id).first()
    if device_db:
        if device_db.id != device_id:
            raise HTTPException(status_code=400, detail="device serial_number is exist")


def modify_device_position(db: Session, group_id: int, device_model_id: int, device_id: int, position_x: int, position_y: int):
    device_db = db.query(device).filter(device.group_id == group_id,
                                        device.device_model_id == device_model_id,
                                        device.id == device_id).first()

    db.begin()
    try:
        temp_info = device_db.info.copy()  # dict 是 call by Ref. 所以一定要複製一份
        temp_info["position_x"] = position_x
        temp_info["position_y"] = position_y
        device_db.info = temp_info
        device_db.updated_at = datetime.now()
        db.commit()
        db.refresh(device_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modify_device_position.__name__, description=str(e), status_code=500)
    return device_db
