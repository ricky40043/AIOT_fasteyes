# crud
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.domain.Error_handler import UnicornException
from app.models.domain.device import device
from app.models.schemas.Nitrogen_device import NitrogenDevicePostModel, \
    NitrogenDevicePatchModel, NitrogenDevice_InfoModel
from app.server.device.crud import check_name_repeate, check_serial_number_repeate
from app.server.device_model import DeviceType


def get_Nitrogen_devices(db: Session, group_id: int):
    return db.query(device).filter(device.device_model_id == DeviceType.Nitrogen.value, device.group_id == group_id).all()


def create_Nitrogen_devices(db: Session, group_id: int, user_id: int,
                            name: str, serial_number: str, area: str, NitrogenDevice_create: NitrogenDevice_InfoModel):

    check_name_repeate(db, name, DeviceType.Nitrogen.value)
    check_serial_number_repeate(db, name, DeviceType.Nitrogen.value)

    db.begin()
    try:
        device_db = device(name=name,
                           serial_number=serial_number,
                           area=area,
                           info=NitrogenDevice_create,
                           group_id=group_id,
                           user_id=user_id,
                           device_model_id=DeviceType.Nitrogen.value)

        db.add(device_db)
        db.commit()
        db.refresh(device_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_Nitrogen_devices.__name__, description=str(e), status_code=500)
    return device_db


def modify_Nitrogen_devices(db: Session, group_id: int, device_id: int,
                                        device_patch: NitrogenDevicePatchModel):
    device_db = db.query(device).filter(device.group_id == group_id, device.device_model_id == DeviceType.Nitrogen.value,
                                        device.id == device_id).first()
    check_name_repeate(db, device_patch.name, DeviceType.Nitrogen.value)

    db.begin()
    try:
        temp_info = device_db.info.copy()  # dict 是 call by Ref. 所以一定要複製一份
        temp_info["interval_time"] = device_patch.info["interval_time"]
        temp_info["Nitrogen_alarm"] = device_patch.info["Nitrogen_alarm"]
        temp_info["Oxygen_alarm"] = device_patch.info["Oxygen_alarm"]
        device_db.info = temp_info
        device_db.name = device_patch.name
        device_db.area = device_patch.area
        db.commit()
        db.refresh(device_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modify_Nitrogen_devices.__name__, description=str(e), status_code=500)
    return device_db


def delete_Nitrogen_devices(db: Session, group_id: int, device_id: int):
    device_db = db.query(device).filter(device.group_id == group_id, device.device_model_id == DeviceType.Nitrogen.value,
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
        raise UnicornException(name=delete_Nitrogen_devices.__name__, description=str(e), status_code=500)
    return device_db


