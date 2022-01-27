# crud
import csv
from typing import Optional

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


def get_Nitrogen_devices(db: Session, group_id: int, area: Optional[str] = ""):
    if area == "":
        return db.query(device).filter(device.device_model_id == DeviceType.Nitrogen.value,
                                       device.group_id == group_id).order_by(device.id).all()
    else:
        return db.query(device).filter(device.device_model_id == DeviceType.Nitrogen.value,
                                       device.group_id == group_id, device.area == area).order_by(device.id).all()


def create_Nitrogen_devices(db: Session, group_id: int, user_id: int,
                            name: str, serial_number: str, area: str, NitrogenDevice_create: NitrogenDevice_InfoModel):

    check_name_repeate(db, name, DeviceType.Nitrogen.value, group_id, group_id)
    check_serial_number_repeate(db, name, DeviceType.Nitrogen.value, group_id)

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

    check_name_repeate(db, device_patch.name, DeviceType.Nitrogen.value, group_id, device_id)
    check_serial_number_repeate(db, device_patch.serial_number, DeviceType.Nitrogen.value, group_id, device_id)

    db.begin()
    try:
        temp_info = device_db.info.copy()  # dict 是 call by Ref. 所以一定要複製一份
        temp_info["alarm_Nitrogen_lower_limit"] = device_patch.info["alarm_Nitrogen_lower_limit"]
        temp_info["alarm_Nitrogen_upper_limit"] = device_patch.info["alarm_Nitrogen_upper_limit"]
        temp_info["alarm_Oxygen_lower_limit"] = device_patch.info["alarm_Oxygen_lower_limit"]
        temp_info["alarm_Oxygen_upper_limit"] = device_patch.info["alarm_Oxygen_upper_limit"]
        temp_info["Nitrogen_Flow_lower_limit"] = device_patch.info["Nitrogen_Flow_lower_limit"]
        temp_info["Nitrogen_Flow_upper_limit"] = device_patch.info["Nitrogen_Flow_upper_limit"]
        temp_info["Nitrogen_content_Oxygen_lower_limit"] = device_patch.info["Nitrogen_content_Oxygen_lower_limit"]
        temp_info["Nitrogen_content_Oxygen_upper_limit"] = device_patch.info["Nitrogen_content_Oxygen_upper_limit"]
        temp_info["ip"] = device_patch.info["ip"]
        temp_info["port"] = device_patch.info["port"]

        device_db.info = temp_info
        device_db.name = device_patch.name
        device_db.area = device_patch.area
        device_db.serial_number = device_patch.serial_number
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


def get_Nitrogen_observation_csv(db: Session, group_id, device_model_id, status, start_timestamp, end_timestamp, select_device:Optional[int]=-1, area: Optional[str]= ""):
    observation_data_list = get_Observations_by_group_and_device_model_id_and_timespan(db, group_id,
                                                                                       device_model_id,
                                                                                       status, start_timestamp,
                                                                                       end_timestamp, select_device, area)

    # device_db_list = get_device_by_group_id_and_device_model_id(db, group_id, device_model_id)
    # device_name_dict = {device_db.__dict__["id"]: device_db.__dict__["name"] for device_db in device_db_list}
    # device_area_dict = {device_db.__dict__["id"]: device_db.__dict__["area"] for device_db in device_db_list}
    # device_serial_number_dict = {device_db.__dict__["id"]: device_db.__dict__["serial_number"] for device_db in
    #                              device_db_list}
    outputdata = [["裝置名稱", "裝置編號", "裝置位置", "測量時間", "氮氣壓力(Mpag)", "空氣壓力(Nm3/h)", "氮氣流量(Mpag)",
                   "氮氣含氧量(ppm)", "氮氣氧含量高报警", "儀表空氣壓力低报警", "冷乾機故障", "空氣系統報警",
                   "氮氣壓力高", "氮氣壓力低", "運行信號", "停機信號", "系統待機", "維護提示"]]

    for each_data in observation_data_list:
        each_data_dict = each_data.__dict__
        temp = []
        # temp.append(device_name_dict[each_data_dict["device_id"]])
        # temp.append(device_serial_number_dict[each_data_dict["device_id"]])
        # temp.append(device_area_dict[each_data_dict["device_id"]])
        # print(each_data_dict["info"])
        temp.append(each_data_dict["info"]["name"])
        temp.append(each_data_dict["info"]["serial_number"])
        temp.append(each_data_dict["info"]["area"])
        temp.append(each_data_dict["created_at"].strftime("%m/%d/%Y, %H:%M:%S"))

        if each_data_dict["info"]["oxygen_height"] == -1:
            temp.append("無資料")
        else:
            temp.append(each_data_dict["info"]["oxygen_height"])

        if each_data_dict["info"]["air_press"] == -1:
            temp.append("無資料")
        else:
            temp.append(each_data_dict["info"]["air_press"])

        if each_data_dict["info"]["nitrogen_flowrate"] == -1:
            temp.append("無資料")
        else:
            temp.append(each_data_dict["info"]["nitrogen_flowrate"])

        if each_data_dict["info"]["oxygen_content"] == -1:
            temp.append("無資料")
        else:
            temp.append(each_data_dict["info"]["oxygen_content"])

        if each_data_dict["info"]["oxygen_height"] == 1:
            temp.append("異常")
        elif each_data_dict["info"]["oxygen_height"] == 0:
            temp.append("正常")
        else:
            temp.append("無資料")

        if each_data_dict["info"]["air_press_low"] == 1:
            temp.append("異常")
        elif each_data_dict["info"]["air_press_low"] == 0:
            temp.append("正常")
        else:
            temp.append("無資料")

        if each_data_dict["info"]["freeze_drier"] == 1:
            temp.append("異常")
        elif each_data_dict["info"]["freeze_drier"] == 0:
            temp.append("正常")
        else:
            temp.append("無資料")

        if each_data_dict["info"]["air_system"] == 1:
            temp.append("異常")
        elif each_data_dict["info"]["air_system"] == 0:
            temp.append("正常")
        else:
            temp.append("無資料")

        if each_data_dict["info"]["nitrogen_press_height"] == 1:
            temp.append("壓力高")
        elif each_data_dict["info"]["nitrogen_press_height"] == 0:
            temp.append("正常")
        else:
            temp.append("無資料")

        if each_data_dict["info"]["nitrogen_press_low"] == 1:
            temp.append("壓力低")
        elif each_data_dict["info"]["nitrogen_press_low"] == 0:
            temp.append("正常")
        else:
            temp.append("無資料")

        if each_data_dict["info"]["run_status"] == 1:
            temp.append("運轉中")
        elif each_data_dict["info"]["run_status"] == 0:
            temp.append("無運轉")
        else:
            temp.append("無資料")

        if each_data_dict["info"]["stop_status"] == 1:
            temp.append("停機")
        elif each_data_dict["info"]["stop_status"] == 0:
            temp.append("未停機")
        else:
            temp.append("無資料")

        if each_data_dict["info"]["standby_status"] == 1:
            temp.append("待機中")
        elif each_data_dict["info"]["standby_status"] == 0:
            temp.append("非待機狀態")
        else:
            temp.append("無資料")

        if each_data_dict["info"]["maintain_status"] == 1:
            temp.append("維護提示")
        elif each_data_dict["info"]["maintain_status"] == 0:
            temp.append("無提示")
        else:
            temp.append("無資料")

        outputdata.append(temp)

    file_location = 'observation_data.csv'
    with open(file_location, 'w', newline="", encoding='utf-8-sig') as f:
        w = csv.writer(f)
        for eachdata in outputdata:
            w.writerow(eachdata)

    return file_location
