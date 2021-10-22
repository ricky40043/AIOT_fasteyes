# crud
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.domain.Error_handler import UnicornException
from app.models.domain.fasteyes_uuid import fasteyes_uuid
import uuid

from app.models.schemas.fasteyes_uuid import FasteysesUuidPostModel, FasteyesUuidChangeModel, FasteyesUuidSearchModel


def get_All_fasteyes_uuids(db: Session):
    return db.query(fasteyes_uuid).all()


def get_hardware_uuid(db: Session, hardware_uuid: str):
    return db.query(fasteyes_uuid).filter(fasteyes_uuid.hardware_uuid == hardware_uuid).first()


def get_hardwareUuid_by_deviceuuid(db: Session, device_uuid: str):
    return db.query(fasteyes_uuid).filter(fasteyes_uuid.uuid == device_uuid).first()


def create_fasteyes_uuid(db: Session, fasteyes_uuid_create: FasteysesUuidPostModel):
    device_uuid = uuid.uuid4()
    # 檢查UUID是否有了
    while True:
        if db.query(fasteyes_uuid).filter(fasteyes_uuid.uuid == str(device_uuid)).first():
            device_uuid = uuid.uuid4()
        else:
            break

    hardware_uuid = uuid.uuid4()
    # 檢查UUID是否有了
    while True:
        if db.query(fasteyes_uuid).filter(fasteyes_uuid.hardware_uuid == str(hardware_uuid)).first():
            hardware_uuid = uuid.uuid4()
        else:
            break

    db.begin()
    try:
        DeviceUuid_db = fasteyes_uuid(**fasteyes_uuid_create.dict(),
                                      uuid=device_uuid, hardware_uuid=hardware_uuid)
        db.add(DeviceUuid_db)
        db.commit()
        db.refresh(DeviceUuid_db)
    except Exception as e:
        db.rollback()
        raise UnicornException(name=create_fasteyes_uuid.__name__, description=str(e), status_code=500)

    return DeviceUuid_db


def change_hardwareUuid(db: Session, fasteyes_uuid_patch: FasteyesUuidChangeModel):
    print(fasteyes_uuid_patch.device_uuid)
    fasteyes_uuid_db = db.query(fasteyes_uuid).filter(fasteyes_uuid.uuid == fasteyes_uuid_patch.device_uuid).first()
    if not fasteyes_uuid_db:
        raise HTTPException(status_code=404, detail="fasteyes_uuid not found")

    db.begin()
    try:
        fasteyes_uuid_db.hardware_uuid = fasteyes_uuid_patch.hardware_uuid
        db.commit()
        db.refresh(fasteyes_uuid_db)

    except Exception as e:
        db.rollback()
        raise UnicornException(name=change_hardwareUuid.__name__, description=str(e), status_code=500)

    return fasteyes_uuid_db


def check_deviceuuid_exist(db: Session, device_uuid: str):
    if not db.query(fasteyes_uuid).filter(fasteyes_uuid.uuid == device_uuid).first():
        raise UnicornException(name=check_deviceuuid_exist.__name__,
                               description="device_uuid is not exist ", status_code=400)


def delete_fasteyes_uuid(db: Session, fasteyes_uuid_delete: FasteyesUuidSearchModel):
    fasteyes_uuid_db = db.query(fasteyes_uuid).filter(
        fasteyes_uuid.hardware_uuid == fasteyes_uuid_delete.hardwareuuid).first()
    if not fasteyes_uuid_db:
        raise HTTPException(status_code=404, detail="fasteyes_uuid not found")

    db.begin()
    try:
        db.delete(fasteyes_uuid_db)
        db.commit()
    except Exception as e:
        db.rollback()
        raise UnicornException(name=delete_fasteyes_uuid.__name__, description=str(e), status_code=500)

    return fasteyes_uuid_db


def reset_fasteyes_Uuid(db: Session, uuid: str):
    fasteyes_uuid_db = db.query(fasteyes_uuid).filter(fasteyes_uuid.hardware_uuid == uuid).first()
    db.begin()
    try:
        fasteyes_uuid_db.is_registered = False
        db.commit()
        db.refresh(fasteyes_uuid_db)
    except Exception as e:
        db.rollback()
        raise UnicornException(name=reset_fasteyes_Uuid.__name__, description=str(e), status_code=500)

    return fasteyes_uuid_db