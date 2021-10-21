# crud
from sqlalchemy.orm import Session

from app.models.domain.role import role


def get_All_roles(db: Session):
    return db.query(role).all()