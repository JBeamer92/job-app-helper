from sqlalchemy.orm import Session

from data import models, schemas


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def add_posting(db: Session, posting: schemas.PostingCreate, user_id: int):
    new_posting = models.Posting(position=posting.position, company=posting.company, url=posting.url,
                                 events=posting.events, owner_id=user_id)
    db.add(new_posting)
    db.commit()
    db.refresh(new_posting)
    return new_posting


def delete_posting(db: Session, posting_id: int):
    posting = db.query(models.Posting).filter(models.Posting.id == posting_id).first()
    db.delete(posting)
    db.commit()
    # db.refresh()  # TODO: Do I need to refresh the user here?
    return posting_id


def get_posting_by_id(db: Session, posting_id: int):
    return db.query(models.Posting).filter(models.Posting.id == posting_id).first()


def update_posting(db: Session, posting: schemas.Posting):
    db.query(models.Posting).filter(models.Posting.id == posting.id).update({
        models.Posting.position: posting.position,
        models.Posting.company: posting.company,
        models.Posting.url: posting.url
    })
    db.commit()
    db.refresh(posting)
    return posting

