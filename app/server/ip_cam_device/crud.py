# crud
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.domain.Error_handler import UnicornException
from app.models.domain.device import device
from app.models.schemas.ip_cam import Ip_CamPostModel, Ip_CamDevicePatchModel, Ip_CamInfoModel
from app.server.device.crud import check_name_repeate, check_serial_number_repeate
from app.server.device_model import DeviceType


def get_ip_cam_devices(db: Session, group_id: int):
    return db.query(device).filter(device.device_model_id == DeviceType.ip_cam.value, device.group_id == group_id).all()


def create_ip_cam_devices(db: Session, group_id: int, user_id: int,
                          name: str, serial_number: str, area: str, Ip_CamPost_create: Ip_CamInfoModel):
    check_name_repeate(db, name, DeviceType.ip_cam.value)
    check_serial_number_repeate(db, name, DeviceType.ip_cam.value)
    db.begin()
    try:
        device_db = device(name=name,
                           serial_number=serial_number,
                           area=area,
                           info=Ip_CamPost_create,
                           group_id=group_id,
                           user_id=user_id,
                           device_model_id=DeviceType.ip_cam.value)

        db.add(device_db)
        db.commit()
        db.refresh(device_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=get_ip_cam_devices.__name__, description=str(e), status_code=500)
    return device_db


def modify_ip_cam_devices(db: Session, group_id: int, device_id: int,
                          device_patch: Ip_CamDevicePatchModel):
    device_db = db.query(device).filter(device.group_id == group_id, device.device_model_id == DeviceType.ip_cam.value,
                                        device.id == device_id).first()

    check_name_repeate(db, device_patch.name, DeviceType.ip_cam.value)

    db.begin()
    try:
        temp_info = device_db.info.copy()  # dict 是 call by Ref. 所以一定要複製一份
        temp_info["ip"] = device_patch.info["ip"]
        temp_info["port"] = device_patch.info["port"]
        temp_info["username"] = device_patch.info["username"]
        temp_info["password"] = device_patch.info["password"]
        temp_info["stream_name"] = device_patch.info["stream_name"]
        device_db.info = temp_info
        device_db.name = device_patch.name
        device_db.area = device_patch.area
        db.commit()
        db.refresh(device_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modify_ip_cam_devices.__name__, description=str(e), status_code=500)
    return device_db


def delete_ip_cam_devices(db: Session, group_id: int, device_id: int):
    device_db = db.query(device).filter(device.group_id == group_id, device.device_model_id == DeviceType.ip_cam.value,
                                        device.id == device_id).first()
    if device_db is None:
        raise HTTPException(status_code=404, detail="device is not exist or is not in this group.")

    db.begin()
    try:
        db.delete(device_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_ip_cam_devices.__name__, description=str(e), status_code=500)
    return device_db
