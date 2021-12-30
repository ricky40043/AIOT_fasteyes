from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.models.schemas.bulletin_board import Bulletin_boardViewModel, Bulletin_boardPostModel, Bulletin_boardPatchModel
from app.server.authentication import Authority_Level, verify_password, checkLevel, get_tocken, get_email_token
from app.server.bulletin_board import get_bulletin_image_file
from app.server.bulletin_board.crud import get_bulletin_board_by_group_id, create_bulletin_board, \
    delete_bulletin_board, upload_Bulletin_file, delete_Bulletin_file

router = APIRouter()


# 取得佈告欄 (Admin)
@router.get("/bulletin", response_model=Bulletin_boardViewModel)
def GetBulletin(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.User.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_bulletin_board_by_group_id(current_user.group_id)


# 取得佈告欄 (Admin)
@router.get("/bulletin/image")
def GetBulletin(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.User.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_bulletin_image_file(db, current_user.group_id)


# 修改佈告欄 (Admin)
@router.patch("/bulletin", response_model=Bulletin_boardViewModel)
def ModifyBulletin(Image_file: UploadFile = File(...),
                   db: Session = Depends(get_db),
                   Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    # 覆蓋舊的資料
    return upload_Bulletin_file(db, current_user.group_id, Image_file)


# 刪除佈告欄 (Admin)
@router.delete("/bulletin/image", response_model=Bulletin_boardViewModel)
def GetBulletin(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return delete_Bulletin_file(db, current_user.group_id)

# # 取得佈告欄 (Admin)
# @router.get("/bulletin/{bulletin_id}", response_model=Bulletin_boardViewModel)
# def GetBulletin(bulletin_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     current_user = Authorize_user(Authorize, db)
#
#     if not checkLevel(current_user, Authority_Level.Admin.value):
#         raise HTTPException(status_code=401, detail="權限不夠")
#
#     return get_bulletin_board_by_id_and_group_id(db, bulletin_id, current_user.group_id)
#
#
# # 新增佈告欄 (Admin)
# @router.post("/bulletin", response_model=Bulletin_boardViewModel)
# def GreateBulletin(bulletin_create: Bulletin_boardPostModel, db: Session = Depends(get_db),
#                 Authorize: AuthJWT = Depends()):
#     current_user = Authorize_user(Authorize, db)
#
#     if not checkLevel(current_user, Authority_Level.Admin.value):
#         raise HTTPException(status_code=401, detail="權限不夠")
#
#     return create_bulletin_board(db, current_user.group_id, bulletin_create)
#
#
# # 修改佈告欄 (Admin)
# @router.patch("/bulletin/{bulletin_id}", response_model=Bulletin_boardViewModel)
# def ModifyBulletin(bulletin_patch: Bulletin_boardPatchModel, bulletin_id: int, db: Session = Depends(get_db),
#                 Authorize: AuthJWT = Depends()):
#     current_user = Authorize_user(Authorize, db)
#
#     if not checkLevel(current_user, Authority_Level.Admin.value):
#         raise HTTPException(status_code=401, detail="權限不夠")
#
#     return modify_bulletin_board(db, bulletin_id, current_user.group_id, bulletin_patch)
#
#
# # 刪除佈告欄 (Admin)
# @router.get("/bulletin/{bulletin_id}", response_model=Bulletin_boardViewModel)
# def DeleteBulletin(bulletin_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     current_user = Authorize_user(Authorize, db)
#
#     if not checkLevel(current_user, Authority_Level.Admin.value):
#         raise HTTPException(status_code=401, detail="權限不夠")
#
#     return delete_bulletin_board(db, bulletin_id, current_user.group_id)
