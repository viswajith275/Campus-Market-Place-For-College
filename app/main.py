from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router
from app.core.exceptions import (
    BadRequest,
    Conflict,
    DetailedHTTPException,
    NotFound,
    UnAuthorized,
    exception_handler,
)

app = FastAPI()


app.mount(path="/static", app=StaticFiles(directory="static"), name="static")


app.add_exception_handler(DetailedHTTPException, exception_handler)
app.add_exception_handler(UnAuthorized, exception_handler)
app.add_exception_handler(NotFound, exception_handler)
app.add_exception_handler(Conflict, exception_handler)
app.add_exception_handler(BadRequest, exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://0.0.0.0:5173"],  # change this uri
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
