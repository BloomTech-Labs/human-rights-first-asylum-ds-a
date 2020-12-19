import os

from fastapi import APIRouter, BackgroundTasks, File
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine


from app.scrape import textScraper

router = APIRouter()
load_dotenv(find_dotenv())
database_url = os.getenv('DATABASE_URL')

engine = create_engine(database_url)

@router.post('/insert')
async def insertDoc(file: bytes = File(...), background_tasks: BackgroundTasks = None):
    '''
    This function inserts a PDF and the OCR converted text into a database
    '''
    # background_tasks.add_task(processAndInsert, file)
    return {"response": "Document has been received and will be uploaded"}


def processAndInsert(file: bytes = File(...)) -> None:
    '''
    Converts the uploaded file to plaintext, scrapes data, and 
    uploads to database
    file is an uploaded PDF document
    returns nothing
    '''
    scraper = textScraper(file)
    plainText = scraper.text
    judge = scraper.judge
    print('plain text ', plainText[:30])
    query = """INSERT INTO pdfs(plainText, judge) VALUES (%s, %s)""" 
    vals = (plainText, judge)
    engine.execute(query, vals)
    print('execution done')
