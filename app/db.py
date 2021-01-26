"""Database functions"""

import os
import pandas as pd
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import model, schemas

router = APIRouter()


Base = declarative_base()

async def get_db() -> sqlalchemy.engine.base.Connection:
    """Get a SQLAlchemy database connection.
    
    Uses this environment variable if it exists:  
    DATABASE_URL=dialect://user:password@host/dbname

    Otherwise uses a SQLite database for initial local development.
    """
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    engine = sqlalchemy.create_engine(database_url)
    model.Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()


@router.post('/new', response_model=CaseObject)
async def add_case(case: CaseObject, connection=Depends(get_db)):
    """
    add a new case file
    """
    query = new.insert().values(
        case_id=case.case_id,
        public=case.public,
        case_title=case.case_title,
        case_number=case.case_number,
        judge_name=case.judge_name,
        outcome=case.outcome,
        country_of_origin=case.country_of_origin,
        pdf_file=case.pdf_file
    )
    def write_data(case):
        tablename = "case"
        case.to_sql(tablename, connection, if_exists='append', index=False, method='multi')
    return case

@router.get('/info')
async def get_url(connection=Depends(get_db)):
    """Verify we can connect to the database, 
    and return the database URL in this format:

    dialect://user:password@host/dbname

    The password will be hidden with ***
    """
    url_without_password = repr(connection.engine.url)
    return {'database_url': url_without_password}

