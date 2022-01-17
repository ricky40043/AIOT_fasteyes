# crud
import io
import os
import shutil
from datetime import datetime, timedelta
from typing import Optional

import cv2
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.config import FILE_PATH
from app.db.database import get_db
from app.models.domain.Error_handler import UnicornException
from app.models.domain.device import device
from app.models.domain.observation import observation
from starlette.responses import StreamingResponse
from fastapi import UploadFile, File

from app.models.schemas.observation import ObservationPostModel
from app.models.schemas.temperature_humidity_observation import temperature_humidity_ObservationPostModel, \
    temperature_humidity_infoModel
from app.models.schemas.Nitrogen_observation import Nitrogen_ObservationPostModel
from app.models.schemas.electrostatic_observation import electrostatic_ObservationPostModel
from app.server.device_model import DeviceType
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean

def get_All_observations(db: Session):
    return db.query(observation).all()


def get_observation_by_id(db: Session, observation_id: int):
    return db.query(observation).filter(observation.id == observation_id).first()


def check_observation_ownwer(db: Session, observation_id: int, group_id: int):
    return db.query(observation).filter(observation.id == observation_id, observation.group_id == group_id).first()


def Create_temperature_humidity_Observation(observation_in: temperature_humidity_infoModel, group_id: int,
                                            device_id: int):
    db = next(get_db())
    db.begin()
    try:
        observation_db = observation(info=observation_in,
                                     group_id=group_id,
                                     device_id=device_id,
                                     device_model_id=DeviceType.temperature_humidity.value)
        db.add(observation_db)
        db.commit()
        db.refresh(observation_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=Create_temperature_humidity_Observation.__name__, description=str(e),
                               status_code=500)
    return observation_db


def Ceate_Nitrogen_Observation(db: Session,
                               observation_in: Nitrogen_ObservationPostModel,
                               group_id: int, device_id: int):
    db.begin()
    try:
        observation_db = observation(**observation_in.dict(),
                                     group_id=group_id,
                                     device_id=device_id,
                                     device_model_id=DeviceType.Nitrogen.value)
        db.add(observation_db)
        db.commit()
        db.refresh(observation_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=Ceate_Nitrogen_Observation.__name__, description=str(e),
                               status_code=500)
    return observation_db


def Ceate_electrostatic_Observation(db: Session,
                                    observation_in: electrostatic_ObservationPostModel,
                                    group_id: int, device_id: int):
    db.begin()
    try:
        observation_db = observation(**observation_in.dict(),
                                     group_id=group_id,
                                     device_id=device_id,
                                     device_model_id=DeviceType.electrostatic.value)
        db.add(observation_db)
        db.commit()
        db.refresh(observation_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=Ceate_electrostatic_Observation.__name__, description=str(e),
                               status_code=500)
    return observation_db


def delete_observation_by_id(db: Session, observation_id: int):
    db.begin()
    try:
        observation_db = db.query(observation).filter(observation.id == observation_id).first()
        db.delete(observation_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_observation_by_id.__name__, description=str(e),
                               status_code=500)
    return observation_db


def delete_observation_by_device_id(db: Session, device_id: int):
    db.begin()
    try:
        observation_db = db.query(observation).filter(observation.device_id == device_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_observation_by_device_id.__name__, description=str(e),
                               status_code=500)

    return "delete temperature_humidity_device" + str(device_id) + "_observation"


def get_Observations_by_device_id_and_timespan(db: Session, device_id: int, start_timestamp: datetime,
                                               end_timestamp: datetime):
    return db.query(observation).filter(observation.device_id == device_id).filter(
        observation.created_at >= start_timestamp, observation.created_at <= end_timestamp).all()


def get_Observations_by_device_id(db: Session, device_id: int):
    return db.query(observation).filter(observation.device_id == device_id).all()


