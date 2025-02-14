import os
from urllib.request import Request

from aiohttp_session import Session
from fastapi import FastAPI, Depends
from starlette.responses import RedirectResponse, HTMLResponse

import models
from database import engine
from routers import auth, todos
from starlette.staticfiles import StaticFiles

from routers.auth import get_current_user, get_db

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
# Define the upload directory

app.include_router(auth.router)
app.include_router(todos.router)
import sys
from typing import Optional

sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse

from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session


from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()



@app.get("/", response_class=HTMLResponse)
async def user_login_page(request: Request):
    return templates.TemplateResponse("user_login.html", {"request": request})

@app.get("/team", response_class=HTMLResponse)
async def get_todo_by_main(request: Request, main: str, db: Session = Depends(get_db)):
    # Query the database for the todo item with the specified main attribute
    todo = db.query(models.Todos).filter(models.Todos.main == main).first()

    if todo is None:
        return templates.TemplateResponse("error.html", {"request": request, "msg": "Todo not found"})

    # Render the userprofile.html template with the todo data
    return templates.TemplateResponse("userprofile.html", {"request": request, "todo": todo})