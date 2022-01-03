# crud
import csv

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.domain.Error_handler import UnicornException
from app.models.domain.device import device
from app.models.schemas.Nitrogen_device import NitrogenDevicePostModel, \
    NitrogenDevicePatchModel, NitrogenDevice_InfoModel
from app.server.device.crud import check_name_repeate, check_serial_number_repeate, \
    get_device_by_group_id_and_device_model_id, get_device_by_name
from app.server.device_model import DeviceType
from app.server.observation.crud import get_Observations_by_group_and_device_model_id_and_timespan


def get_Nitrogen_devices(db: Session, group_id: int):
    return db.query(device).filter(device.device_model_id == DeviceType.Nitrogen.value,
                                   device.group_id == group_id).all()


def create_Nitrogen_devices(db: Session, group_id: int, user_id: int,
                            name: str, serial_number: str, area: str, NitrogenDevice_create: NitrogenDevice_InfoModel):
    check_name_repeate(db, name, DeviceType.Nitrogen.value)
    check_serial_number_repeate(db, name, DeviceType.Nitrogen.value)

    db.begin()
    try:
        device_db = device(name=name,
                           serial_number=serial_number,
                           area=area,
                           info=NitrogenDevice_create,
                           group_id=group_id,
                           user_id=user_id,
                           device_model_id=DeviceType.Nitrogen.value)

        db.add(device_db)
        db.commit()
        db.refresh(device_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_Nitrogen_devices.__name__, description=str(e), status_code=500)
    return device_db


def modify_Nitrogen_devices(db: Session, group_id: int, device_id: int,
                            device_patch: NitrogenDevicePatchModel):
    device_db = db.query(device).filter(device.group_id == group_id,
                                        device.device_model_id == DeviceType.Nitrogen.value,
                                        device.id == device_id).first()

    device_by_name = get_device_by_name(db, device_patch.name, DeviceType.Nitrogen.value)
    if device_by_name:
        if device_by_name.id != device_db.id:
            raise HTTPException(status_code=400, detail="device name is exist")

    db.begin()
    try:
        temp_info = device_db.info.copy()  # dict 是 call by Ref. 所以一定要複製一份
        temp_info["alarm_Nitrogen_lower_limit"] = device_patch.info["alarm_Nitrogen_lower_limit"]
        temp_info["alarm_Nitrogen_upper_limit"] = device_patch.info["alarm_Nitrogen_upper_limit"]
        temp_info["alarm_Oxygen_lower_limit"] = device_patch.info["alarm_Oxygen_lower_limit"]
        temp_info["alarm_Oxygen_upper_limit"] = device_patch.info["alarm_Oxygen_upper_limit"]
        device_db.info = temp_info
        device_db.name = device_patch.name
        device_db.area = device_patch.area
        db.commit()
        db.refresh(device_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modify_Nitrogen_devices.__name__, description=str(e), status_code=500)
    return device_db


def delete_Nitrogen_devices(db: Session, group_id: int, device_id: int):
    device_db = db.query(device).filter(device.group_id == group_id,
                                        device.device_model_id == DeviceType.Nitrogen.value,
                                        device.id == device_id).first()
    if device_db is None:
        raise HTTPException(status_code=404, detail="device is not exist or is not in this group.")

    db.begin()
    try:
        db.delete(device_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_Nitrogen_devices.__name__, description=str(e), status_code=500)
    return device_db


def get_Nitrogen_observation_csv(db: Session, group_id, device_model_id, status, start_timestamp, end_timestamp):
    observation_data_list = get_Observations_by_group_and_device_model_id_and_timespan(db, group_id,
                                                                                       device_model_id,
                                                                                       status, start_timestamp,
                                                                                       end_timestamp)

    device_db_list = get_device_by_group_id_and_device_model_id(db, group_id, device_model_id)
    device_name_dict = {device_db.__dict__["id"]: device_db.__dict__["name"] for device_db in device_db_list}
    device_area_dict = {device_db.__dict__["id"]: device_db.__dict__["area"] for device_db in device_db_list}
    device_serial_number_dict = {device_db.__dict__["id"]: device_db.__dict__["serial_number"] for device_db in
                                 device_db_list}
    outputdata = [["裝置名稱", "裝置編號", "裝置位置", "測量時間", "氮氣壓力", "氮氣壓力異常", "氧氣濃度", "氧氣異常"]]

    for each_data in observation_data_list:
        each_data_dict = each_data.__dict__
        temp = []
        if device_model_id == DeviceType.temperature_humidity.value:
            temp.append(device_name_dict[each_data_dict["device_id"]])
            temp.append(device_serial_number_dict[each_data_dict["device_id"]])
            temp.append(device_area_dict[each_data_dict["device_id"]])
            temp.append(each_data_dict["created_at"].strftime("%m/%d/%Y, %H:%M:%S"))
            temp.append(each_data_dict["info"]["Nitrogen"])
            temp.append("異常" if each_data_dict["info"]["alarm_Nitrogen"] else "正常")
            temp.append(each_data_dict["info"]["Oxygen"] + "%")
            temp.append("異常" if each_data_dict["info"]["alarm_Oxygen"] else "正常")
            outputdata.append(temp)

    file_location = 'observation_data.csv'
    with open(file_location, 'w', newline="", encoding='utf-8-sig') as f:
        w = csv.writer(f)
        for eachdata in outputdata:
            w.writerow(eachdata)

    return file_location
