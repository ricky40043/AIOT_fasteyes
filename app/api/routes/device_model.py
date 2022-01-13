from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session

from typing import List
from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.models.schemas.device_model import DeviceModelViewModel, DeviceModelPostModel, DeviceModelPatchModel
from app.server.authentication import Authority_Level, verify_password, checkLevel
from app.server.device_model.crud import get_All_device_models, create_device_models, modify_device_models, \
    get_device_model_by_name
router = APIRouter()


# 取得所有device model (RD)
@router.get("/device_model", response_model=List[DeviceModelViewModel])
def GetAllDevicesModel(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_All_device_models(db)


# 創建所有device model (RD)
@router.post("/device_model", response_model=DeviceModelViewModel)
def CreateDevicesModel(device_post: DeviceModelPostModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if get_device_model_by_name(db, DeviceModelPostModel.name):
        raise HTTPException(status_code=400, detail="name is exist")

    return create_device_models(db, device_post)


# 修改所有device model (RD)
@router.patch("/device_model/{device_model_id}", response_model=DeviceModelViewModel)
def ModifyDevicesModel(device_model_id: int, device_post: DeviceModelPatchModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return modify_device_models(db, device_model_id, device_post)

