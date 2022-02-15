# crud
import os
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import FILE_PATH
from app.models.domain.Error_handler import UnicornException
from app.models.domain.face import face
from app.models.domain.staff import staff
import cv2
import io
from fastapi import UploadFile, File
from starlette.responses import StreamingResponse
from app.server.face import upload_image, delete_all_image


def get_All_faces(db: Session):
    return db.query(face).all()


def get_staff_face_images(db: Session, staff_id: int):
    return db.query(face).filter(face.staff_id == staff_id).first()


# 傳檔案
def get_staff_face_image_file(db: Session, staff_id: int):
    staff_db = db.query(staff).filter(staff.id == staff_id).first()
    Face_db = db.query(face).filter(face.staff_id == staff_id).first()
    if not Face_db:
        raise UnicornException(name=get_staff_face_image_file.__name__, description="face image not exist",
                               status_code=400)

    file_name = FILE_PATH + "face/group" + str(staff_db.group_id) + "/staff" + str(
        staff_db.id) + "/" + Face_db.face_uuid + ".jpg"
    cv2img = cv2.imread(file_name)
    if cv2img is None:
        raise UnicornException(name=get_staff_face_image_file.__name__, description="face image not exist",
                               status_code=400)

    res, im_png = cv2.imencode(".jpg", cv2img)
    return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")


def upload_face_file(db: Session, staff_id: int, image: UploadFile = File(...)):
    db_staff = db.query(staff).filter(staff.id == staff_id).first()
    db.begin()
    try:
        temp_info = db_staff.info.copy()
        temp_info["face_detect"] = True
        db_staff.info = temp_info
        face_uuid = uuid.uuid4()
        while True:
            if db.query(face).filter(face.face_uuid == str(face_uuid)).first():
                face_uuid = uuid.uuid4()
            else:
                break
        upload_image(db_staff.group_id, db_staff.id, str(face_uuid), image)
        Face_db = face(staff_id=staff_id,
                       group_id=db_staff.group_id,
                       face_uuid=face_uuid)
        db.add(Face_db)
        db.commit()
        db.refresh(Face_db)

    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=upload_face_file.__name__, description=str(e), status_code=500)
    finally:
        image.file.close()
    return Face_db


def delete_staff_all_image(db: Session, staff_id: int):
    Staff_db = db.query(staff).filter(staff.id == staff_id).first()
    db.begin()
    try:
        # 刪除全部照片和feature
        delete_all_image(Staff_db.group_id, staff_id)
        db.query(face).filter(face.staff_id == staff_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_staff_all_image.__name__, description=str(e), status_code=500)
    return "Delete All Image Done"


def upload_raw_face_feature(db: Session, staff_id, raw_face_feature: str):
    db.begin()
    try:
        staff_db = db.query(staff).filter(staff.id == staff_id).first()
        face_db = db.query(face).filter(face.staff_id == staff_id).first()
        face_db.updated_at = datetime.now()
        temp_info = staff_db.info.copy()
        temp_info["face_feature"] = raw_face_feature
        staff_db.info = temp_info
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=upload_raw_face_feature.__name__, description=str(e), status_code=500)
    return staff_db


def download_raw_face_feature(db: Session, staff_id):
    # 回傳檔案資料
    try:
        staff_db = db.query(staff).filter(staff.id == staff_id).first()

        face_db = db.query(face).filter(face.staff_id == staff_id).first()

        raw_face_feature_data = {
            "id": face_db.id,
            "face_uuid": face_db.face_uuid,
            "updated_at": face_db.updated_at,
            "created_at": face_db.created_at,
            "staff_id": face_db.staff_id,
            "raw_face_feature": staff_db.info["face_feature"]
        }

    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=download_raw_face_feature.__name__, description=str(e), status_code=500)

    return raw_face_feature_data

