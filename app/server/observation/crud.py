# crud
import io
import os
import shutil
from datetime import datetime

import cv2
from sqlalchemy.orm import Session
from app.core.config import FILE_PATH
from app.db.database import get_db
from app.models.domain.Error_handler import UnicornException
from app.models.domain.observation import observation
from starlette.responses import StreamingResponse
from fastapi import UploadFile, File

from app.models.schemas.observation import ObservationPostModel
from app.models.schemas.temperature_humidity_observation import temperature_humidity_ObservationPostModel
from app.models.schemas.Nitrogen_observation import Nitrogen_ObservationPostModel
from app.models.schemas.electrostatic_observation import electrostatic_ObservationPostModel

def get_All_observations(db: Session):
    return db.query(observation).all()


def get_observation_by_id(db: Session, observation_id: int):
    return db.query(observation).filter(observation.id == observation_id).first()


def check_observation_ownwer(db: Session, observation_id: int, group_id: int):
    return db.query(observation).filter(observation.id == observation_id, observation.group_id == group_id).first()


def Create_temperature_humidity_Observation(observation_in: dict, group_id: int, device_id: int):
    db = next(get_db())
    db.begin()
    try:
        observation_db = observation(info=observation_in,
                                     group_id=group_id,
                                     device_id=device_id,
                                     device_model_id=1)
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
                                     device_model_id=4)
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
                                     device_model_id=1)
        db.add(observation_db)
        db.commit()
        db.refresh(observation_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=Ceate_electrostatic_Observation.__name__, description=str(e),
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
                                     device_model_id=1)
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
