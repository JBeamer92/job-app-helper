from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Eventually, I should add this to a config that loads in at runtime for prod/dev DBs.
SQLALCHEMY_DATABASE_URL = 'sqlite:///./data/app.db'

# connect_args is only needed for SQL Lite. There's got to be a way to add this to configs as well.
# see docs on why this param is needed for FastAPI: https://fastapi.tiangolo.com/tutorial/sql-databases/
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)
# Each instance of this will be a DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This class will be inherited from in each of the ORM models
Base = declarative_base()
