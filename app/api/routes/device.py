from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session

from typing import List

from starlette.responses import StreamingResponse

from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.models.schemas.device_model import DeviceViewModel, DeviceModelPostModel, DevicePatchModel, DevicePostModel
from app.server.authentication import Authority_Level, verify_password, checkLevel
from app.server.device_model import DeviceType
from app.server.ip_cam_device import ip_cam_video_stream
from app.server.temperature_humidity_device.crud import get_temperature_humidity_devices, \
    create_temperature_humidity_devices, modify_temperature_humidity_devices, delete_temperature_humidity_devices
from app.server.ip_cam_device.crud import get_ip_cam_devices, create_ip_cam_devices, \
    modify_ip_cam_devices, delete_ip_cam_devices
from app.server.electrostatic_device.crud import get_electrostatic_devices, \
    create_electrostatic_devices, modify_electrostatic_devices, delete_electrostatic_devices
from app.server.Nitrogen_device.crud import get_Nitrogen_devices, \
    create_Nitrogen_devices, modify_Nitrogen_devices, delete_Nitrogen_devices

router = APIRouter()


# 取得所有device (user)
@router.get("/devices/device_model/{device_model_id}", response_model=List[DeviceViewModel])
def GetAllDevices(device_model_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.User.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if device_model_id == DeviceType.temperature_humidity.value:
        return get_temperature_humidity_devices(db, current_user.group_id)
    elif device_model_id == DeviceType.ip_cam.value:
        return get_ip_cam_devices(db, current_user.group_id)
    elif device_model_id == DeviceType.electrostatic.value:
        return get_electrostatic_devices(db, current_user.group_id)
    elif device_model_id == DeviceType.Nitrogen.value:
        return get_Nitrogen_devices(db, current_user.group_id)


# 創建device (Admin)
@router.post("/devices/device_model/{device_model_id}", response_model=DeviceViewModel)
def CreateDevices(device_model_id: int, device_create: DevicePostModel,
                  db: Session = Depends(get_db),
                  Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")
    if device_model_id == DeviceType.temperature_humidity.value:
        device = create_temperature_humidity_devices(db, current_user.group_id, current_user.id,
                                                     device_create.name, device_create.serial_number, device_create.area, device_create.info)
    elif device_model_id == DeviceType.ip_cam.value:
        device = create_ip_cam_devices(db, current_user.group_id, current_user.id,
                                       device_create.name, device_create.serial_number, device_create.area, device_create.info)
    elif device_model_id == DeviceType.electrostatic.value:
        device = create_electrostatic_devices(db, current_user.group_id, current_user.id,
                                              device_create.name, device_create.serial_number, device_create.area, device_create.info)
    elif device_model_id == DeviceType.Nitrogen.value:
        device = create_Nitrogen_devices(db, current_user.group_id, current_user.id,
                                         device_create.name, device_create.serial_number, device_create.area, device_create.info)

    return device


# 修改device (RD)
@router.patch("/devices/device_model/{device_model_id}/device/{device_id}", response_model=DeviceViewModel)
def ModifyDevices(device_model_id: int, device_id: int,
                  device_patch: DevicePatchModel, db: Session = Depends(get_db),
                  Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if device_model_id == DeviceType.temperature_humidity.value:
        return modify_temperature_humidity_devices(db, current_user.group_id, device_id, device_patch)
    elif device_model_id == DeviceType.ip_cam.value:
        return modify_ip_cam_devices(db, current_user.group_id, device_id, device_patch)
    elif device_model_id == DeviceType.electrostatic.value:
        return modify_electrostatic_devices(db, current_user.group_id, device_id, device_patch)
    elif device_model_id == DeviceType.Nitrogen.value:
        return modify_Nitrogen_devices(db, current_user.group_id, device_id, device_patch)


# 刪除device (RD)
@router.delete("/devices/device_model/{device_model_id}/device/{device_id}", response_model=DeviceViewModel)
def DeleteDevices(device_model_id: int, device_id: int, db: Session = Depends(get_db),
                  Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if device_model_id == DeviceType.temperature_humidity.value:
        return delete_temperature_humidity_devices(db, current_user.group_id, device_id)
    elif device_model_id == DeviceType.ip_cam.value:
        return delete_ip_cam_devices(db, current_user.group_id, device_id)
    elif device_model_id == DeviceType.electrostatic.value:
        return delete_electrostatic_devices(db, current_user.group_id, device_id)
    elif device_model_id == DeviceType.Nitrogen.value:
        return delete_Nitrogen_devices(db, current_user.group_id, device_id)


# ipcam test (Admin)
# @router.post("/ip_cam/connect_test", response_model=DeviceViewModel)
# def ip_cam_connect_test(Ip_CamTest: Ip_CamTestModel, db: Session = Depends(get_db),
#                         Authorize: AuthJWT = Depends()):
#     current_user = Authorize_user(Authorize, db)
#
#     if not checkLevel(current_user, Authority_Level.Admin.value):
#         raise HTTPException(status_code=401, detail="權限不夠")
#
#     return ip_cam_connect(Ip_CamTest)

# ipcam test (Admin)
@router.get("/ip_cam/connect_test")
def Ip_camConnectTest(ip: str,
                        port: str,
                        username: str,
                        password: str,
                        stream_name: str):
    return StreamingResponse(ip_cam_video_stream(ip, port, username, password, stream_name),
                             media_type="multipart/x-mixed-replace;boundary=frame")


