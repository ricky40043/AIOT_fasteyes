# crud
from sqlalchemy.orm import Session

from app.models.domain.device import device


def get_All_devices(db: Session):
    return db.query(device).all()