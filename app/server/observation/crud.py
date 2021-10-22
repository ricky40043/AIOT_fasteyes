# crud
import io
import os
import shutil
import cv2
from sqlalchemy.orm import Session
from app.core.config import FILE_PATH
from app.models.domain.Error_handler import UnicornException
from app.models.domain.observation import observation
from app.models.schemas.fasteyes_observation import ObservationPostModel
from starlette.responses import StreamingResponse
from fastapi import UploadFile, File


def get_All_observations(db: Session):
    return db.query(observation).all()
