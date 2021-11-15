# crud
from datetime import datetime
from http.client import HTTPException

from sqlalchemy.orm import Session

from app.models.domain.Error_handler import UnicornException
from app.models.domain.fasteyes_output import fasteyes_output
from app.models.schemas.fasteyes_output import FasteyesOutputPatchViewModel


def get_All_fasteyes_outputs(db: Session):
    return db.query(fasteyes_output).all()


def get_fasteyes_outputs_by_id(db: Session, group_id: int):
    return db.query(fasteyes_output).filter(fasteyes_output.group_id == group_id).first()


def fasteyes_output_modify(db: Session, group_id: int, userPatch: FasteyesOutputPatchViewModel):
    fasteyes_output_db = db.query(fasteyes_output).filter(fasteyes_output.group_id == group_id).first()
    if fasteyes_output_db is None:
        raise HTTPException(status_code=404, detail="user not exist")
    db.begin()
    try:
        fasteyes_output_db.updated_at = datetime.now()
        fasteyes_output_db.time = userPatch.time
        fasteyes_output_db.name = userPatch.name
        fasteyes_output_db.department = userPatch.department
        fasteyes_output_db.observation_ID = userPatch.observation_ID
        fasteyes_output_db.wear_mask = userPatch.wear_mask
        fasteyes_output_db.temperature = userPatch.temperature
        fasteyes_output_db.threshold_temperature = userPatch.threshold_temperature
        fasteyes_output_db.compensate_temperature = userPatch.compensate_temperature
        fasteyes_output_db.device_ID = userPatch.device_ID
        fasteyes_output_db.result = userPatch.result
        fasteyes_output_db.output_time = userPatch.output_time
        db.commit()
        db.refresh(fasteyes_output_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=fasteyes_output_modify.__name__, description=str(e), status_code=500)
    return fasteyes_output_db


def create_fasteyes_output(db: Session, user_id: int, group_id: int):
    db.begin()
    try:
        db_fasteyes_output = fasteyes_output(user_id, group_id)
        db.add(db_fasteyes_output)
        db.commit()
        db.refresh(db_fasteyes_output)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_fasteyes_output.__name__, description=str(e), status_code=500)
    return db_fasteyes_output
