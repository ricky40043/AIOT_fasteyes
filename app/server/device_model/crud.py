# crud
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.domain.Error_handler import UnicornException
from app.models.domain.device_model import device_model
from app.models.schemas.device_model import DeviceModelPostModel, DeviceModelPatchModel


def get_All_device_models(db: Session):
    return db.query(device_model).all()


def get_device_model_by_name(db: Session, name: str):
    return db.query(device_model).filter(device_model.name == name).first()


def create_device_models(db: Session, device_post: DeviceModelPostModel):
    db.begin()
    try:
        device_model_db = device_model(**device_post.dict())
        db.add(device_model_db)
        db.commit()
        db.refresh(device_model_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_device_models.__name__, description=str(e), status_code=500)
    return device_model_db


def modify_device_models(db: Session, device_model_id: int, device_patch: DeviceModelPatchModel):
    device_model_db = db.query(device_model).filter(device_model.id == device_model_id).first()
    db.begin()
    try:
        device_model_db.name = device_patch.name
        device_model_db.updated_at = datetime.now()
        db.commit()
        db.refresh(device_model_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_device_models.__name__, description=str(e), status_code=500)
    return device_model_db
