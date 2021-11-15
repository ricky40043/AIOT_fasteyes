# crud
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.domain.Error_handler import UnicornException
from app.models.domain.bulletin_board import bulletin_board
from app.models.schemas.bulletin_board import Bulletin_boardPostModel, Bulletin_boardPatchModel


def get_All_bulletin_boards(db: Session):
    return db.query(bulletin_board).all()


def get_bulletin_board_by_id_and_group_id(db: Session, bulletin_board_id: int, group_id: int):
    bulletin_board_db = db.query(bulletin_board).filter(bulletin_board.id == bulletin_board_id,
                                                        bulletin_board.group_id == group_id).first()
    if bulletin_board_db is None:
        raise HTTPException(status_code=404, detail="bulletin_board_id is not exist or is not in this group")

    return bulletin_board_db


def create_bulletin_board(db: Session, group_id: int, bulletin_create: Bulletin_boardPostModel):
    db.begin()
    try:
        bulletin_board_db = bulletin_board(**bulletin_create.dict(), group_id=group_id)
        db.add(bulletin_board_db)
        db.commit()
        db.refresh(bulletin_board_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_bulletin_board.__name__, description=str(e), status_code=500)
    return bulletin_board_db


def modify_bulletin_board(db: Session, bulletin_board_id: int, group_id: int, bulletin_patch: Bulletin_boardPatchModel):
    bulletin_board_db = get_bulletin_board_by_id_and_group_id(db, bulletin_board_id, group_id)
    db.begin()
    try:
        bulletin_board_db.text = bulletin_patch.text
        bulletin_board_db.picture_name = bulletin_patch.picture_name
        bulletin_board_db.picture_or_text = bulletin_patch.picture_or_text
        bulletin_board_db.is_used = bulletin_patch.is_used
        bulletin_board_db.updated_at = datetime.now()
        db.commit()
        db.refresh(bulletin_board_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modify_bulletin_board.__name__, description=str(e), status_code=500)
    return bulletin_board_db


def delete_bulletin_board(db: Session, bulletin_board_id: int, group_id: int):
    bulletin_board_db = get_bulletin_board_by_id_and_group_id(db, bulletin_board_id, group_id)
    db.begin()
    try:
        db.delete(bulletin_board_db)
        db.commit()
        db.refresh(bulletin_board_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_bulletin_board.__name__, description=str(e), status_code=500)
    return bulletin_board_db