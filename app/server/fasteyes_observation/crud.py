# crud
import _datetime
from datetime import datetime, timedelta

from app.models.domain.fasteyes_observation import fasteyes_observation
import io
import os
import shutil
import cv2
from sqlalchemy.orm import Session
from app.core.config import FILE_PATH
from app.models.domain.Error_handler import UnicornException
from app.models.domain.staff import staff
from app.models.schemas.fasteyes_observation import FasteyesObservationInfoModel, FasteyesObservationPostModel, \
    FasteyesObservationViewModel, FasteyesObservationPatchViewModel, attendancePostModel
from starlette.responses import StreamingResponse
from fastapi import UploadFile, File

from app.server.department.crud import get_department_by_id
from app.server.fasteyes_device.crud import get_fasteyes_device_by_id
from app.server.staff.crud import get_default_staff_id, get_staff_by_id


def get_All_observations(db: Session):
    return db.query(fasteyes_observation).all()


def get_observation_by_id(db: Session, observation_id: int):
    return db.query(fasteyes_observation).filter(fasteyes_observation.id == observation_id).first()


def CeateFasteyesObservation(db: Session, observation_in: FasteyesObservationPostModel, group_id: int,
                             fasteyes_device_id: int):
    db.begin()
    try:
        if observation_in.staff_id == -1:
            observation_in.staff_id = get_default_staff_id(db).id

        staff_db = get_staff_by_id(db, observation_in.staff_id)
        temp_info = observation_in.info.copy()  # dict 是 call by Ref. 所以一定要複製一份
        info = temp_info.dict()
        info["staff_name"] = staff_db.info["name"]
        info["staff_serial_number"] = staff_db.serial_number
        info["department_name"] = get_department_by_id(db, staff_db.department_id).name
        info["device_name"] = get_fasteyes_device_by_id(db, fasteyes_device_id).name

        observation_db = fasteyes_observation(phenomenon_time=observation_in.phenomenon_time,
                                              result=observation_in.result,
                                              image_name=observation_in.image_name,
                                              info=info,
                                              staff_id=observation_in.staff_id,
                                              group_id=group_id,
                                              fasteyes_device_id=fasteyes_device_id)
        db.add(observation_db)
        db.commit()
        db.refresh(observation_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=CeateFasteyesObservation.__name__, description=str(e), status_code=500)
    return observation_db


