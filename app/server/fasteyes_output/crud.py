# crud
from sqlalchemy.orm import Session

from app.models.domain.fasteyes_output import fasteyes_output


def get_All_fasteyes_outputs(db: Session):
    return db.query(fasteyes_output).all()