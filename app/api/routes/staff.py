from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session

from typing import List, Optional

from app.core.config import HOST_NAME, COMPUTE_URL
from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.helper.department import check_department_Authority
from app.helper.staff import check_Staff_Authority, Check_Staff_Authority_SerialNumber
from app.models.schemas.face import FaceViewModel, FaceFeatureViewModel
from app.models.schemas.staff import StaffViewModel, StaffPostModel, StaffPatchModel
from app.server.authentication import Authority_Level, checkLevel
from app.server.department.crud import get_department_by_id
from app.server.face.crud import get_staff_face_images, get_staff_face_image_file, upload_face_file, \
    delete_staff_all_image, download_raw_face_feature, upload_raw_face_feature
from app.server.staff.crud import get_All_staffs, get_user_by_serveral_number_in_group, create_staff, \
    get_staff_by_group, modefy_Staff_Info, delete_Staff_by_Staff_id, get_default_staff_id
import json

import requests

router = APIRouter()


# 取得所有Staff (RD)
@router.get("/staffs/GetAllStaffs", response_model=List[StaffViewModel])
def GetAllStaffs(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_All_staffs(db)


# 取得所有員工 (HRAccess)
@router.get("/staffs", response_model=List[StaffViewModel])
def GetStaffs(status: Optional[int] = -1, department_id: Optional[int] = -1, db: Session = Depends(get_db),
              Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_staff_by_group(db, current_user.group_id, status, department_id)


# 員工ID 取得員工 (HRAccess)
@router.get("/staffs/{staff_id}", response_model=StaffViewModel)
def GetStaffById(staff_id: int, db: Session = Depends(get_db),
                 Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    staff = check_Staff_Authority(db, current_user, staff_id)
    return staff


# 員工編號 取得員工 (HRAccess)
@router.get("/staffs/SerialNumber/{SerialNumber}", response_model=StaffViewModel)
def GetStaffBySerialNumber(SerialNumber: str, db: Session = Depends(get_db),
                           Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    staff = Check_Staff_Authority_SerialNumber(db, current_user, SerialNumber)
    return staff


# 員工ID 取得員工臉列表DB (HRAccess)
@router.get("/staffs/{staff_id}/face", response_model=FaceViewModel)
def GetStaffFaceImageDB(staff_id: int, db: Session = Depends(get_db),
                        Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Staff_Authority(db, current_user, staff_id)
    return get_staff_face_images(db, staff_id)


# 員工ID 取得員工照片 回傳檔案 (HRAccess)
@router.get("/staffs/{staff_id}/faces")
def GetStaffFaceImage(staff_id: int, db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Staff_Authority(db, current_user, staff_id)
    return get_staff_face_image_file(db, staff_id)


# 員工ID 上傳員工照片 上傳檔案 & 刪除舊的資料 (HRAccess)
@router.post("/staffs/{staff_id}/faces", response_model=FaceViewModel)
def AddStaffFaceImagesAsync(staff_id: int, Image_file: UploadFile = File(...), db: Session = Depends(get_db),
                            Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Staff_Authority(db, current_user, staff_id)
    # 刪除舊的資料
    delete_staff_all_image(db, staff_id)

    return upload_face_file(db, staff_id, Image_file)


# 員工ID 修改員工資料 (HRAccess)
@router.patch("/staffs/{staff_id}", response_model=StaffViewModel)
def PatchStaffById(staff_id: int, staffPatch: StaffPatchModel, db: Session = Depends(get_db),
                   Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Staff_Authority(db, current_user, staff_id)
    return modefy_Staff_Info(db, staff_id, staffPatch)


# 創建 Staff (HR)
@router.post("/staffs", response_model=StaffViewModel)
def CreateStaff(staff_create: StaffPostModel, db: Session = Depends(get_db),
                Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if get_user_by_serveral_number_in_group(db, staff_create.serial_number, current_user.group_id):
        raise HTTPException(status_code=400, detail="Serveral_number already exist in this group")

    if not get_department_by_id(db, staff_create.department_id):
        raise HTTPException(status_code=400, detail="department id is not exist")

    return create_staff(db, staff_create, current_user.id, current_user.group_id)


# 員工ID 刪除員工 (HRAccess)
@router.delete("/staffs/{staff_id}", response_model=StaffViewModel)
def DeleteStaff(staff_id: int, db: Session = Depends(get_db),
                Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Staff_Authority(db, current_user, staff_id)
    delete_staff_all_image(db, staff_id)
    return delete_Staff_by_Staff_id(db, staff_id)


# 員工ID 上傳員工Feature (HRAccess)
@router.post("/staffs/{staff_id}/raw_face_features", response_model=StaffViewModel)
def Upload_Face_Feature(staff_id: int, feature: str, db: Session = Depends(get_db),
                        Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Staff_Authority(db, current_user, staff_id)


    result = upload_raw_face_feature(db, staff_id, feature)

    # 打一隻ＡＰＩ
    Headers = {"Authorization": "Bearer "+Authorize._token}
    r = requests.post(COMPUTE_URL+"/face_recongnition/update",
                      headers=Headers,
                      verify=False)
    # print(r.status_code)
    print(r.json())
    return result

# 員工ID 下載員工Feature (HRAccess)
@router.get("/staffs/{staff_id}/raw_face_features", response_model=FaceFeatureViewModel)
def Download_Face_Feature(staff_id: int, db: Session = Depends(get_db),
                          Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_Staff_Authority(db, current_user, staff_id)
    return download_raw_face_feature(db, staff_id)


########################################################################################################################
@router.get("/get-default-staff", response_model=StaffViewModel)
def GetDefaultStaff(db: Session = Depends(get_db)):
    return get_default_staff_id(db)


# # 員工ID 上傳員工照片 上傳檔案 & 刪除舊的資料 (HRAccess)
# @router.post("/staffs/{staff_id}/faces", response_model=FaceViewModel)
# def AddStaffFaceImagesAsync(staff_id: int, Image_file: UploadFile = File(...), db: Session = Depends(get_db),
#                             Authorize: AuthJWT = Depends()):
#     current_user = Authorize_user(Authorize, db)
#     check_Staff_Authority(db, current_user, staff_id)
#     # 刪除舊的資料
#     delete_staff_all_image(db, staff_id)
#     # 打一隻ＡＰＩ
#
#     r = requests.get( "http://127.0.0.1:8050/"+"face_recongnition/update/group/"+str(current_user.group_id), verify=False)
#     print(r.status_code)
#     return upload_face_file(db, staff_id, Image_file)