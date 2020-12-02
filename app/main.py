from datetime import timedelta, datetime


from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging

from app.data import crud, models, schemas
from app.data.database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "a68e0c8365ec2ec1c5502508920dc4ff55b5af71c0029ffdaa7c3cc810cc205e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30

app = FastAPI()


# Dependency, TODO: Should probably move this somewhere else
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# APPLICATIONS


@app.get("/apps")
def get_apps():
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
        "id": 4,
        "company": "Kindred",
        "position": "Programmer Analyst",
        "url": "www.sample.com",
        "status": "SENT"
    }]


@app.post("/apps")
def create_apps():
    # TODO: implement this method
    print('I created some apps!')


# ITEMS


# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items


@app.get("/items/")
def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


# USER MANAGEMENT


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = get_user(email=token_data.email, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Not an active user.')
    return current_user


@app.post('/users/', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(email=user.email, db=db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_pw = pwd_context.hash(user.password)
    return crud.create_user(db=db, user=user, hashed_password=hashed_pw)


@app.get('/users/', response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(skip=skip, limit=limit, db=db)


@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_item(db=db, item=item, user_id=user_id)


# TOKEN MANAGEMENT


@app.post('/token', response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = authenticate_user(db=db, email=form_data.username, password=form_data.password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password.",
                            headers={'WWW-Authenticate': 'Bearer'})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token(
        data={'sub': db_user.email}, expires_delta=access_token_expires
    )

    return {'access_token': access_token, 'token_type': 'bearer'}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(email: str, db: Session):
    return crud.get_user_by_email(db=db, email=email)


def authenticate_user(email: str, password: str, db: Session):
    user = get_user(email=email, db=db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


if __name__ == '__main__':
    import uvicorn
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, log_config=None)
