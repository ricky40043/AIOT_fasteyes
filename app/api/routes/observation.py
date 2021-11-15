import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session

from typing import List, Optional

from starlette.responses import StreamingResponse

from app.db.database import get_db
from app.helper.device import check_Device_Authority, check_Device_Upload_Authority
from app.helper.authentication import Authorize_user
from app.helper.observation import check_observation_Authority
from app.models.schemas.observation import ObservationViewModel, ObservationPostModel, \
    ObservationPatchViewModel
from starlette.background import BackgroundTasks

from app.server.authentication import Authority_Level, checkLevel
from app.server.device.crud import check_device_owner, get_device_by_id
from app.server.ip_cam_device import ip_cam_video_stream, ip_cam_face_detect_stream
from app.server.observation.crud import delete_observation_by_device_id, \
    get_Observations_by_device_id_and_timespan, get_Observations_by_device_id, delete_observation_by_id
from app.server.send_email import send_email_async, send_email_temperature_alert
from fastapi_pagination import Page, paginate

router = APIRouter()


# # 裝置ID 上傳觀測 打Socket & 寄信 (User)
# @router.post("/devices/{device_id}/observation", response_model=ObservationViewModel)
# def UploadObservation(device_id: int,
#                       observation_in: ObservationPostModel,
#                       background_tasks: BackgroundTasks,
#                       db: Session = Depends(get_db),
#                       Authorize: AuthJWT = Depends()):
#     current_user = Authorize_user(Authorize, db)
#     device = check_Device_Upload_Authority(db, current_user, device_id)
#
#     if device.device_model_id == 1:
#         observation_db = Ceate_temperature_humidity_Observation(db, observation_in, current_user.group_id, device_id)
#
#     if current_user.info["email_alert"] and not observation_db.result:  # 寄信
#         send_email_temperature_alert(background_tasks=background_tasks, db=db,
#                                      email=current_user.email, observation_db=observation_db)
#     return observation_db


# Device ID 取得所有觀測 (User)
@router.get("/observations/device/{device_id}", response_model=Page[ObservationViewModel])
def GetObservationsByDeviceId(device_id: int,
                              start_timestamp: Optional[datetime] = None,
                              end_timestamp: Optional[datetime] = None,
                              db: Session = Depends(get_db),
                              Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Device_Authority(db, current_user, device_id)
    if start_timestamp and end_timestamp:
        return paginate(get_Observations_by_device_id_and_timespan(db, device_id, start_timestamp, end_timestamp))
    else:
        return paginate(get_Observations_by_device_id(db, device_id))


# 觀測ID 刪除觀測 (HRAccess)
@router.delete("/observations/{observation_id}", response_model=ObservationViewModel)
def DeleteObservation(observation_id: int,
                      db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    check_observation_Authority(db, current_user, observation_id)

    observation_db = delete_observation_by_id(db, observation_id)
    return observation_db


# 觀測ID 刪除觀測 (Admin)
@router.delete("/devices/{device_id}/observation")
def DeleteDeviceObservation(device_id: int,
                            db: Session = Depends(get_db),
                            Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    check_device_owner(db, device_id, current_user.id)

    return delete_observation_by_device_id(db, device_id)


# 取得IP Cam video (User)
@router.get("/ip_cam/device/{device_id}/video")
def GetIp_CamVideoByDeviceId(device_id: int,
                         db: Session = Depends(get_db)):
    #                     Authorize: AuthJWT = Depends()):
    # current_user = Authorize_user(Authorize, db)
    # device_db = check_Device_Authority(db, current_user, device_id)
    device_db = get_device_by_id(db, device_id)
    if device_db.device_model_id != 2:
        raise HTTPException(status_code=400, detail="this device is not ip cam")
    return StreamingResponse(ip_cam_video_stream(device_db.info["ip"],
                                                 device_db.info["port"],
                                                 device_db.info["username"],
                                                 device_db.info["password"],
                                                 device_db.info["stream_name"]),
                             media_type="multipart/x-mixed-replace;boundary=frame")


# 取得IP Cam Face detect (User)
@router.get("/ip_cam/device/{device_id}/face_detect")
def Get_Ip_CamFaceDetectByDeviceId(device_id: int,
                         db: Session = Depends(get_db)):
    #                     Authorize: AuthJWT = Depends()):
    # current_user = Authorize_user(Authorize, db)
    # device_db = check_Device_Authority(db, current_user, device_id)
    device_db = get_device_by_id(db, device_id)
    if device_db.device_model_id != 2:
        raise HTTPException(status_code=400, detail="this device is not ip cam")
    return StreamingResponse(ip_cam_face_detect_stream(device_db.info["ip"],
                                                       device_db.info["port"],
                                                       device_db.info["username"],
                                                       device_db.info["password"],
                                                       device_db.info["stream_name"]),
                             media_type="multipart/x-mixed-replace;boundary=frame")
# ########################################################################################################################