# crud
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.domain.Error_handler import UnicornException
from app.models.domain.device import device
from app.models.schemas.temperature_humidity_device import Temperature_humidityDevicePostModel, \
    Temperature_humidityDevicePatchModel, Temperature_humidityDevice_InfoModel
from app.server.device.crud import check_name_repeate, check_serial_number_repeate
from app.server.device_model import DeviceType


def get_temperature_humidity_devices(db: Session, group_id: int):
    return db.query(device).filter(device.device_model_id == DeviceType.temperature_humidity.value,
                                   device.group_id == group_id).order_by(device.id).all()


def get_temperature_humidity_devices_by_serial_number(serial_number: str):
    db = next(get_db())
    return db.query(device).filter(device.device_model_id == DeviceType.temperature_humidity.value, device.serial_number == serial_number).first()


def create_temperature_humidity_devices(db: Session, group_id: int, user_id: int, name: str, serial_number: str,
                                        area: str, Temperature_humidityDevice_create: Temperature_humidityDevice_InfoModel):
    check_name_repeate(db, name, DeviceType.temperature_humidity.value)
    check_serial_number_repeate(db, name, DeviceType.temperature_humidity.value)

    db.begin()
    try:
        device_db = device(name=name,
                           area=area,
                           serial_number=serial_number,
                           info=Temperature_humidityDevice_create,
                           group_id=group_id,
                           user_id=user_id,
                           device_model_id=DeviceType.temperature_humidity.value)

        db.add(device_db)
        db.commit()
        db.refresh(device_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_temperature_humidity_devices.__name__, description=str(e), status_code=500)
    return device_db


def modify_temperature_humidity_devices(db: Session, group_id: int, device_id: int,
                                        device_patch: Temperature_humidityDevicePatchModel):
    device_db = db.query(device).filter(device.group_id == group_id,
                                        device.device_model_id == DeviceType.temperature_humidity.value,
                                        device.id == device_id).first()

    check_name_repeate(db, device_patch.name, DeviceType.temperature_humidity.value)

    db.begin()
    try:
        temp_info = device_db.info.copy()  # dict 是 call by Ref. 所以一定要複製一份
        temp_info["alarm_humidity"] = device_patch.info["alarm_humidity"]
        temp_info["alarm_temperature"] = device_patch.info["alarm_temperature"]
        temp_info["battery_alarm"] = device_patch.info["battery_alarm"]
        temp_info["interval_time"] = device_patch.info["interval_time"]
        device_db.info = temp_info
        device_db.name = device_patch.name
        device_db.area = device_patch.area
        db.commit()
        db.refresh(device_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modify_temperature_humidity_devices.__name__, description=str(e), status_code=500)
    return device_db


def delete_temperature_humidity_devices(db: Session, group_id: int, device_id: int):
    device_db = db.query(device).filter(device.group_id == group_id,
                                        device.device_model_id == DeviceType.temperature_humidity.value,
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
        raise UnicornException(name=delete_temperature_humidity_devices.__name__, description=str(e), status_code=500)
    return device_db
