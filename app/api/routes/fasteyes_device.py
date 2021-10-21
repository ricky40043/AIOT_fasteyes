from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session

from typing import List
from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.models.schemas.fasteyes_device import FasteyesDeviceViewModel, FasteyesDevicePostViewModel, \
    FasteyesDeviceSettingChangeModel, FasteyesDevicePatchModel
from app.server.authentication import Authority_Level, verify_password, checkLevel
from app.server.fasteyes_device.crud import get_All_fasteyes_devices, get_group_fasteyes_devices, \
    check_device_exist_by_deviceuuid, regist_device, \
    change_fasteyes_device_setting, change_fasteyes_device_data, check_device_owner, get_fasteyes_device_by_uuid
from app.server.fasteyes_uuid.crud import check_deviceuuid_exist

router = APIRouter()


# 取得所有device (RD)
@router.get("/fasteyes_device/all", response_model=List[FasteyesDeviceViewModel])
def GetAllfasteyes_devices(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_All_fasteyes_devices(db)


# 取得所有device (Admin)
@router.get("/fasteyes_device", response_model=List[FasteyesDeviceViewModel])
def Getgroup_fasteyes_devices(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    return get_group_fasteyes_devices(db, current_user.group_id)


# 註冊 創建裝置 (HRAccess)
@router.post("/fasteyes_device", response_model=FasteyesDeviceViewModel)
def RegistDevice(device_in: FasteyesDevicePostViewModel,
                 db: Session = Depends(get_db),
                 Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    check_deviceuuid_exist(db, device_in.device_uuid)
    check_device_exist_by_deviceuuid(db, device_in.device_uuid)
    device_db = regist_device(db, device_in, user_id=current_user.id, group_id=current_user.group_id)
    # send_data(device_db.to_dict())
    return device_db


# device_id 修改 Device info (HRAccess)
@router.patch("/fasteyes_device/{fasteyes_device_id}", response_model=FasteyesDeviceViewModel)
def PatchUserSetting(fasteyes_device_id: int, DevicePatch: FasteyesDevicePatchModel,
                     db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_device_owner(db, fasteyes_device_id, current_user.id)
    return change_fasteyes_device_data(db, fasteyes_device_id, DevicePatch)


# device_id 修改 Device setting (HRAccess)
@router.patch("/fasteyes_device/{fasteyes_device_id}/setting", response_model=FasteyesDeviceViewModel)
def PatchUserSetting(fasteyes_device_id: int, DevicePatch: FasteyesDeviceSettingChangeModel,
                     db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_device_owner(db, fasteyes_device_id, current_user.id)
    return change_fasteyes_device_setting(db, fasteyes_device_id, DevicePatch)


# 取得device by device_uuid
@router.post("/fasteyes_device/{fasteyes_uuid}", response_model=FasteyesDeviceViewModel)
def GetFasteyesDevice(fasteyes_uuid: str, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    fasteyes_device = get_fasteyes_device_by_uuid(db,fasteyes_uuid)
    if fasteyes_device is None:
        raise HTTPException(status_code=404, detail="fasteyes_device is not exist")

    return fasteyes_device