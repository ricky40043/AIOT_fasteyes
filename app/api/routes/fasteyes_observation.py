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
from app.helper.fasteyes_device import check_FasteyesDevice_Authority
from app.helper.fasteyes_observation import check_observation_Authority
from app.helper.staff import check_Staff_Authority
from app.models.schemas.fasteyes_observation import FasteyesObservationViewModel, FasteyesObservationPostModel, \
    FasteyesObservationPatchViewModel, attendanceViewModel, attendancePostModel
from starlette.background import BackgroundTasks

from app.models.schemas.fasteyes_output import FasteyesOutputPatchViewModel
from app.server.authentication import Authority_Level, checkLevel
from app.server.fasteyes_device.crud import check_fasteyes_device_owner
from app.server.fasteyes_observation.crud import upload_observation_image, download_observation_image, \
    get_Observations_by_device_id_and_staff_id, get_Observations_by_staff_id, get_Observations_by_department_id, \
    get_Observations_by_staff_id_and_timespan, get_Observations_by_department_id_and_timespan, \
    download_observation_image_by_id, CeateFasteyesObservation, update_observation, get_attendence_by_time_interval, \
    delete_observation_by_id, delete_observation_by_device_id, get_Observations_by_group_id_and_timespan
from app.server.fasteyes_output.crud import get_fasteyes_outputs_by_id, fasteyes_output_modify
from app.server.send_email import send_email_async, send_email_temperature_alert
from app.server.staff.crud import get_staff_by_id
from fastapi_pagination import Page, paginate

router = APIRouter()


# 裝置ID 上傳觀測 打Socket & 寄信 (HRAccess)
@router.post("/fasteyes_devices/{device_id}/observation", response_model=FasteyesObservationViewModel)
def UploadObservation(device_id: int,
                      observation_in: FasteyesObservationPostModel,
                      background_tasks: BackgroundTasks,
                      db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_FasteyesDevice_Authority(db, current_user, device_id)
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
def UploadObservationImage(device_id: int,
                           file_name: str,
                           image_file: UploadFile = File(...),
                           db: Session = Depends(get_db),
                           Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_FasteyesDevice_Authority(db, current_user, device_id)
    return upload_observation_image(db, device_id, file_name, image_file)


# 裝置ID file_name 下載觀測image (HRAccess)
@router.get("/Files/download/image/device/{device_id}/file_name/{file_name}")
def DownloadObservationImage(device_id: int,
                             file_name: str,
                             db: Session = Depends(get_db)):
    # Authorize: AuthJWT = Depends()):
    # current_user = Authorize_user(Authorize, db)
    # if not checkLevel(current_user, Authority_Level.Admin.value):
    #     raise HTTPException(status_code=401, detail="權限不夠")

    return download_observation_image(device_id, file_name)


# 裝置ID file_name 下載觀測image (HRAccess)
@router.get("/fasteyes_observations/{observation_id}/image")
def DownloadObservationImage(observation_id: int,
                             db: Session = Depends(get_db),
                             Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return download_observation_image_by_id(db, observation_id)


# 取得所有觀測 (HRAccess)
@router.get("/fasteyes_observations", response_model=Page[FasteyesObservationViewModel])
def GetObservations(start_timestamp: Optional[datetime] = None,
                    end_timestamp: Optional[datetime] = None,
                    db: Session = Depends(get_db),
                    Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if start_timestamp and end_timestamp:
        return paginate(
            get_Observations_by_group_id_and_timespan(db, current_user.group_id, start_timestamp, end_timestamp))
    else:
        return paginate(get_Observations_by_staff_id(db, current_user.group_id))


# 員工ID 取得所有觀測 (HRAccess)
@router.get("/fasteyes_observations/staff/{staff_id}", response_model=Page[FasteyesObservationViewModel])
def GetObservationsByStaffId(staff_id: int,
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
@router.get("/fasteyes_observations/department/{department_id}", response_model=Page[FasteyesObservationViewModel])
def GetObservationsByDepartmentId(department_id: int,
                                  start_timestamp: Optional[datetime] = None,
                                  end_timestamp: Optional[datetime] = None,
                                  db: Session = Depends(get_db),
                                  Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_department_Authority(db, current_user, department_id)
    if start_timestamp and end_timestamp:
        return paginate(
            get_Observations_by_department_id_and_timespan(db, department_id, start_timestamp, end_timestamp))
    else:
        return paginate(get_Observations_by_department_id(db, department_id))


# 觀測ID 修改觀測 (HRAccess)
@router.patch("/fasteyes_observations/{observation_id}", response_model=FasteyesObservationViewModel)
def UpdateObservation(observation_id: int, obsPatch: FasteyesObservationPatchViewModel,
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

    return paginate(
        get_attendence_by_time_interval(db, current_user.group_id, start_timestamp, end_timestamp, attendance_in))


# 觀測ID 刪除觀測 (HRAccess)
@router.delete("/fasteyes_observations/{observation_id}", response_model=FasteyesObservationViewModel)
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

    check_fasteyes_device_owner(db, device_id, current_user.id)

    return delete_observation_by_device_id(db, device_id)


# 取得資料輸出格式 (Admin)
@router.get("/fasteyes_observations/output_format")
def GetFasteyesOutput(db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_fasteyes_outputs_by_id(db, current_user.group_id)


# 取得資料輸出格式 (Admin)
@router.patch("/fasteyes_observations/output_format")
def ModifyFasteyesOutput(fasteyes_output: FasteyesOutputPatchViewModel,
                         db: Session = Depends(get_db),
                         Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return fasteyes_output_modify(db, current_user.group_id, fasteyes_output)


# 取得資料輸出 (Admin)
@router.get("/fasteyes_observations/output_data")
def ModifyFasteyesOutput(start_timestamp: Optional[datetime] = None,
                         end_timestamp: Optional[datetime] = None,
                         db: Session = Depends(get_db),
                         Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    # step1 取得時間區間內資料

    # step2 把staff id中離職員工的資料拿掉

    # step3 排版輸出資料

    # step4 利用pandas 和 Numpy 把資料整理成輸出檔案csv檔案

    return "Done" # step5"回傳結果"
########################################################################################################################
