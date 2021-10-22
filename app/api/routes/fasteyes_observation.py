import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session

from typing import List, Optional
from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.helper.department import check_department_Authority
from app.helper.fasteyes_device import check_Device_Authority
from app.helper.fasteyes_observation import check_observation_Authority
from app.helper.staff import check_Staff_Authority
from app.models.schemas.fasteyes_observation import ObservationViewModel, ObservationPostModel, \
    ObservationPatchViewModel, attendanceViewModel, attendancePostModel
from starlette.background import BackgroundTasks

from app.server.authentication import Authority_Level, checkLevel
from app.server.fasteyes_device.crud import check_device_owner
from app.server.fasteyes_observation.crud import upload_observation_image, download_observation_image, \
    get_Observations_by_device_id_and_staff_id, get_Observations_by_staff_id, get_Observations_by_department_id, \
    get_Observations_by_staff_id_and_timespan, get_Observations_by_department_id_and_timespan, \
    download_observation_image_by_id, CeateFasteyesObservation, update_observation, get_attendence_by_time_interval, \
    delete_observation_by_id, delete_observation_by_device_id
from app.server.send_email import send_email_async, send_email_temperature_alert
from app.server.staff.crud import get_staff_by_id
from fastapi_pagination import Page, paginate
router = APIRouter()


# 裝置ID 上傳觀測 打Socket & 寄信 (HRAccess)
@router.post("/fasteyes_devices/{device_id}/observation", response_model=ObservationViewModel)
def UploadObservation(device_id: int,
                      observation_in: ObservationPostModel,
                      background_tasks: BackgroundTasks,
                      db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Device_Authority(db, current_user, device_id)
    observation_db = CeateFasteyesObservation(db, observation_in, current_user.group_id, device_id)

    # send_data("uploadobservation", observation_db.to_dict())

    # time_start = time.time()
    if current_user.info["email_alert"] and not observation_db.result:  # 寄信
        send_email_temperature_alert(background_tasks=background_tasks, db=db,
                                     email=current_user.email, observation_db=observation_db)
    # time_end = time.time()  # 結束計時

    # time_c = time_end - time_start  # 執行所花時間
    # print('time cost', time_c, 's')
    return observation_db


# 裝置ID file_name 上傳觀測image (HRAccess)
@router.post("/Files/upload/image/device/{device_id}/file_name/{file_name}")
def Upload_observation_image(device_id: int,
                             file_name: str,
                             image_file: UploadFile = File(...),
                             db: Session = Depends(get_db),
                             Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Device_Authority(db, current_user, device_id)
    return upload_observation_image(db, device_id, file_name, image_file)


# 裝置ID file_name 下載觀測image (HRAccess)
@router.get("/Files/download/image/device/{device_id}/file_name/{file_name}")
def Download_observation_image(device_id: int,
                               file_name: str,
                               db: Session = Depends(get_db)):
    # Authorize: AuthJWT = Depends()):
    # current_user = Authorize_user(Authorize, db)
    # if not checkLevel(current_user, Authority_Level.Admin.value):
    #     raise HTTPException(status_code=401, detail="權限不夠")

    return download_observation_image(device_id, file_name)


# 裝置ID file_name 下載觀測image (HRAccess)
@router.get("/fasteyes_observations/{observation_id}/image")
def Download_observation_image(observation_id: int,
                               db: Session = Depends(get_db),
                               Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return download_observation_image_by_id(db, observation_id)


# 員工ID 取得所有觀測 (HRAccess)
@router.get("/fasteyes_observations/staff/{staff_id}", response_model=Page[ObservationViewModel])
def GetObservationsByDeviceId_And_StaffId(staff_id: int,
                                          start_timestamp: Optional[datetime] = None,
                                          end_timestamp: Optional[datetime] = None,
                                          db: Session = Depends(get_db),
                                          Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Staff_Authority(db, current_user, staff_id)
    if start_timestamp and end_timestamp:
        return paginate(get_Observations_by_staff_id_and_timespan(db, staff_id, start_timestamp, end_timestamp))
    else:
        return paginate(get_Observations_by_staff_id(db, staff_id))


# 部門ID 取得所有觀測 (HRAccess)
@router.get("/fasteyes_observations/department/{department_id}", response_model=Page[ObservationViewModel])
def GetObservationsByDeviceId_And_StaffId(department_id: int,
                                          start_timestamp: Optional[datetime] = None,
                                          end_timestamp: Optional[datetime] = None,
                                          db: Session = Depends(get_db),
                                          Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_department_Authority(db, current_user, department_id)
    if start_timestamp and end_timestamp:
        return paginate(get_Observations_by_department_id_and_timespan(db, department_id, start_timestamp, end_timestamp))
    else:
        return paginate(get_Observations_by_department_id(db, department_id))


# 觀測ID 修改觀測 (HRAccess)
@router.patch("/fasteyes_observations/{observation_id}", response_model=ObservationViewModel)
def UpdateObservation(observation_id: int, obsPatch: ObservationPatchViewModel,
                      db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    check_observation_Authority(db, current_user, observation_id)

    if not get_staff_by_id(db, obsPatch.staff_id):
        raise HTTPException(status_code=404, detail="staff id is not exist")

    return update_observation(db, observation_id, obsPatch)


# 取得考勤紀錄 (HRAccess)
@router.get("/attendance", response_model=Page[attendanceViewModel])
def GetObservationsByDeviceId_And_StaffId(attendance_in: attendancePostModel,
                                          start_timestamp: Optional[datetime] = None,
                                          end_timestamp: Optional[datetime] = None,
                                          db: Session = Depends(get_db),
                                          Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return paginate(get_attendence_by_time_interval(db, current_user.group_id, start_timestamp, end_timestamp, attendance_in))


# 觀測ID 刪除觀測 (HRAccess)
@router.delete("/fasteyes_observations/{observation_id}", response_model=ObservationViewModel)
def DeleteObservation(observation_id: int,
                      db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    check_observation_Authority(db, current_user, observation_id)

    return delete_observation_by_id(db, observation_id)


# 觀測ID 刪除觀測 (Admin)
@router.delete("/fasteyes_observations/device/{device_id}")
def DeleteDeviceObservation(device_id: int,
                      db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    check_device_owner(db, device_id, current_user.id)

    return delete_observation_by_device_id(db, device_id)

########################################################################################################################
