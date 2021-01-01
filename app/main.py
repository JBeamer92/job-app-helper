import logging
from datetime import timedelta, datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from data import crud, models, schemas
from data.database import SessionLocal, engine

# Initialize DB
models.Base.metadata.create_all(bind=engine)

# Security Stuff
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "a68e0c8365ec2ec1c5502508920dc4ff55b5af71c0029ffdaa7c3cc810cc205e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30

# Build the darn thing
app = FastAPI()

# Allow CORS for communication with front-end
origins = [
    'http://localhost:8080'
]

app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=['*'], allow_headers=['*']
)


# Dependency, TODO: Should probably move this somewhere else
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


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


# POSTING MANAGEMENT


@app.get("/postings", response_model=List[schemas.Posting])
async def get_postings(
        current_user: models.User = Depends(get_current_active_user)):
    if current_user:
        return current_user.postings


@app.post("/postings", response_model=schemas.Posting)
async def add_posting(
        posting: schemas.PostingCreate,
        current_user: models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)):
    if current_user:
        new_posting = models.Posting(position=posting.position, company=posting.company, url=posting.url)
        # events_list = []
        # for event in posting.events:
        #     events_list.append(models.Event(name=event.name, date=event.date))
        # new_posting.events = events_list

        return crud.add_posting(db=db, posting=new_posting, user_id=current_user.id)


@app.delete("/postings/{posting_id}")
async def delete_posting(posting_id: int, current_user: models.User = Depends(get_current_active_user),
                         db: Session = Depends(get_db)):
    if current_user:
        crud.delete_posting(posting_id=posting_id, db=db)
        return {"message": f"Deleting posting with ID:  {posting_id}"}


@app.put("/postings")
async def update_posting(posting: schemas.PostingUpdate, current_user: models.User = Depends(get_current_active_user),
                         db: Session = Depends(get_db)):
    if current_user:
        db_post = crud.get_posting_by_id(db=db, posting_id=posting.id)
        db_post.position = posting.position
        db_post.company = posting.company
        db_post.url = posting.url
        crud.update_posting(posting=db_post, db=db)
        return {"message": f"Updating posting with ID:  {posting.id}"}


if __name__ == '__main__':
    import uvicorn
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run('main:app', host='0.0.0.0', port=8000, log_config=None)