def upload_observation_image(db: Session, device_id: int, image_name: str, image: UploadFile = File(...)):
    Observation_db = db.query(fasteyes_observation).filter(fasteyes_observation.image_name == image_name).first()
    if not Observation_db:
        raise UnicornException(name=upload_observation_image.__name__, description="file name is not exist",
                               status_code=404)

    try:
        # 資料夾創建
        if not os.path.exists(FILE_PATH + "observation/"):
            os.mkdir(FILE_PATH + "observation/")
        if not os.path.exists(FILE_PATH + "observation/" + "device" + str(device_id)):
            os.mkdir(FILE_PATH + "observation/" + "device" + str(device_id))

        with open(FILE_PATH + "observation/" + "device" + str(device_id) + "/" + image_name + ".jpg", "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        print(str(e))
        raise UnicornException(name=upload_observation_image.__name__, description=str(e), status_code=500)
    finally:
        image.file.close()

    return Observation_db


def download_observation_image(device_id: int, image_name: str):
    file_name = FILE_PATH + "observation/" + "device" + str(device_id) + "/" + image_name + ".jpg"
    try:
        cv2img = cv2.imread(file_name)
        res, im_png = cv2.imencode(".jpg", cv2img)
    except Exception as e:
        print(str(e))
        raise UnicornException(name=download_observation_image.__name__, description=str(e), status_code=500)

    return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")


def download_observation_image_by_id(db: Session, observation_id: int):
    try:
        observation_db = db.query(fasteyes_observation).filter(fasteyes_observation.id == observation_id).first()
        file_name = FILE_PATH + "observation/" + "device" + str(
            observation_db.fasteyes_device_id) + "/" + observation_db.image_name + ".jpg"
        cv2img = cv2.imread(file_name)
        res, im_png = cv2.imencode(".jpg", cv2img)
    except Exception as e:
        print(str(e))
        raise UnicornException(name=download_observation_image.__name__, description=str(e), status_code=500)

    return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")


def get_Observations_by_group_id_and_timespan(db: Session, group_id: int, start_timestamp: datetime,
                                              end_timestamp: datetime, status_in):
    if status_in == -1:
        return db.query(fasteyes_observation).filter(fasteyes_observation.group_id == group_id).filter(
            fasteyes_observation.phenomenon_time >= start_timestamp,
            fasteyes_observation.phenomenon_time <= end_timestamp).order_by(
            -fasteyes_observation.id).all()
    else:
        return db.query(fasteyes_observation).filter(fasteyes_observation.group_id == group_id).filter(
            fasteyes_observation.phenomenon_time >= start_timestamp,
            fasteyes_observation.phenomenon_time <= end_timestamp).filter(
            fasteyes_observation.result == status_in).order_by(
            -fasteyes_observation.id).all()


def get_Observations_by_device_id_and_staff_id(db: Session, device_id: int, staff_id: int):
    return db.query(fasteyes_observation).filter(fasteyes_observation.device_id == device_id,
                                                 fasteyes_observation.staff_id == staff_id).order_by(
        -fasteyes_observation.id).all()


def get_Observations_by_staff_id(db: Session, staff_id: int):
    return db.query(fasteyes_observation).filter(fasteyes_observation.staff_id == staff_id).order_by(
        -fasteyes_observation.id).all()


def get_Observations_by_group_id(db: Session, group_id: int, status: int):
    return db.query(fasteyes_observation).filter(fasteyes_observation.group_id == group_id).order_by(
        -fasteyes_observation.id).all()


def get_Observations_by_department_id(db: Session, department_id: int):
    return db.query(fasteyes_observation).join(staff).filter(staff.department_id == department_id).order_by(
        -fasteyes_observation.id).all()


def get_Observations_by_staff_id_and_timespan(db: Session, staff_id: int, start_timestamp: datetime,
                                              end_timestamp: datetime):
    return db.query(fasteyes_observation).filter(fasteyes_observation.staff_id == staff_id).filter(
        fasteyes_observation.phenomenon_time >= start_timestamp,
        fasteyes_observation.phenomenon_time <= end_timestamp).order_by(
        -fasteyes_observation.id).all()


def get_Observations_by_department_id_and_timespan(db: Session, department_id: int, start_timestamp: datetime,
                                                   end_timestamp: datetime, status: int):
    return db.query(fasteyes_observation).join(staff).filter(staff.department_id == department_id).filter(
        fasteyes_observation.phenomenon_time >= start_timestamp,
        fasteyes_observation.phenomenon_time <= end_timestamp).order_by(-fasteyes_observation.id).all()


def get_All_fasteyes_observations(db: Session):
    return db.query(fasteyes_observation).order_by(-fasteyes_observation.id).all()


def update_observation(db: Session, observation_id: int, obsPatch: FasteyesObservationPatchViewModel):
    db.begin()
    try:
        observation_db = db.query(fasteyes_observation).filter(fasteyes_observation.id == observation_id).first()
        observation_db.staff_id = obsPatch.staff_id
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=update_observation.__name__, description=str(e), status_code=500)
    return observation_db


def check_observation_ownwer(db: Session, observation_id: int, group_id: int):
    return db.query(fasteyes_observation).filter(fasteyes_observation.id == observation_id,
                                                 fasteyes_observation.group_id == group_id).first()


