"""Database functions"""

from typing import List, Optional 
import os
import databases
from sqlalchemy import delete, insert, update, Table, MetaData, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.sql import select
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
import sqlalchemy

"""below is an example of the DB host server URL"""
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

# to connect to the stakeholders DB, you must get the credentials
# and then set up those credentials in a `.env` file to maintain
# the stakeholders data security
database_url = os.getenv('DATABASE_URL')
engine = sqlalchemy.create_engine(database_url) # to use with Postgres

# if you don't have the stakeholders credentials
# use the two lines below to use an sqlite test database for protyping
# to use the test DB, just uncomment the two lines below
# and comment the two lines above
""" 
DATABASE_URL = "sqlite:///./test.db"
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # to use with sqlite change back `database_url` when switching back to postgres DB
"""


# the block below creates the database table
# the Metadata() class is instantiated and creates the DB table scaffolding
# to add/alter the DB tables replicate syntax seen below in the `cases` variable
# and the class models

# to persist any added/altered DB tables you made use the `reset`
# function found below among the endpoint functions
meta = MetaData() 

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
# the construct of the class models follows the methods laid in the pydantic module
# please refer to https://pydantic-docs.helpmanual.io/usage/models/
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
# furthermore to use the depedency function below, sqlalchemy.orm.Session must be imported
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


### STARTING HERE ###
"""
All the functions below this line are visible to the `main.py` file 
with this line `app.include_router(db.router, tags=['DataBase'])`
via the `APIRouter()` class instantiated right above the functions

that class object is used as a decorator with the functions below --> @router.someHTTPmethod()
HTTP methods include post(), get(), put(), delete()... 
for more info see documentation (fastAPI)[https://fastapi.tiangolo.com/tutorial/first-steps/#operation]

to build an endpoint:
1. build your path parameter
@router.get("/cases/{case_id}")  <--- path parameter
refer to https://fastapi.tiangolo.com/tutorial/path-params/

2. build a query parameter
async def get_case(case_id:int, q: Optional[str] = None):  <--- query parameter
refer to https://fastapi.tiangolo.com/tutorial/query-params/

3. finish your function logic and double check in the browser to make sure everything renders
refer to https://fastapi.tiangolo.com/tutorial/body/#use-the-model
"""
router = APIRouter()

@router.get("/cases/{case_id}")
async def get_case(case_id: int, q: Optional[str] = None):
    """
    Use this function to return a case file specified by inputting a
    specified case_id number
    """
    s = select([cases]).where(cases.columns.case_id == case_id)
    result= engine.execute(s)
    print(cases.exists(bind=engine))
    return result.fetchall()

@router.put("/cases/{case_id}", response_model=CaseObject)
async def create_case(case_id: int, case: CaseObject):
    """
    Use this function to create a new case file by inputting a new
    case_id number
    """
    s = engine.connect().execute(cases.insert(), case_id=case_id)
    s.close()
    s = select([cases]).where(cases.columns.case_id == case_id)
    result= engine.execute(s)

    return result.fetchall()[0]

@router.get("/see_all", response_model=List[CaseObject])
async def see_all(limit: Optional[int] = 1000):
    """
    This function returns all case files within the DB, limited
    to the first 1000 cases
    """
    result = engine.execute(cases.select())
    return result.fetchall()

@router.get("/num_of_cases", response_model=int)
async def num_of_cases():
    """
    returns the number of total cases in the DB
    """
    result= engine.execute(cases.count())
    return result.fetchall()[0][0]

@router.delete('/reset', response_model=int)
async def reset():
    """
    this function essentially resets the DB by deleting the DB tables

    currently it only deletes the cases table

    this function is useful for prototyping DB tables, however once a 
    final DB schema is agreed upon the developer should consider removing this function
    to avoid accidental deletion of the stakeholder's actual data

    to prototype future DB tables just replicate the syntax for any new 
    DB tables you create found in the db.py file of the app folder
    """
    cases.drop(engine)
    cases.create(engine)
    result= engine.execute(cases.count())
    return result.fetchall()[0][0]