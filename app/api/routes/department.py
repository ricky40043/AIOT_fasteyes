from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session

from typing import List
from app.db.database import get_db
from app.helper.authentication import Authorize_user
from app.helper.department import check_department_Authority
from app.models.schemas.department import DepartmentViewModel, Department_staffViewModel, DepartmentPatchModel, \
    DepartmentPostModel
from app.server.authentication import Authority_Level, checkLevel
from app.server.department.crud import get_department_by_id, get_department_by_name, get_department_by_group_id, \
    create_department, get_department_staff_by_group_id, modify_department, Check_department_in_staffs, \
    delete_department_by_id

router = APIRouter()


# 公司ID 取得所有部門 (HRAccess)
@router.get("/department", response_model=List[DepartmentViewModel])
def Get_department(db: Session = Depends(get_db),
                   Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_department_by_group_id(db, current_user.group_id)


# 公司ID 取得所有部門和部門底下所有員工 (HRAccess)
@router.get("/department_staff", response_model=List[Department_staffViewModel])
def Get_department_staff(db: Session = Depends(get_db),
                         Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    return get_department_staff_by_group_id(db,current_user.group_id)


# 公司ID 新增部門 (HRAccess)
@router.post("/department", response_model=DepartmentViewModel)
def Create_department(department: DepartmentPostModel,
                      db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)

    if not checkLevel(current_user, Authority_Level.HRAccess.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    if get_department_by_name(db, current_user.group_id, department.name):
        raise HTTPException(status_code=400, detail="department name is exist")

    return create_department(db, current_user.group_id, department)


# 公司ID 修改部門 (HRAccess)
@router.patch("/department/{department_id}", response_model=DepartmentPatchModel)
def Modify_department(department_id: int,
                      department: DepartmentPatchModel,
                      db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_department_Authority(db, current_user, department_id)

    department_db = get_department_by_name(db, current_user.group_id, department.name)
    if department_db:
        raise HTTPException(status_code=400, detail="department name is exist")

    return modify_department(db, department_id, department)


# 公司ID 刪除部門 (HRAccess)
@router.delete("/department/{department_id}", response_model=DepartmentViewModel)
def Delete_department(department_id: int,
                      db: Session = Depends(get_db),
                      Authorize: AuthJWT = Depends()):
    current_user = Authorize_user(Authorize, db)
    check_department_Authority(db, current_user, department_id)

    if Check_department_in_staffs(db, department_id):
        raise HTTPException(status_code=400, detail="department is use in staffs")

    return delete_department_by_id(db, department_id)


@router.get("/department/{department_id}", response_model=DepartmentViewModel)
def Get_department_name(department_id: int,
                        db: Session = Depends(get_db),
                        Authorize: AuthJWT = Depends()):
    Authorize_user(Authorize, db)
    if not get_department_by_id(db, department_id):
        raise HTTPException(status_code=404, detail="department id is not exist")

    return get_department_by_id(db, department_id)
