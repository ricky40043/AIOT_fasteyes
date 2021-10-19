import os
import shutil

from app.core.config import file_path
from fastapi import UploadFile, File


def upload_image(group_id: int, staff_id: int, image_name: str, image: UploadFile = File(...)):
    # 資料夾創建
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    if not os.path.exists(file_path + "face/"):
        os.mkdir(file_path + "face/")
    if not os.path.exists(file_path + "face/group" + str(group_id)):
        os.mkdir(file_path + "face/group" + str(group_id))
    if not os.path.exists(file_path + "face/group" + str(group_id) + "/staff" + str(staff_id)):
        os.mkdir(file_path + "face/group" + str(group_id) + "/staff" + str(staff_id))
    if not os.path.exists(file_path + "face/group" + str(group_id) + "/staff" + str(staff_id)):
        os.mkdir(file_path + "face/group" + str(group_id) + "/staff" + str(staff_id))

    with open(file_path + "face/group" + str(group_id) + "/staff" + str(
            staff_id) + "/" + image_name + ".jpg", "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)


def delete_image(group_id: int, staff_id: int, image_name: str):
    if os.path.exists(file_path + "face/group" + str(group_id) + "/staff" + str(staff_id)):
        os.remove(file_path + "face/group" + str(group_id) + "/staff" + str(
            staff_id) + "/" + image_name + ".jpg")


def delete_all_image(group_id: int, staff_id: int):
    if os.path.exists(file_path + "face/group" + str(group_id) + "/staff" + str(staff_id)):
        shutil.rmtree(file_path + "face/group" + str(group_id) + "/staff" + str(staff_id))