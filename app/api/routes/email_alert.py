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
from app.server.area.crud import create_area_user, delete_area_user_by_id, get_All_area_users, get_All_areas
from app.server.authentication import Authority_Level, verify_password, checkLevel, get_tocken, get_email_token

router = APIRouter()


# 取得所有email_alert (RD)
@router.get("/area/GetAllarea", response_model=List[Area_ViewModel])
def GetAllEmail_alert(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_All_areas(db)


# 取得所有email_alert_users (RD)
@router.get("/area_user/GetAllarea_users ", response_model=List[Area_UsersViewModel])
def GetEmail_alert_user(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_All_area_users(db)


@router.post("/area_user", response_model=Area_UsersViewModel)
def GetAllUsers(email_alert_id:int, user_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return create_area_user(db, email_alert_id, user_id)


@router.delete("/area_user", response_model=Area_UsersViewModel)
def GetAllUsers(email_alert_user_id:int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return delete_area_user_by_id(db, email_alert_user_id)