# crud
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.models.domain.Error_handler import UnicornException
from app.models.domain.fasteyes_device import fasteyes_device
from app.models.domain.fasteyes_uuid import fasteyes_uuid
from app.models.schemas.fasteyes_device import FasteyesDeviceViewModel, FasteyesDeviceSettingChangeModel, \
    FasteyesDevicePatchModel
from app.server.fasteyes_uuid.crud import get_hardwareUuid_by_deviceuuid


def get_All_fasteyes_devices(db: Session):
    return db.query(fasteyes_device).all()


def get_fasteyes_device_by_id(db: Session, device_id: int):
    return db.query(fasteyes_device).filter(fasteyes_device.id == device_id).first()


def get_fasteyes_device_by_uuid(db: Session, device_uuid: str):
    return db.query(fasteyes_device).filter(fasteyes_device.device_uuid == device_uuid).first()


def get_group_fasteyes_devices(db: Session, group_id: int):
    return db.query(fasteyes_device).filter(fasteyes_device.group_id == group_id).all()


def check_device_exist_by_deviceuuid(db: Session, device_uuid: str):
    Device_db = db.query(fasteyes_device).filter(fasteyes_device.device_uuid == device_uuid).first()
    if Device_db:
        raise UnicornException(name=check_device_exist_by_deviceuuid.__name__,
                               description="device is registed ", status_code=400)
    return True


def regist_device(db: Session, device_in: FasteyesDeviceViewModel, user_id: int, group_id: int):
    db.begin()
    try:
        fasteyes_uuid_db = get_hardwareUuid_by_deviceuuid(db, device_in.device_uuid)
        fasteyes_uuid_db.updated_at = datetime.now()
        fasteyes_uuid_db.registered_at = datetime.now()
        fasteyes_uuid_db.is_registered = True
        info = {"", }

        fasteyes_device_db = fasteyes_device(**device_in.dict(), user_id=user_id, group_id=group_id)
        db.add(fasteyes_device_db)
        db.commit()
        db.refresh(fasteyes_device_db)
    except Exception as e:
        db.rollback()
        raise UnicornException(name=regist_device.__name__, description=str(e), status_code=500)
    return fasteyes_device_db


def check_device_owner(db: Session, fasteyes_device_id: int, user_id: int):
    return db.query(fasteyes_device).filter(fasteyes_device.id == fasteyes_device_id,
                                            fasteyes_device.user_id == user_id).first()


def change_fasteyes_device_data(db: Session, fasteyes_device_id,
                                davice_Patch: FasteyesDevicePatchModel):
    fasteyes_device_db = db.query(fasteyes_device).filter(fasteyes_device.id == fasteyes_device_id).first()
    if fasteyes_device_db is None:
        raise HTTPException(status_code=404, detail="fasteyes_device is not exist")
    db.begin()
    try:
        fasteyes_device_db.name = davice_Patch.name
        fasteyes_device_db.description = davice_Patch.description
        fasteyes_device_db.updated_at = datetime.now()
        db.commit()
        db.refresh(fasteyes_device_db)

    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=change_fasteyes_device_setting.__name__, description=str(e), status_code=500)
    return fasteyes_device_db


def change_fasteyes_device_setting(db: Session, fasteyes_device_id,
                                   davice_Patch: FasteyesDeviceSettingChangeModel):
    fasteyes_device_db = db.query(fasteyes_device).filter(fasteyes_device.id == fasteyes_device_id).first()
    if fasteyes_device_db is None:
        raise HTTPException(status_code=404, detail="fasteyes_device is not exist")
    db.begin()
    try:
        temp_info = fasteyes_device_db.info.copy()  # dict 是 call by Ref. 所以一定要複製一份
        if davice_Patch.uploadScreenshot != -1:
            temp_info["uploadScreenshot"] = davice_Patch.uploadScreenshot
        if davice_Patch.body_temperature_threshold != -1:
            temp_info["body_temperature_threshold"] = davice_Patch.body_temperature_threshold
        fasteyes_device_db.updated_at = datetime.now()
        fasteyes_device_db.info = temp_info
        db.commit()
        db.refresh(fasteyes_device_db)

    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=change_fasteyes_device_setting.__name__, description=str(e), status_code=500)
    return fasteyes_device_db


def delete_fasteyes_device_by_id(db: Session, device_id: int):
    fasteyes_observation_db = db.query(fasteyes_device).filter(fasteyes_device.id == device_id).first()
    db.begin()
    try:
        db.delete(fasteyes_observation_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_fasteyes_device_by_id.__name__, description=str(e), status_code=500)
    return fasteyes_observation_db