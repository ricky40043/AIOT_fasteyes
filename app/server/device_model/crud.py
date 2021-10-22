# crud
from sqlalchemy.orm import Session

from app.models.domain.device_model import device_model


def get_All_device_models(db: Session):
    return db.query(device_model).all()