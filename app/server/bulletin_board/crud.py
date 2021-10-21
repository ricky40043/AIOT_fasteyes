# crud
from sqlalchemy.orm import Session

from app.models.domain.bulletin_board import bulletin_board


def get_All_bulletin_boards(db: Session):
    return db.query(bulletin_board).all()