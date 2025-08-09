from sqlalchemy.orm import Session
from . import models

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, password_hash: str):
    user = models.User(username=username, hashed_password=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
