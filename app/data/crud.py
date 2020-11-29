from sqlalchemy.orm import Session

from app.data import models, schemas


# TODO: Generate PyDocs for each method

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    # TODO: need actual hashing to be implemented here
    hashed_password = user.password + 'notsecureatallatm'
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_item(db: Session, item: schemas.ItemCreate, user_id: int):
    """
    :param db: Session
    :param item: schemas.ItemCreate
    :param user_id: int
    :return: models.Item
    """
    """
    Instead of passing each of the keyword arguments to Item and reading each one of them from the Pydantic model, 
    we are generating a dict with the Pydantic model's data with: item.dict()
    and then we are passing the dict's key-value pairs as the keyword arguments to the SQLAlchemy Item, with:
    Item(**item.dict())
    And then we pass the extra keyword argument owner_id that is not provided by the Pydantic model, with:
    Item(**item.dict(), owner_id=user_id)
    """
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
