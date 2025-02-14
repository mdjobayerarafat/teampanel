from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    todos = relationship("Todos", back_populates="owner")

class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Ensure autoincrement is set
    name = Column(String)
    position = Column(String)
    number = Column(String)
    main = Column(String)
    mail = Column(String)
    website = Column(String)
    github = Column(String)
    facebook = Column(String)
    webhook = Column(String)
    profile_picture = Column(String)
    complete = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey('users.id'))

    # Define the relationship to Users
    owner = relationship("Users", back_populates="todos")
