from sqlalchemy.orm import Session

from app.data import models, schemas


# TODO: Generate PyDocs for each method


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_application(db: Session, application: schemas.ApplicationCreate, user_id: int):
    db_app = models.Application(position=application.position, company=application.company, owner_id=user_id)
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

