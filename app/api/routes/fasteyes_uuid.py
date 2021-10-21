from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session

from typing import List
from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.models.schemas.fasteyes_uuid import FasteysesUuidViewModel, FasteysesUuidPostModel, FasteyesUuidChangeModel, \
    FasteyesUuidSearchModel
from app.server.authentication import Authority_Level, verify_password, checkLevel
from app.server.fasteyes_device.crud import delete_fasteyes_device_by_id, get_fasteyes_device_by_uuid
from app.server.fasteyes_observation.crud import delete_observation_by_device_id
from app.server.fasteyes_uuid.crud import get_All_fasteyes_uuids, create_fasteyes_uuid, change_hardwareUuid, \
    delete_fasteyes_uuid, get_hardware_uuid, reset_fasteyes_Uuid

router = APIRouter()


# 取得所有device uuid (RD)
@router.get("/fasteyes_uuid/all", response_model=List[FasteysesUuidViewModel])
def GetAllfasteyes_devices(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_All_fasteyes_uuids(db)


# 創建 uuid (Partner)
@router.post("/fasteyes_uuid", response_model=FasteysesUuidViewModel)
def CreateFasteyesUuid(fasteyes_uuid_create: FasteysesUuidPostModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.Partner.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    device_uuid_db = create_fasteyes_uuid(db, fasteyes_uuid_create)
    return device_uuid_db


# 尋找 hardwareuuid
@router.post("/fasteyes_hardware_uuid", response_model=FasteysesUuidViewModel)
def SearchFasteyesUuid(fasteyes_uuid_search: FasteyesUuidSearchModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    fasteyes_uuid = get_hardware_uuid(db, fasteyes_uuid_search.hardwareuuid)
    if not fasteyes_uuid:
        raise HTTPException(status_code=404, detail="fasteyes_hardware_uuid is not exist")
    return fasteyes_uuid


# ########################################################################################################################
# hardwareUuid Reset 同時刪除裝置 (Admin)
@router.patch("/fasteyes_uuid/reset/{hardwareUuid}", response_model=FasteysesUuidViewModel)
def ResetHardwareUuid(hardwareUuid: str,
                      db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    hardware_uuid_db = get_hardware_uuid(db, hardwareUuid)

    if not hardware_uuid_db:
        raise HTTPException(status_code=400, detail="hardware_uuid is not exist")

    if not hardware_uuid_db.is_registered:
        raise HTTPException(status_code=400, detail="hardware_uuid is not registered")

    # Delete Device
    device_db = get_fasteyes_device_by_uuid(db, hardware_uuid_db.uuid)
    if device_db:
        delete_observation_by_device_id(db, device_db.id)
        delete_fasteyes_device_by_id(db, device_db.id)

    return reset_fasteyes_Uuid(db, hardwareUuid)


# 修改  hardware_uuid (RD)
@router.patch("/fasteyes_uuid", response_model=FasteysesUuidViewModel)
def ChangeFasteyesHardwareUuid(fasteyes_uuid_patch: FasteyesUuidChangeModel,
                               db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    device_uuid_db = change_hardwareUuid(db, fasteyes_uuid_patch)
    return device_uuid_db


# 刪除 uuid (RD)
@router.delete("/fasteyes_uuid", response_model=FasteysesUuidViewModel)
def DeleteFasteyesHardwareUuid(fasteyes_uuid: FasteyesUuidSearchModel,
                               db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):

    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    device_uuid_db = delete_fasteyes_uuid(db, fasteyes_uuid)
    return device_uuid_db
