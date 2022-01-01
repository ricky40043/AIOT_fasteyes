import time
from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session
import os
from typing import List, Optional
from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.helper.department import check_department_Authority
from app.helper.fasteyes_device import check_FasteyesDevice_Authority
from app.helper.fasteyes_observation import check_observation_Authority
from app.helper.staff import check_Staff_Authority
from app.models.schemas.fasteyes_observation import FasteyesObservationViewModel, FasteyesObservationPostModel, \
    FasteyesObservationPatchViewModel, attendanceViewModel, attendancePostModel, attendancePieViewModel, \
    attendanceTime_intervalViewModel
from starlette.background import BackgroundTasks

from app.models.schemas.fasteyes_output import FasteyesOutputPatchViewModel
from app.server.authentication import Authority_Level, checkLevel
from app.server.fasteyes_device.crud import check_fasteyes_device_owner
from app.server.fasteyes_observation import output_interval_data_csv, get_output_data_form, modify_output_data_form
from app.server.fasteyes_observation.crud import upload_observation_image, download_observation_image, \
    get_Observations_by_department_id, \
    get_Observations_by_staff_id_and_timespan, get_Observations_by_department_id_and_timespan, \
    download_observation_image_by_id, CeateFasteyesObservation, update_observation, get_attendence_by_time_interval, \
    delete_observation_by_id, delete_observation_by_device_id, get_Observations_by_group_id_and_timespan, \
    get_attendence_by_time_interval_data, output_observations_by_group
