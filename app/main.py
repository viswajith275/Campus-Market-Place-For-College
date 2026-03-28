import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router
from app.core.config import settings
from app.core.exceptions import (
    BadRequest,
    Conflict,
    DetailedHTTPException,
    NotFound,
    exception_handler,
)

app = FastAPI()

abs_path = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.join(abs_path, settings.upload_directory)
os.makedirs(new_path, exist_ok=True)

app.mount(path="/app/static", app=StaticFiles(directory="app/static"), name="static")


app.add_exception_handler(DetailedHTTPException, exception_handler)
app.add_exception_handler(NotFound, exception_handler)
app.add_exception_handler(Conflict, exception_handler)
app.add_exception_handler(BadRequest, exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],  # change thisuvi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
