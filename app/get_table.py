from dotenv import load_dotenv
from fastapi import APIRouter, Depends
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd

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


@router.get('/req')
async def make_req(connection=Depends(get_db)):
    """Returns a json object with the entire pdfs table.
    Right now there's nothing in that table so it's just the
    headers but there will be
    """
    sql = """
        SELECT *
        FROM pdfs
        """
    return pd.read_sql(sql, con=connection)