from app.server.fasteyes_output.crud import get_fasteyes_outputs_by_id, fasteyes_output_modify
from app.server.send_email import send_email_async, send_email_temperature_alert
from app.server.staff.crud import get_staff_by_id, get_staff_by_group
from fastapi_pagination import Page, paginate
from starlette.responses import FileResponse
import csv

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

    # time_start = time.time()
    if current_user.info["email_alert"] and observation_db.result:  # 寄信
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
def GetObservations(status: int,
                    start_timestamp: datetime,
                    end_timestamp: datetime,
                    select_device_id: Optional[int] = -1,
                    db: Session = Depends(get_db),
                    Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    return paginate(get_Observations_by_group_id_and_timespan(db, current_user.group_id, start_timestamp, end_timestamp,
                                                              status, select_device_id))


# 員工ID 取得所有觀測 (HRAccess)
@router.get("/fasteyes_observations/staff/{staff_id}", response_model=Page[FasteyesObservationViewModel])
def GetObservationsByStaffId(staff_id: int,
                             start_timestamp: datetime,
                             end_timestamp: datetime,
                             select_device_id: Optional[int] = -1,
                             db: Session = Depends(get_db),
                             Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Staff_Authority(db, current_user, staff_id)
    if start_timestamp and end_timestamp:
        return paginate(
            get_Observations_by_staff_id_and_timespan(db, staff_id, start_timestamp, end_timestamp, select_device_id))


# 部門ID 取得所有觀測 (HRAccess)
@router.get("/fasteyes_observations/department/{department_id}", response_model=Page[FasteyesObservationViewModel])
def GetObservationsByDepartmentId(department_id: int,
                                  status: int,
                                  start_timestamp: Optional[datetime] = None,
                                  end_timestamp: Optional[datetime] = None,
                                  db: Session = Depends(get_db),
                                  Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_department_Authority(db, current_user, department_id)
    if start_timestamp and end_timestamp:
        return paginate(
            get_Observations_by_department_id_and_timespan(db, department_id, start_timestamp, end_timestamp, status))
    else:
        return paginate(get_Observations_by_department_id(db, department_id, status))


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
@router.post("/attendance", response_model=Page[attendanceViewModel])
def GetAttendance(attendance_in: attendancePostModel,
                  status: int,
                  start_timestamp: datetime,
                  end_timestamp: datetime,
                  select_device_id: Optional[int] = -1,
                  db: Session = Depends(get_db),
                  Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return paginate(get_attendence_by_time_interval(db, current_user.group_id, start_timestamp,
                                                    end_timestamp, attendance_in, status, select_device_id))


# 取得考勤紀錄Pie (HRAccess)
@router.post("/attendance/pie", response_model=attendancePieViewModel)
def GetAttendancePie(attendance_in: attendancePostModel,
                     start_timestamp: datetime,
                     end_timestamp: datetime,
                     select_device_id: Optional[int] = -1,
                     db: Session = Depends(get_db),
                     Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")
    attendence_data_list = get_attendence_by_time_interval(db, current_user.group_id, start_timestamp, end_timestamp,
                                                           attendance_in, -1, select_device_id)
    # 取得在職員工
    staff_db_list = get_staff_by_group(db, current_user.group_id, 1, -1)
    staff_id_list = [each_staff.id for each_staff in staff_db_list]
    staff_total = len(staff_db_list)

    # 計算出勤
    temp = attendancePieViewModel()
    for attendence_data in attendence_data_list:
        day_attendence_data = attendence_data["attendance"]
        for each_data in day_attendence_data:
            # print(each_data)
            if each_data["staff_id"] not in staff_id_list:
                # print("員工已被離職")
                continue

            if "punch_in" in each_data and "punch_out" in each_data:
                temp.ontime += 1
            elif "punch_in" not in each_data and "punch_out" in each_data:
                temp.late += 1
            elif "punch_in" in each_data and "punch_out" not in each_data:
                temp.leaveEarly += 1

    temp.notArrived = len(attendence_data_list) * staff_total - temp.ontime - temp.late - temp.leaveEarly

    return temp


# 取得考勤紀錄 時間表(HRAccess)
@router.post("/attendance/line_chart", response_model=attendanceTime_intervalViewModel)
def GetAttendance(attendance_in: attendancePostModel,
                  page: int,
                  start_timestamp: datetime,
                  end_timestamp: datetime,
                  select_device_id: int,
                  db: Session = Depends(get_db),
                  Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")
    work_time_interval_data = get_attendence_by_time_interval_data(db, current_user.group_id, start_timestamp,
                                                                   end_timestamp,
                                                                   attendance_in, -1, select_device_id)

    temp = attendanceTime_intervalViewModel()

    # 取得在職員工
    staff_total = len(get_staff_by_group(db, current_user.group_id, 1, -1))
    # 計算出勤

    working_time = int(attendance_in.working_time_1.strftime("%-H"))
    working_time_off = int(attendance_in.working_time_off_2.strftime("%-H")) + 1
    day_attendence_data = work_time_interval_data[page - 1]["attendance"]
    time_interval = [x for x in range(working_time, working_time_off)]
    work_staff = [0 for i in range(working_time, working_time_off)]
    for each_data in day_attendence_data:
        # print(each_data)
        if "punch_in" in each_data and "punch_out" in each_data:
            punch_in_time = int(each_data["punch_in"].strftime("%-H")) + 1
            punch_out_time = int(each_data["punch_out"].strftime("%-H"))

            for i in range(working_time, working_time_off):
                if punch_in_time <= i <= punch_out_time:
                    work_staff[i - working_time] += 1
    temp.time_interval = [str(each_time) + ":00" for each_time in time_interval]
    # temp.time_interval = time_interval
    temp.work_staff = work_staff
    temp.total_staff = staff_total

    return temp


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

    check_fasteyes_device_owner(db, device_id, current_user.group_id)

    return delete_observation_by_device_id(db, device_id)


@router.get("/fasteyes_observations/output_form", response_model=FasteyesOutputPatchViewModel)
def getFasteyeObservationOutputForm(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    data = get_output_data_form(current_user.group_id)
    return data


@router.patch("/fasteyes_observations/output_form/modify", response_model=FasteyesOutputPatchViewModel)
def getFasteyeObservationOutputForm(output_form: FasteyesOutputPatchViewModel,
                                    db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    output_form_out = modify_output_data_form(current_user.group_id, output_form)

    return output_form_out


@router.get("/fasteyes_observations/output_interval_data_csv")
def FasteyesOutputCSV(start_timestamp: Optional[datetime] = None,
                      end_timestamp: Optional[datetime] = None,
                      db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    csv_file = output_interval_data_csv(db, current_user.group_id, start_timestamp, end_timestamp)
    print(csv_file)

    return FileResponse(csv_file, media_type='text/csv', filename=csv_file)
########################################################################################################################
