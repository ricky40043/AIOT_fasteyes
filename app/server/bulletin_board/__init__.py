import os
import io
import shutil
import cv2
from fastapi import UploadFile, File
from app.core.config import FILE_PATH
from app.models.domain.Error_handler import UnicornException
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.domain.bulletin_board import bulletin_board


def upload_image(group_id: int, image: UploadFile = File(...)):
    # 資料夾創建
    if not os.path.exists(FILE_PATH):
        os.mkdir(FILE_PATH)
    if not os.path.exists(FILE_PATH + "bulletin/"):
        os.mkdir(FILE_PATH + "bulletin/")
    if not os.path.exists(FILE_PATH + "bulletin/group" + str(group_id)):
        os.mkdir(FILE_PATH + "bulletin/group" + str(group_id))

    with open(FILE_PATH + "bulletin/group" + str(group_id)+ "/bulletin_image.jpg", "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)


# 傳檔案
def get_bulletin_image_file(db: Session, group_id: int):
    bulletin_board_db = db.query(bulletin_board).filter(bulletin_board.group_id == group_id).first()

    if not bulletin_board_db:
        raise UnicornException(name=get_bulletin_image_file.__name__, description="bulletin db not exist",
                               status_code=400)

    file_name = FILE_PATH + "bulletin/group" + str(group_id) + "/bulletin_image.jpg"
    cv2img = cv2.imread(file_name)
    if cv2img is None:
        raise UnicornException(name=get_bulletin_image_file.__name__, description="bulletin image not exist",
                               status_code=400)

    res, im_png = cv2.imencode(".jpg", cv2img)
    return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")


def delete_image(group_id):
    if os.path.exists(FILE_PATH + "bulletin/group" + str(group_id)):
        shutil.rmtree(FILE_PATH + "bulletin/group" + str(group_id))