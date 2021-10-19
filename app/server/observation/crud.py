# crud
import io
import os
import shutil
import cv2
from sqlalchemy.orm import Session
from app.core.config import file_path
from app.models.domain.Error_handler import UnicornException
from app.models.domain.observation import observation
from app.models.schemas.fasteyes_observation import ObservationPostModel
from starlette.responses import StreamingResponse
from fastapi import UploadFile, File


def get_All_observations(db: Session):
    return db.query(observation).all()

#
# def create_observation(db: Session, observation_in: ObservationPostModel, device_id: int):
#     db.begin()
#     try:
#         observation_db = observation(**observation_in.dict(), device_id=device_id)
#         db.add(observation_db)
#         db.commit()
#         db.refresh(observation_db)
#     except Exception as e:
#         db.rollback()
#         print(str(e))
#         raise UnicornException(name=create_observation.__name__, description=str(e), status_code=500)
#     return observation_db
#
#
# def upload_observation_image(db: Session, device_id: int, image_name: str, image: UploadFile = File(...)):
#     try:
#         # 資料夾創建
#         if not os.path.exists(file_path + "observation/"):
#             os.mkdir(file_path + "observation/")
#         if not os.path.exists(file_path + "observation/" + "device" + str(device_id)):
#             os.mkdir(file_path + "observation/" + "device" + str(device_id))
#
#         with open(file_path + "observation/" + "device" + str(device_id) + "/" + image_name + ".jpg", "wb") as buffer:
#             shutil.copyfileobj(image.file, buffer)
#         Observation_db = db.query(observation).filter(observation.image_name == image_name).first()
#     except Exception as e:
#         print(str(e))
#         raise UnicornException(name=upload_observation_image.__name__, description=str(e), status_code=500)
#     finally:
#         image.file.close()
#
#     return Observation_db
#
#
# def download_observation_image(device_id: int, image_name: str):
#     file_name = file_path + "observation/" + "device" + str(device_id) + "/" + image_name + ".jpg"
#     cv2img = cv2.imread(file_name)
#     res, im_png = cv2.imencode(".jpg", cv2img)
#     return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")
#
# def download_observation_image_by_id(db:Session,observation_id: int):
#     observation_db = db.query(observation).filter(observation.id == observation_id).first()
#     file_name = file_path + "observation/" + "device" + str(observation_db.device_id) + "/" + observation_db.image_name + ".jpg"
#     cv2img = cv2.imread(file_name)
#     res, im_png = cv2.imencode(".jpg", cv2img)
#     return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")
#
#
#
#
# def get_Observations_by_device_id_and_staff_id(db: Session, device_id: int, staff_id: int):
#     return db.query(observation).filter(observation.device_id == device_id, observation.staff_id == staff_id).all()
#
#
# def get_Observations_by_staff_id(db: Session, staff_id: int):
#     return db.query(observation).filter(observation.staff_id == staff_id).all()
#
#
# def get_Observations_by_department_id(db: Session, staff_id: int):
#     return db.query(observation).filter(observation.staff_id == staff_id).all()
#
#
# def get_Observations_by_staff_id_and_timespan(db: Session, staff_id: int, start_timestamp: os,
#                                                end_timestamp: os):
#     # test
#     start_timestamp = start_timestamp
#     end_timestamp = end_timestamp
#     return db.query(observation).filter(observation.staff_id == staff_id).filter(
#         observation.updated_at >= start_timestamp, observation.updated_at <= end_timestamp).all()
#
#
# def get_Observations_by_department_id_and_timespan(db: Session, staff_id: int, start_timestamp: os,
#                                                end_timestamp: os):
#     # test
#     start_timestamp = start_timestamp
#     end_timestamp = end_timestamp
#     return db.query(observation).filter(observation.staff_id == staff_id).filter(
#         observation.updated_at >= start_timestamp, observation.updated_at <= end_timestamp).all()