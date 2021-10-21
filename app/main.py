from app import create_app

from app.db.database import get_db
from app.models.domain.Error_handler import Error_handler, UnicornException
from requests import Request
from starlette.responses import JSONResponse, FileResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

app = create_app()


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    # 紀錄到Table
    db = next(get_db())
    db.begin()
    db_Error_handler = Error_handler(name=exc.name,
                                     description=exc.description,
                                     status_code=exc.status_code)
    db.add(db_Error_handler)
    db.commit()
    db.refresh(db_Error_handler)
    return JSONResponse(
        status_code=exc.status_code,
        content={"function_name": exc.name,
                 "description": exc.description}
    )


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    # 紀錄到Table
    db = next(get_db())
    db.begin()
    db_Error_handler = Error_handler(name="AuthJWTException",
                                     description=exc.message,
                                     status_code=exc.status_code)
    db.add(db_Error_handler)
    db.commit()
    db.refresh(db_Error_handler)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
