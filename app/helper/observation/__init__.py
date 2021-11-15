from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app.models.domain.user import user
from app.server.authentication import get_user_by_email, checkLevel, Authority_Level
from app.server.observation.crud import get_observation_by_id, check_observation_ownwer


def check_observation_Authority(db: Session, current_user: user, observation_id: int):
    if not checkLevel(current_user, Authority_Level.Admin.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if get_observation_by_id(db, observation_id) is None:
        raise HTTPException(status_code=404, detail="observation_id is not exist")

    observation = check_observation_ownwer(db, observation_id, current_user.group_id)
    if observation is None:
        raise HTTPException(status_code=401, detail="你不是觀測結果的擁有者")

    return observation
