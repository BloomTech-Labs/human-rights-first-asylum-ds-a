import os
os.environ["OMP_NUM_THREADS"]= '1'
os.environ["OMP_THREAD_LIMIT"] = '1'
os.environ["MKL_NUM_THREADS"] = '1'
os.environ["NUMEXPR_NUM_THREADS"] = '1'
os.environ["OMP_NUM_THREADS"] = '1'
os.environ["PAPERLESS_AVX2_AVAILABLE"]="false"
os.environ["OCR_THREADS"] = '1'


from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
from fastapi import APIRouter, File
import sqlalchemy
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

from io import StringIO

import app.test

router = APIRouter()
# print('dir ', os.listdir('..'))
load_dotenv(find_dotenv())
database_url = os.getenv('DATABASE_URL')
# print('test db?',database_url)

engine = sqlalchemy.create_engine(database_url)

@router.post('/insert')
async def insertDoc(file: bytes = File(...)):
    '''
    This function inserts a PDF and the OCR converted text into a database

    '''
    text = ocr_func(file)
    # query = """INSERT INTO pdfs(pdf, plaintext) VALUES (%s, %s)""" 
    # vals = (file, text)
    # engine.execute(query, vals)
    # Return text as response
    return {'Text': text}


def ocr_func(pdfBytes: bytes = File(...), txt_folder: str = './temp/'):
    '''
    Takes an uploaded .pdf file, converts it to plain text, and saves it as a
    .txt file
    '''

    pages = convert_from_bytes(pdfBytes, dpi=300)
    # num_pages = 0
    print('num pages ', pages)
    fulltext = []
    for image_counter, page in enumerate(pages):
        filename = 'page_' + str(image_counter) + '.jpg'
        page.save(filename, 'JPEG')
        img = Image.open(filename)
        print('file name ', filename)
        result = (pytesseract.image_to_string(img))
        text = str(result)
        os.remove(filename)
        text = text.replace('-\n', '')
        fulltext.append(text)
    return (''.join(fulltext).split('\n\n'))
    
    # print('num pages', list(range(num_pages)))
    # for i in range(num_pages):
    #     filename = 'page_' + str(i) + '.jpg'
    #     print('fileName', filename)
        