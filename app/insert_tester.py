from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine
from fastapi import APIRouter, File, Depends
import psycopg2

router = APIRouter()

async def get_db() -> sqlalchemy.engine.base.Connection:
    """Get a SQLAlchemy database connection.

    Uses this environment variable if it exists:
    DATABASE_URL=dialect://user:password@host/dbname

    """
    load_dotenv()
    database_url = "asylum.catpmmwmrkhp.us-east-1.rds.amazonaws.com"
  
    os.getenv('DATABASE_URL', default='sqlite:///temporary.db')
    engine = sqlalchemy.create_engine(database_url)
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()


@router.post('/insert_tester')
async def insert_pdf(file: bytes = File(...), connection=Depends(get_db)):
    testup = file

    cursor.execute("""INSERT INTO pdfs (pdf) VALUES (%s);""", (testup,))

    connection.commit()

    cursor.close()
    connection.close()

    return 'all done'
