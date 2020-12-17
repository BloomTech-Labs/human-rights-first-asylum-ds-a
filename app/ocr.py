import os


from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
from fastapi import APIRouter, File
import sqlalchemy
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

from io import StringIO

import app.test

# os.environ['DATABASE_URL'] = 'postgresql://master:LMGaJr77nyC353V@asylum.catpmmwmrkhp.us-east-1.rds.amazonaws.com/asylum'
router = APIRouter()
print('dir ', os.listdir('..'))
load_dotenv(find_dotenv())
database_url = os.getenv('DATABASE_URL')
print('test db?',database_url)

if database_url == None:
    print('first pass failed')
    load_dotenv('.env')
    database_url = os.getenv('DATABASE_URL')

if database_url == None:
    print('second pass failed')
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')

engine = sqlalchemy.create_engine(database_url)

@router.post('/insert')
async def insertDoc(file: bytes = File(...)):
    '''
    This function inserts a PDF and the OCR converted text into a database

    '''
    text = ocr_func(file)
    query = """INSERT INTO pdfs(pdf, plaintext) VALUES (%s, %s)""" 
    vals = (file, text)
    engine.execute(query, vals)
    return


def ocr_func(pdfBytes: bytes = File(...), txt_folder: str = './temp/'):
    '''
    Takes an uploaded .pdf file, converts it to plain text, and saves it as a
    .txt file
    '''

    pages = convert_from_bytes(pdfBytes, dpi=300)
    num_pages = 0
    
    for image_counter, page in enumerate(pages):
        filename = 'page_' + str(image_counter) + '.jpg'
        page.save(filename, 'JPEG')
        num_pages += 1
    
    fulltext = []
 
    for i in range(num_pages):
        filename = 'page_' + str(i) + '.jpg'
        text = str(((pytesseract.image_to_string(Image.open(filename)))))
        os.remove(filename)
        text = text.replace('-\n', '')
        fulltext.append(text)
    return (''.join(fulltext).split('\n\n'))