def get_attendence_by_time_interval(db: Session, group_id: int, start_timestamp: datetime,
                                    end_timestamp: datetime, attendance_in: attendancePostModel, status_in: int):
    fasteyes_observation_db_list = db.query(fasteyes_observation).filter(
        fasteyes_observation.group_id == group_id).filter(
        fasteyes_observation.phenomenon_time >= start_timestamp,
        fasteyes_observation.phenomenon_time <= end_timestamp).order_by(fasteyes_observation.phenomenon_time).all()

    bCrossDay = False
    date = start_timestamp.date()
    datetime1 = datetime.combine(date, attendance_in.working_time_1)
    datetime2 = datetime.combine(date, attendance_in.working_time_off_1)

    if datetime1 > datetime2:
        bCrossDay = True

    timeinterval = end_timestamp - start_timestamp
    date_attendance_list = [{"date": start_timestamp.date() + timedelta(day), "attendance": []} for day in
                            range(timeinterval.days)]
    for each_fasteyes_observation in fasteyes_observation_db_list:
        # 先判斷上班時間
        if attendance_in.working_time_1 < each_fasteyes_observation.phenomenon_time.time() < attendance_in.working_time_2:
            temp_timeinterval = (each_fasteyes_observation.phenomenon_time.date() - start_timestamp.date())
            idx = temp_timeinterval.days
            date_attendance = date_attendance_list[idx]["attendance"]

            # 判斷 資料是否已有 沒有就新增
            res = next((sub for sub in date_attendance if sub['staff_id'] == each_fasteyes_observation.staff_id), None)
            if not res:
                working_time_data = {
                    "staff_id": each_fasteyes_observation.staff_id,
                    "punch_in": each_fasteyes_observation.phenomenon_time,
                    "punch_in_temperature_result": each_fasteyes_observation.result,
                    "punch_in_temperature": each_fasteyes_observation.info["temperature"],
                    "staff_name": each_fasteyes_observation.info["staff_name"],
                    "staff_serial_number": each_fasteyes_observation.info["staff_serial_number"],
                    "department_name": each_fasteyes_observation.info["department_name"]
                }
                date_attendance.append(working_time_data)

            # else:
            #     res["punch_in"] = each_fasteyes_observation.phenomenon_time
            #     res["punch_in_temperature_result"] = each_fasteyes_observation.result
            #     res["punch_in_temperature"] = each_fasteyes_observation.info["temperature"]
        # 判斷下班時間
        elif attendance_in.working_time_off_1 < each_fasteyes_observation.phenomenon_time.time() < attendance_in.working_time_off_2:
            temp_timeinterval = (each_fasteyes_observation.phenomenon_time.date() - start_timestamp.date())
            idx = temp_timeinterval.days
            if bCrossDay:
                idx = idx - 1
            date_attendance = date_attendance_list[idx]["attendance"]
            # 判斷 資料是否已有 沒有就新增
            res = next((sub for sub in date_attendance if sub['staff_id'] == each_fasteyes_observation.staff_id), None)
            if not res:
                working_time_data = {
                    "staff_id": each_fasteyes_observation.staff_id,
                    "punch_out": each_fasteyes_observation.phenomenon_time,
                    "punch_out_temperature_result": each_fasteyes_observation.result,
                    "punch_out_temperature": each_fasteyes_observation.info["temperature"],
                    "staff_name": each_fasteyes_observation.info["staff_name"],
                    "staff_serial_number": each_fasteyes_observation.info["staff_serial_number"],
                    "department_name": each_fasteyes_observation.info["department_name"]
                }
                date_attendance.append(working_time_data)
            else:
                res["punch_out"] = each_fasteyes_observation.phenomenon_time
                res["punch_out_temperature_result"] = each_fasteyes_observation.result
                res["punch_out_temperature"] = each_fasteyes_observation.info["temperature"]

    for each_date_attendance in date_attendance_list:
        attendance_list = each_date_attendance["attendance"]
        if status_in == 0:
            filtered = filter(filter_status_normal, attendance_list)
            each_date_attendance["attendance"] = list(filtered)
        elif status_in == 1:
            filtered = filter(filter_status_abnormal, attendance_list)
            each_date_attendance["attendance"] = list(filtered)

    return date_attendance_list


def filter_status_normal(x):
    return not x["punch_in_temperature_result"] and not x["punch_out_temperature_result"] and len(x) == 10


def filter_status_abnormal(x):
    return x["punch_in_temperature_result"] or x["punch_out_temperature_result"] or len(x) <10


def delete_observation_by_device_id(db: Session, device_id: int):
    db.begin()
    try:
        db.query(fasteyes_observation).filter(fasteyes_observation.fasteyes_device_id == device_id).delete()

        if os.path.exists(FILE_PATH + "observation/device" + str(device_id)):
            shutil.rmtree(FILE_PATH + "observation/device" + str(device_id))

        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_observation_by_device_id.__name__, description=str(e), status_code=500)
    return "Delete observation Done"


def delete_observation_by_id(db: Session, observation_id: int):
    db.begin()
    try:
        observation_db = db.query(fasteyes_observation).filter(
            fasteyes_observation.fasteyes_device_id == observation_id).delete()

        if os.path.exists(FILE_PATH + "observation/" + "device" + str(
                observation_db.device_id) + "/" + observation_db.image_name + ".jpg"):
            os.remove(FILE_PATH + "observation/" + "device" + str(
                observation_db.device_id) + "/" + observation_db.image_name + ".jpg")

        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_observation_by_id.__name__, description=str(e), status_code=500)
    return fasteyes_observation
