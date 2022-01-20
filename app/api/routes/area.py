import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from typing import List, Optional

from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.models.schemas.area import Area_ViewModel, Area_UsersViewModel
from app.models.schemas.user import UserViewModel
from app.server.area.crud import create_area_user, delete_area_user_by_id, get_All_area_users, get_All_areas, \
    create_area, get_area_by_group_id, modify_area, delete_area_by_id, get_users_by_area_id, \
    delete_area_user_by_area_id, get_area_by_group_id_and_name, get_area_user_by_area_id_and_user_id, \
    delete_area_user_by_area_id_and_user_id
from app.server.authentication import Authority_Level, verify_password, checkLevel, get_tocken, get_email_token

router = APIRouter()


# 取得所有Area (RD)
@router.get("/area/GetAllArea", response_model=List[Area_ViewModel])
def GetAllArea(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_All_areas(db)


# 取得所有Area (User)
@router.get("/area", response_model=List[Area_ViewModel])
def GetArea(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.User.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_area_by_group_id(db, current_user.group_id)


# 創建Area (Admin)
@router.post("/area", response_model=Area_ViewModel)
def CreateArea(name: str,
               db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if get_area_by_group_id_and_name(db, current_user.group_id, name):
        raise HTTPException(status_code=400, detail="area name is exist")

    return create_area(db, current_user.group_id, name)


# 修改Area (Admin)
@router.patch("/area/{area_id}", response_model=Area_ViewModel)
def ModifyArea(area_id: int, name: Optional[str]=-1, send_mail: Optional[bool]=-1,
               db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")
    area_db = get_area_by_group_id_and_name(db, current_user.group_id, name)
    if area_db:
        if area_db.id != area_id:
            raise HTTPException(status_code=400, detail="area name is exist")

    return modify_area(db, area_id, name, send_mail)


# 刪除Area (Admin)
@router.delete("/area/{area_id}")
def DeleteArea(area_id: int,
               db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    delete_area_user_by_area_id(db, area_id)

    return delete_area_by_id(db, area_id)


########################################################################################################################
# 取得所有area_users (RD)
@router.get("/area_user/GetAllArea_users ", response_model=List[Area_UsersViewModel])
def GetArea_user(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_All_area_users(db)


# 取得area_users (User)
@router.get("/area_user", response_model=List[UserViewModel])
def GetArea_users(area_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.User.value):
        raise HTTPException(status_code=401, detail="權限不夠")
    return get_users_by_area_id(db, area_id)


# 創建area_users (Admin)
@router.post("/area_user", response_model=Area_UsersViewModel)
def CreateArea_users(area_id: int, user_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if get_area_user_by_area_id_and_user_id(db, area_id, user_id):
        raise HTTPException(status_code=204, detail="已經有了")

    return create_area_user(db, area_id, user_id)


@router.delete("/area_user")
def deleteArea_user(area_id: int, user_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return delete_area_user_by_area_id_and_user_id(db, area_id, user_id)
