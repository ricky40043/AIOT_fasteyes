# crud
from sqlalchemy.orm import Session

from app.models.domain.Error_handler import UnicornException
from app.models.domain.group import group
from app.models.schemas.group import GroupPostModel


def get_All_groups(db: Session):
    return db.query(group).all()


def get_group_by_name(db: Session, group_name):
    return db.query(group).filter(group.name == group_name).first()


def create_group(db: Session, group_create: GroupPostModel):
    db.begin()
    try:
        db_group = group(**group_create.dict())
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_group.__name__, description=str(e), status_code=500)
    return db_group
