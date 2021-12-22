from app import create_app
from app.core.config import PORT, HOST_IP

from app.db.database import get_db
from app.models.domain.Error_handler import Error_handler, UnicornException
from requests import Request
from starlette.responses import JSONResponse, FileResponse
from fastapi_jwt_auth.exceptions import AuthJWTException
import asyncio
from app.server.temperature_humidity_device import MyUDPProtocol




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


@app.on_event("startup")
async def on_startup() -> None:
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: MyUDPProtocol(), local_addr=(HOST_IP, PORT)
    )
    app.state.udp_transport = transport
    app.state.udp_protocol = protocol


# pcs = set()
# args = ''


@app.on_event("shutdown")
async def on_shutdown() -> None:
    app.state.udp_transport.close()
    # coros = [pc.close() for pc in pcs]
    # await asyncio.gather(*coros)
    # pcs.clear()



