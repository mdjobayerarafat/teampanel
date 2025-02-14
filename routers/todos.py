import logging
import os
import sys
from typing import Optional


sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse

from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user

from fastapi import Depends, APIRouter, Request, Form, File, UploadFile, HTTPException

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}}
)
# Define the upload directory
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    # No authentication check for this endpoint
    todos = db.query(models.Todos).all()  # Show all todos (or filter as needed)
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})

@router.get("/admin", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()

    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "todos": todos, "user": user})
@router.get("/add-member", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})


@router.post("/add-member", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    name: str = Form(...),
    position: str = Form(...),
    number: str = Form(...),
    main: str = Form(...),
    webhook: Optional[str] = Form(None),
    profile_picture: Optional[str] = Form(None),  # Changed to accept a string (URL)
    mail: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    facebook: Optional[str] = Form(None),
    github: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    # No need to handle file uploads; directly use the provided URL
    profile_picture_url = profile_picture  # Use the provided URL directly

    # Create the todo model
    todo_model = models.Todos()
    todo_model.name = name
    todo_model.position = position
    todo_model.number = number
    todo_model.main = main
    todo_model.mail = mail
    todo_model.website = website
    todo_model.github = github
    todo_model.facebook = facebook
    todo_model.webhook = webhook
    todo_model.profile_picture = profile_picture_url  # Assign the URL directly
    todo_model.complete = False
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/teams/admin", status_code=status.HTTP_302_FOUND)

@router.get("/edit-member/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})


@router.post("/edit-member/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(
    request: Request,
    todo_id: int,
    name: str = Form(...),
    position: str = Form(...),
    number: str = Form(...),
    main: str = Form(...),
    webhook: Optional[str] = Form(None),
    profile_picture: Optional[str] = Form(None),  # Changed to accept a string (URL)
    mail: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    facebook: Optional[str] = Form(None),
    github: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    # Update the profile picture URL directly
    if profile_picture:
        todo_model.profile_picture = profile_picture  # Assign the URL directly

    # Update the todo model
    todo_model.name = name
    todo_model.position = position
    todo_model.number = number
    todo_model.main = main
    todo_model.mail = mail
    todo_model.website = website
    todo_model.github = github
    todo_model.facebook = facebook
    todo_model.webhook = webhook

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/teams/admin", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return RedirectResponse(url="/teams/admin", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo.complete = not todo.complete

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/teams", status_code=status.HTTP_302_FOUND)

@router.get("/user_login", response_class=HTMLResponse)
async def user_login_page(request: Request):
    return templates.TemplateResponse("user_login.html", {"request": request})

@router.get("/teams", response_class=HTMLResponse)
async def get_todo_by_main(request: Request, main: str, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.main == main).first()
    logging.debug(f"Todo: {todo}")

    if todo is None:
        return templates.TemplateResponse("error.html", {"request": request, "msg": "Todo not found", "user": user})

    return templates.TemplateResponse("userprofile.html", {"request": request, "todo": todo, "user": user})


