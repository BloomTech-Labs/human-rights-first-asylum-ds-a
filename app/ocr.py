import os


from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
from fastapi import APIRouter, File
import sqlalchemy
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine


from app.scrape import textScraper

router = APIRouter()
load_dotenv(find_dotenv())
database_url = os.getenv('DATABASE_URL')

engine = sqlalchemy.create_engine(database_url)

@router.post('/insert')
async def insertDoc(file: bytes = File(...)):
    '''
    This function inserts a PDF and the OCR converted text into a database

    '''
    # Convert bytes from POST to list of strings
    # text = ocr_func(file)
    text = "Success"
    scraper = textScraper(text)
    judge = scraper.Judge
    print('judge ', judge)
    query = """INSERT INTO pdfs(pdf, plaintext) VALUES (%s, %s)""" 
    vals = (file, text)
    engine.execute(query, vals)
    return


def ocr_func(pdfBytes: bytes = File(...), txt_folder: str = './temp/') -> list:
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
    # Show what is being converted
    print(fulltext[:2])
    return ''.join(fulltext).split('\n\n')