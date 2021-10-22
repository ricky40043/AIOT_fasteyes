from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app.models.domain.user import user
from app.server.authentication import get_user_by_email, checkLevel, Authority_Level
from app.server.staff.crud import get_staff_by_id, check_staff_id_by_group_id, get_staff_by_SerialNumber


def check_Staff_Authority(db: Session, current_user: user, staff_id: int):
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    staff = get_staff_by_id(db, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="staff is not exist")

    if not check_staff_id_by_group_id(db, staff_id, current_user.group_id):
        raise HTTPException(status_code=401, detail="staff id不在登入的使用者的group")

    return staff


def Check_Staff_Authority_SerialNumber(db: Session, current_user: user, SerialNumber: str):
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    staff = get_staff_by_SerialNumber(db, SerialNumber, current_user.group_id)
    if staff is None:
        raise HTTPException(status_code=404, detail="staff is not exist")

    return staff