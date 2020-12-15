from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import os
from fastapi import APIRouter, File
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine



router = APIRouter()

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


def ocr_func(file: bytes = File(...)):
    '''
    Takes an uploaded .pdf file, converts it to plain text, and saves it as a
    .txt file
    '''
    print('IN OCR FUNC')
    print(os.cwd())
    print('\nlist dir')
    print(os.listdir())
    pytesseract.pytesseract.tesseract_cmd = '/app/bin/Tesseract-OCR/tesseract.exe'

    popplerPath = '/app/bin/poppler/bin/'

    pages = convert_from_bytes(file, dpi=300, fmt='jpg', poppler_path=popplerPath)

    num_images = 0
    for image_counter, page in enumerate(pages):
        filename = "page_"+str(image_counter)+".jpg"
        page.save(filename, 'JPEG')
        num_images += 1

    snippets = []

    for i in range(num_images):
        filename = "page_"+str(i)+".jpg"
        text = str(((pytesseract.image_to_string(Image.open(filename)))))
        os.remove(filename)
        text = text.replace('-\n', '')
        snippets.append(text)
    
    return '\n'.join(snippets)