def get_Lastest_Observation_by_device_id(db: Session, group_id: int):
    temperature_humidity_device_list = db.query(device).filter(
        device.device_model_id == DeviceType.temperature_humidity.value,
        device.group_id == group_id).order_by(device.id).all()

    temperature_humidity_observation_list = []
    for temperature_humidity_device in temperature_humidity_device_list:
        interval_time = temperature_humidity_device.info["interval_time"]
        start_time = datetime.now() - timedelta(seconds=int(interval_time) * 3)
        end_time = datetime.now()
        observation_db = db.query(observation).filter(observation.device_id == temperature_humidity_device.id,
                                                      observation.created_at > start_time,
                                                      observation.created_at < end_time,
                                                      ).order_by(-observation.id).first()
        if observation_db:
            temperature_humidity_observation_list.append(observation_db)

    return temperature_humidity_observation_list


def get_Observations_by_group_and_device_model_id_and_timespan(db: Session, group_id: int, device_model_id: int,
                                                               status_in: int,
                                                               start_timestamp: datetime,
                                                               end_timestamp: datetime,
                                                               select_device_id: Optional[int] = -1,
                                                               area: Optional[str] = ""):
    if status_in == -1:
        if select_device_id == -1:
            data_list = db.query(observation).filter(observation.group_id == group_id,
                                                     observation.device_model_id == device_model_id).filter(
                observation.created_at >= start_timestamp, observation.created_at <= end_timestamp). \
                order_by(-observation.id).all()
        else:
            data_list = db.query(observation).filter(observation.group_id == group_id,
                                                     observation.device_model_id == device_model_id,
                                                     observation.device_id == select_device_id).filter(
                observation.created_at >= start_timestamp, observation.created_at <= end_timestamp). \
                order_by(-observation.id).all()
    elif status_in == 0:
        if select_device_id == -1:
            data_list = db.query(observation).filter(observation.group_id == group_id,
                                                     observation.device_model_id == device_model_id).filter(
                observation.created_at >= start_timestamp, observation.created_at <= end_timestamp). \
                filter(observation.info["status"].astext.cast(Integer) == 0,
                       observation.info["alarm_temperature"].astext.cast(Boolean) == False,
                       observation.info["alarm_humidity"].astext.cast(Boolean) == False). \
                order_by(-observation.id).all()
        else:
            data_list = db.query(observation).filter(observation.group_id == group_id,
                                                     observation.device_model_id == device_model_id,
                                                     observation.device_id == select_device_id).filter(
                observation.created_at >= start_timestamp, observation.created_at <= end_timestamp). \
                filter(observation.info["status"].astext.cast(Integer) == 0,
                       observation.info["alarm_temperature"].astext.cast(Boolean) == False,
                       observation.info["alarm_humidity"].astext.cast(Boolean) == False). \
                order_by(-observation.id).all()

    else:
        if select_device_id == -1:
            data_list = db.query(observation).filter(observation.group_id == group_id,
                                                     observation.device_model_id == device_model_id).filter(
                observation.created_at >= start_timestamp, observation.created_at <= end_timestamp). \
                filter(or_(observation.info["status"].astext.cast(Integer) !=0,
                           observation.info["alarm_temperature"].astext.cast(Boolean) == True,
                           observation.info["alarm_humidity"].astext.cast(Boolean) == True)). \
                order_by(-observation.id).all()
            return data_list
        else:
            data_list = db.query(observation).filter(observation.group_id == group_id,
                                                     observation.device_model_id == device_model_id,
                                                     observation.device_id == select_device_id).filter(
                observation.created_at >= start_timestamp, observation.created_at <= end_timestamp). \
                filter(or_(observation.info["status"].astext.cast(Integer) != 0,
                           observation.info["alarm_temperature"].astext.cast(Boolean) == True,
                           observation.info["alarm_humidity"].astext.cast(Boolean) == True)). \
                order_by(-observation.id).all()
    if area == "" or area == None:
        return data_list
    else:
        filter_list = list(filter(lambda each_observation: each_observation.info["area"] == area, data_list))
        return filter_list
