import os


from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
from fastapi import APIRouter, BackgroundTasks, File
import sqlalchemy
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine


from app.scrape import textScraper

router = APIRouter()
load_dotenv(find_dotenv())
database_url = os.getenv('DATABASE_URL')

engine = sqlalchemy.create_engine(database_url)

@router.post('/insert')
async def insertDoc(file: bytes, background_tasks: BackgroundTasks):
    '''
    This function inserts a PDF and the OCR converted text into a database
    '''
    background_tasks.add_task(processAndInsert, file)
    return {"message": "Successfully received file. Starting OCR and posting to database"}
    # Convert bytes from POST to list of strings
    return {"message":"File received"}


def processAndInsert(file: bytes = File(...)) -> None:
    '''
    Converts the uploaded file to plaintext, scrapes data, and 
    uploads to database
    file is an uploaded PDF document
    returns nothing
    '''
    scraper = textScraper(file)
    judge = scraper.Judge
    text = scraper.getText()
    query = """INSERT INTO pdfs(pdf, plaintext) VALUES (%s, %s)""" 
    vals = (file, text)
    engine.execute(query, vals)
