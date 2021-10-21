# crud
from sqlalchemy.orm import Session

from app.models.domain.Error_handler import UnicornException
from app.models.domain.department import department
from app.models.domain.group import group
from app.models.domain.staff import staff
from app.models.schemas.department import DepartmentPostModel, DepartmentPatchModel


def get_All_departments(db: Session):
    return db.query(department).all()


def get_department_by_group_id(db: Session, group_id: int):
    return db.query(department).filter(department.group_id == group_id).all()


def get_department_by_id(db: Session, department_id):
    return db.query(department).filter(department.id == department_id).first()


def get_department_by_id_and_group_id(db: Session, department_id: int, group_id: int):
    return db.query(department).filter(department.id == department_id, department.group_id == group_id).first()


def get_department_by_name(db: Session, group_id: int, name: str):
    return db.query(department).filter(department.group_id == group_id,
                                       department.name == name).first()


def create_department(db: Session, group_id: int, DepartmentIn: DepartmentPostModel):
    db.begin()
    try:
        db_department = department(**DepartmentIn.dict(), group_id=group_id)
        db.add(db_department)
        db.commit()
        db.refresh(db_department)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_department.__name__, description=str(e), status_code=500)
    return db_department


def get_department_staff_by_group_id(db: Session, group_id: int):
    department_db = db.query(department).filter(department.group_id == group_id).all()
    department_list = []

    # ricky N+1 之後要改掉
    for department_each in department_db:
        department_dict = department_each.to_dict()
        department_dict["member"] = []
        staff_list = db.query(staff).filter(staff.department_id == department_each.id).all()
        department_dict["member"] = staff_list
        department_list.append(department_dict)
    return department_list


def modify_department(db: Session,department_id: int, departmentIn: DepartmentPatchModel):
    Department_db = db.query(department).filter(department.id == department_id).first()

    db.begin()
    try:
        Department_db.name = departmentIn.name
        db.commit()
        db.refresh(Department_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modify_department.__name__, description=str(e), status_code=500)
    return Department_db


def Check_department_in_staffs(db: Session, department_id):
    return db.query(staff).filter(staff.department_id == department_id).all()


def delete_department_by_id(db: Session, department_id):
    Department_db = db.query(department).filter(department.id == department_id).first()
    db.begin()
    try:
        db.delete(Department_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_department_by_id.__name__, description=str(e), status_code=500)
    return Department_db