# crud
from sqlalchemy.orm import Session

from app.models.domain.device import device
from fastapi import HTTPException


def get_All_devices(db: Session):
    return db.query(device).all()


def get_device_by_group_id_and_device_model_id(db: Session, group_id: int, device_model_id: int):
    return db.query(device).filter(device.group_id == group_id, device.device_model_id == device_model_id).all()


def get_device_by_id(db: Session, id: int):
    return db.query(device).filter(device.id == id).first()


def check_device_owner(db: Session, device_id: int, user_id: int):
    return db.query(device).filter(device.id == device_id, device.user_id == user_id).first()


def get_device_by_id_and_group_id(db: Session, id: int, group_id: int):
    return db.query(device).filter(device.id == id, device.group_id == group_id).first()


def check_name_repeate(db: Session, name: str, device_model_id: int):
    if db.query(device).filter(device.name == name, device.device_model_id == device_model_id).first():
        raise HTTPException(status_code=400, detail="device name is exist")


def get_device_by_name(db: Session, name: str, device_model_id: int, group_id: int):
    return db.query(device).filter(device.name == name, device.device_model_id == device_model_id,
                                   device.group_id == group_id).first()


def check_serial_number_repeate(db: Session, name: str, device_model_id: int):
    if db.query(device).filter(device.name == name, device.device_model_id == device_model_id).first():
        raise HTTPException(status_code=400, detail="device serial_number is exist")
