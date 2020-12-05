"""Database functions"""

import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
import sqlalchemy
from sqlalchemy import create_engine

router = APIRouter()


async def get_db() -> sqlalchemy.engine.base.Connection:
    """Get a SQLAlchemy database connection.

    Uses this environment variable if it exists:
    DATABASE_URL=dialect://user:password@host/dbname

    """
    load_dotenv()
    engine = create_engine('postgresql://master:gNh1GB4hW5MFqJvmthF2@asylum.catpmmwmrkhp.us-east-1.rds.amazonaws.com/asylum')
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()


@router.get('/info')
async def get_url(connection=Depends(get_db)):
    """Verify we can connect to the database,
    and return the database URL in this format:

    dialect://user:password@host/dbname

    The password will be hidden with ***
    """
    url_without_password = repr(connection.engine.url)
    return {'database_url': url_without_password}
