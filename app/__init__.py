import logging

from fastapi import FastAPI

from app.api.routes.api import router as api_router
from app.db.database import engine, Base
from starlette.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from starlette.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:8080",
    "*"
]


def create_app():
    app = FastAPI()
    # app.host = "localhost/127.0.0.1"
    # app.port = "8080"
    # app.servers ={"url": "https://localhost/127.0.0.1", "description": "Staging environment"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    app.include_router(api_router)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    add_pagination(app)
    return app
