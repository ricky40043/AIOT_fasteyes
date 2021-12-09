from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.models.schemas.group import GroupViewModel, GroupPatchModel
from app.server.authentication import Authority_Level, verify_password, checkLevel, get_tocken, get_email_token
from app.server.group.crud import get_All_groups, create_group, get_group_by_name, get_group_by_id, group_modify_name, \
    delete_group_by_id

router = APIRouter()


# 取得所有Group (RD)
@router.get("/group/all", response_model=List[GroupViewModel])
def GetAllGroup(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_All_groups(db)


# 取得Group
@router.get("/group", response_model=GroupViewModel)
def GetGroupById(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    # if not checkLevel(current_user, Authority_Level.Admin.value):
    #     raise HTTPException(status_code=401, detail="權限不夠")

    return get_group_by_id(db, current_user.group_id)


# 修改Group (Admin)
@router.patch("/group", response_model=GroupViewModel)
def ModifyGroupName(group_patch: GroupPatchModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if get_group_by_name(db, group_patch.name):
        raise HTTPException(status_code=400, detail="group name is exist")

    return group_modify_name(db, current_user.group_id, group_patch)


# Delete Group (RD)
@router.get("/group", response_model=GroupViewModel)
def DeleteGroup(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return delete_group_by_id(db, current_user.group_id)


