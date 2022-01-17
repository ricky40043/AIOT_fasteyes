import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from typing import List, Optional

from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.models.schemas.user import UserViewModel, UserPostViewModel, adminUserPostViewModel, UserPatchInfoModel, \
    UserPatchPasswordViewModel, UserChangeSettingModel, UserInviteViewModel
from app.server.area.crud import delete_area_user_by_user_id
from app.server.authentication import Authority_Level, verify_password, checkLevel, get_tocken, get_email_token
from app.server.bulletin_board.crud import create_bulletin_board
from app.server.fasteyes_observation import create_output_data_form
from app.server.group.crud import get_All_groups, create_group, get_group_by_name
from app.server.send_email import send_invite_mail
from app.server.user.crud import Create_User, get_user_by_email, get_user_by_name, get_All_users, check_Email_Exist, \
    modefy_User, get_user_by_name_in_group, modefy_User_Password, change_user_setting, change_user_verify_code_enable, \
    get_users_in_group, get_user_by_id, delete_group_by_group_id, check_user_owner, delete_user_by_user_id

from starlette.templating import Jinja2Templates
from starlette.requests import Request

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# 取得所有User (RD)
@router.get("/users/GetAllUsers", response_model=List[UserViewModel])
def GetAllUsers(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_All_users(db)


# 取得所有User
@router.get("/users", response_model=List[UserViewModel])
def GetAllUsers(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    # if not checkLevel(current_user, Authority_Level.Admin.value):
    #     raise HTTPException(status_code=401, detail="權限不夠")

    return get_users_in_group(db, current_user.group_id)


# check Email
@router.get("/users/email/exists")
def UserExists(email: str, db: Session = Depends(get_db)):
    if check_Email_Exist(db, email):
        return "Email is exist"


# user id 修改 User Info(HRAccess)
@router.patch("/users/info", response_model=UserViewModel)
def PatchUserInfo(userPatch: UserPatchInfoModel,
                  db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    user_db = get_user_by_name_in_group(db, userPatch.name, current_user.group_id)
    if user_db:
        if user_db.id != current_user.id:
            raise HTTPException(status_code=400, detail="Name already exist in this group")

    return modefy_User(db, current_user, userPatch)


# user id 修改 密碼 (HRAccess)
@router.patch("/users/password", response_model=UserViewModel)
def PatchUserPassword(userPatch: UserPatchPasswordViewModel, db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not verify_password(userPatch.old_password, current_user.password):
        raise HTTPException(status_code=401, detail="舊密碼錯誤")

    return modefy_User_Password(db, current_user.id, userPatch)


# user id 修改 User setting (HRAccess)
@router.patch("/users/setting", response_model=UserViewModel)
def PatchUserSetting(userPatch: UserChangeSettingModel,
                     db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    return change_user_setting(db, current_user.id, userPatch)


# user id 修改 User verify_code_enable (HRAccess)
@router.patch("/users/verify_code_enable", response_model=UserViewModel)
def PatchUserVerify_code_enable(verify_code_enable: bool, db: Session = Depends(get_db),
                                Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    return change_user_verify_code_enable(db, current_user.id, verify_code_enable)


# 刪除 user (Admin)
@router.delete("/users/{user_id}", response_model=UserViewModel)
def DeleteUser(user_id: int,
               db: Session = Depends(get_db),
               Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    delete_user = get_user_by_id(db, user_id)
    if not delete_user:
        raise HTTPException(status_code=400, detail="user 不存在")

    check_user_owner(db, user_id, current_user.group_id)

    # 不可以刪除跟你同等或比你高的權限
    if delete_user.level <= current_user.level:
        raise HTTPException(status_code=401, detail="權限不夠")

    delete_area_user_by_user_id(db, delete_user.id)

    return delete_user_by_user_id(db, delete_user.id)


# 邀請 User 發信 (Admin)
@router.post("/users/invite")
def InivteUser(user_invite: UserInviteViewModel, background_tasks: BackgroundTasks,
               db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    if get_user_by_email(db, email=user_invite.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    current_user = Authorize_user(Authorize, db)
    if user_invite.level < 2 or user_invite.level > 4:
        raise HTTPException(status_code=400, detail="權限 level 請輸入 2~4")
    # 寄信
    token_data = send_invite_mail(user_invite.email, user_invite.level, current_user.group_id,
                                  background_tasks=background_tasks)
    with open(os.getcwd() + '/Auto/Default/User_data/invite_token.txt', 'w') as token:
        token.write(token_data)
    return "send invite mail"


# User verify
@router.get("/users/verify/{token}")
def InivteUserVerify(token: str, request: Request, db: Session = Depends(get_db)):
    data = get_email_token(token)

    if get_user_by_email(db, email=data["email"]):
        raise HTTPException(status_code=400, detail="Email already registered")

    return templates.TemplateResponse("user_create.html", {"request": request, "email": data["email"], "token": token})


# 創建 User
@router.post("/users/create/{token}", response_model=UserViewModel)
def CreateUser(user_create: UserPostViewModel, token: str,
               db: Session = Depends(get_db)):
    if get_user_by_email(db, email=user_create.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    data = get_email_token(token)
    print(data["level"])
    if data["email"] != user_create.email:
        raise HTTPException(status_code=400, detail="Email and regist_email are different")

    user_db = Create_User(db, user_create, data["group_id"], data["level"])
    return user_db


########################################################################################################################
# 創建 admin User (RD)
@router.post("/users/admin", response_model=UserViewModel)
def CreateAdminUser(user_create: adminUserPostViewModel, db: Session = Depends(get_db)):
    if get_user_by_email(db, email=user_create.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    if get_group_by_name(db, group_name=user_create.group.name):
        raise HTTPException(status_code=400, detail="Group name already exist")

    group_db = create_group(db, user_create.group)
    user_db = Create_User(db, user_create, group_db.id, level=Authority_Level.Admin.value, is_enable=True)
    create_output_data_form(group_db.id)
    create_bulletin_board(db, user_db.group_id)

    return user_db


# 創建 RD User (RD)
@router.post("/users/RD", response_model=UserViewModel)
def CreateRDUser(user_create: adminUserPostViewModel, db: Session = Depends(get_db)):
    if get_user_by_email(db, email=user_create.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    if get_user_by_name(db, name=user_create.name):
        raise HTTPException(status_code=400, detail="Name already exist")

    if get_group_by_name(db, group_name=user_create.group.name):
        raise HTTPException(status_code=400, detail="Group name already exist")

    group_db = create_group(db, user_create.group)
    user_db = Create_User(db, user_create, group_db.id, level=Authority_Level.RD.value, is_enable=True)
    return user_db


# 刪除Admin user ＆ group (RD)
@router.delete("/users/admin/{user_id}")
def DeleteAdminUser(user_id: int, db: Session = Depends(get_db),
                    Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    delete_user = get_user_by_id(db, user_id)

    if delete_user.level != Authority_Level.Admin.value:
        raise HTTPException(status_code=400, detail="此user 不是 Admin user")

    if not delete_user:
        raise HTTPException(status_code=400, detail="user 不存在")

    # 不可以刪除跟你同等或比你高的權限
    if delete_user.level <= current_user.level:
        raise HTTPException(status_code=401, detail="權限不夠")


    #刪除所有 fasteyes observation & fasteyes

    #刪除所有 device & observation

    #刪除所有 staff & face

    #刪除fasteyes output

    #刪除佈告欄


    #刪除所有user

    #刪除group
    return delete_group_by_group_id(db, delete_user.group_id)


#################################################################################################
# # TEST
# @router.post("/Test")
# def Test_get_ALL(db: Session = Depends(get_db)):
#     get_All_roles(db)
#     get_All_groups(db)
#     get_All_users(db)
#     get_All_staffs(db)
#     get_All_devices(db)
#     get_All_departments(db)
#     get_All_observations(db)
#     get_All_faces(db)
#     get_All_device_models(db)
#     get_All_fasteyes_devices(db)
#     get_All_fasteyes_observations(db)
#     get_All_fasteyes_uuids(db)
#     get_All_fasteyes_outputs(db)
#     return "Done"


# 取得User by id (RD)
@router.get("/users/{users_id}", response_model=UserViewModel)
def GetAllUsers(users_id: int, db: Session = Depends(get_db),
                Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.RD.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_user_by_id(db, users_id)
