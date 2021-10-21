from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app.models.domain.user import user
from app.server.authentication import get_user_by_email, checkLevel, Authority_Level
from app.server.department.crud import get_department_by_id, get_department_by_id_and_group_id


def check_department_Authority(db: Session, current_user: user, department_id: int):
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if not get_department_by_id(db, department_id):
        raise HTTPException(status_code=404, detail="department id not exist")

    return get_department_by_id_and_group_id(db, department_id, current_user.group_id)
