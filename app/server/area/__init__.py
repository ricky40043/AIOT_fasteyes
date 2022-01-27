from app.core.config import FILE_PATH
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
import os
import shutil


def upload_image(group_id: int, area_id: int, image: UploadFile = File(...)):
    # 資料夾創建
    if not os.path.exists(FILE_PATH):
        os.mkdir(FILE_PATH)
    if not os.path.exists(FILE_PATH + "area/"):
        os.mkdir(FILE_PATH + "area/")
    if not os.path.exists(FILE_PATH + "area/group" + str(group_id)):
        os.mkdir(FILE_PATH + "area/group" + str(group_id))

    with open(FILE_PATH + "area/group" + str(group_id) + "/area" + str(
            area_id) + ".jpg", "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)


def delete_image(group_id: int, area_id: int):
    if os.path.isfile(FILE_PATH + "area/group" + str(group_id) + "/area" + str(area_id) + ".jpg"):
        os.remove(FILE_PATH + "area/group" + str(group_id) + "/area" + str(area_id) + ".jpg")


def delete_group_image(group_id: int):
    if os.path.exists(FILE_PATH + "area/group" + str(group_id)):
        shutil.rmtree(FILE_PATH + "area/group" + str(group_id))
