import uvicorn
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .data import crud, models, schemas
from .data.database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


# Dependency, TODO: Should probably move this somewhere else
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/apps")
async def get_apps():
    # TODO: require authentication
    # TODO: implement this method
    return [{
        "id": 1,
        "company": "Anthem",
        "position": "Developer",
        "url": "www.sample.com",
        "status": "SENT"
    }, {
        "id": 2,
        "company": "Kindred",
        "position": "Programmer Analyst",
        "url": "www.sample.com",
        "status": "SENT"
    }, {
        "id": 3,
        "company": "Fusion",
        "position": "Programmer Analyst",
        "url": "www.sample.com",
        "status": "SENT"
    }, {
        "id": 4 ,
        "company": "Kindred",
        "position": "Programmer Analyst",
        "url": "www.sample.com",
        "status": "SENT"
    }]


@app.post("/apps")
async def create_apps():
    # TODO: implement this method
    print('I created some apps!')


@app.post('/users/', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(email=user.email, db=db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    return crud.create_user(db=db, user=user)


@app.get('/users/{user_id}', response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found.")


@app.get('/users/', response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(skip=skip, limit=limit, db=db)


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items


@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


def fake_decode_token(token):
    return schemas.User(
        email="john@example.com"
    )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    return user


@app.get("/users/me")
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port='8000')
