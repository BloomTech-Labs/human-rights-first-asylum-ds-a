"""Database functions"""

from typing import List, Optional 
import os
import databases
from sqlalchemy import delete, insert, update, Table, MetaData, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.sql import select
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
import sqlalchemy

# SQLAlchemy specific code, as with any other app
# DATABASE_URL = "postgresql://user:password@postgresserver/db"
database_url = os.getenv('DATABASE_URL')
engine = sqlalchemy.create_engine(database_url) # to use with Postgres

# use the two lines below to use the sqlite test database
# #DATABASE_URL = "sqlite:///./test.db"
# engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # to use with sqlite change back `database_url` when switching back to postgres DB

# the block below creates the database table
meta = MetaData() # not sure if need `bind=engine` inside the `MetaData` object

cases = Table('cases', meta,
    Column('case_id', Integer, primary_key=True),
    Column('user_id', String),
    Column('docs_public', Boolean),
    Column('case_title', String),
    Column('case_number', String),
    Column('judge_name', String),
    Column('outcome', String),
    Column('country_of_origin', String),
    Column('pdf_file', String)
)
meta.create_all(engine, checkfirst=True)

# the two classes below are the models for the data
class Tags(BaseModel):
    protected_group: Optional[List[str]] = None
    social_group_type: Optional[List[str]] = None
    social_group_name: Optional[str] = None

    class Config:
        orm_mode = True

class CaseObject(BaseModel):
    case_id: int
    user_id: Optional[int]
    docs_public: Optional[bool]
    case_title: Optional[str] = "Felicia v. B.I.A."
    case_number: Optional[str] = "4321"
    judge_name: Optional[str] = "Dorothy Day"
    outcome: Optional[str] = "Granted"
    country_of_origin: Optional[str] = "Kazakhstan"
    pdf_file: Optional[str] = None
    tags: Optional[Tags]
    
    class Config:
        orm_mode = True

#below is a function created to be used as a dependency within the path parameters
# however switching over to using the SQLAlchemy Expression Language has made it less needed
# furthermore to use the depedency function sqlalchemy.orm.Session must be imported to be usable
# that module was removed to lighten the file
# however the function is usefule to have around, it's useful for prototyping
def get_db() -> sqlalchemy.engine.base.Connection:
    """Get a SQLAlchemy database connection.
    
    Uses this environment variable if it exists:  
    DATABASE_URL=dialect://user:password@host/dbname

    Otherwise uses a SQLite database for initial local development.
    """
    
    engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # change back `database_url` when switching back to postgres DB

    connection = engine.connect()

    try:
        yield connection
    finally:
        connection.close()

router = APIRouter()

@router.get("/cases/get_case/{case_id}")
async def get_case(case_id: int, q: Optional[str] = None):
    s = select([cases]).where(cases.columns.case_id == case_id)
    result= engine.execute(s)
    print(cases.exists(bind=engine))
    return result.fetchall()

@router.put("/cases/create_case/{case_id}", response_model=CaseObject)
async def create_case(case_id: int, case: CaseObject):
    s = engine.connect().execute(cases.insert(), case_id=case_id)
    s.close()
    s = select([cases]).where(cases.columns.case_id == case_id)
    result= engine.execute(s)

    return result.fetchall()[0]

@router.get("/see_all", response_model=List[CaseObject])
async def see_all(limit: Optional[int] = 1000):
    result = engine.execute(cases.select())
    return result.fetchall()

@router.get("/num_of_cases", response_model=int)
async def num_of_cases():
    result= engine.execute(cases.count())
    return result.fetchall()[0][0]

@router.delete('/reset', response_model=int)
async def reset():
    cases.drop(engine)
    cases.create(engine)
    result= engine.execute(cases.count())
    return result.fetchall()[0][0]

### maybe use for later ###
"""

@router.on_event("startup")
async def startup():
    await engine.connect()

@router.on_event("shutdown")
async def shutdown():
    await engine.disconnect()
"""
"""
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

cases = sqlalchemy.Table(
    "cases",
    metadata,
    sqlalchemy.Column("case_id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("public", sqlalchemy.Boolean),
    sqlalchemy.Column("case_title", sqlalchemy.String),
    sqlalchemy.Column("case_number", sqlalchemy.String),
    sqlalchemy.Column("judge_name", sqlalchemy.String),
    sqlalchemy.Column("outcome", sqlalchemy.String),
    sqlalchemy.Column("country_of_origin", sqlalchemy.String),
    sqlalchemy.Column("pdf_file", sqlalchemy.String),
    
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)
"""