from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app.models.domain.user import user
from app.server.authentication import get_user_by_email, checkLevel, Authority_Level
from app.server.device.crud import get_device_by_id, check_device_owner, get_device_by_id_and_group_id


def check_Device_Authority(db: Session, current_user: user, device_id: int):
    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if get_device_by_id(db, device_id) is None:
        raise HTTPException(status_code=404, detail="device is not exist")

    device = check_device_owner(db, device_id, current_user.id)
    if device is None:
        raise HTTPException(status_code=401, detail="你不是裝置的使用者")

    return device


def check_Device_Upload_Authority(db: Session, current_user: user, device_id: int):
    if not checkLevel(current_user, Authority_Level.User.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if get_device_by_id(db, device_id) is None:
        raise HTTPException(status_code=404, detail="device is not exist")

    device = get_device_by_id_and_group_id(db, device_id, current_user.group_id)
    if device is None:
        raise HTTPException(status_code=401, detail="裝置不在你的群組底下")

    return device


