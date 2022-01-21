# crud
from typing import Optional

from sqlalchemy.orm import Session

from app.models.domain.device import device
from fastapi import HTTPException


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
