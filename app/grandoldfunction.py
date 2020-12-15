#ait so what the fuck we doin here

#first, insert the pdf

#then, convert pdf to txt

#then, insert txt

#figure out how to insert other values once we figure out how to extract them

from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine
import psycopg2
from fastapi import APIRouter, File
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import os


router = APIRouter()


load_dotenv()

database_url = os.getenv('DATABASE_URL')
engine = sqlalchemy.create_engine(database_url)

@router.post('/insert')
async def adding(file: bytes = File(...)):

    pages = convert_from_bytes(file, dpi=300, fmt='jpg')

    num_images = 0
    for image_counter, page in enumerate(pages):
        filename = "page_"+str(image_counter)+".jpg"
        page.save(filename, 'JPEG')
        num_images += 1

    f = []
    
    for i in range(num_images):
        filename = "page_"+str(i)+".jpg"
        text = str(((pytesseract.image_to_string(Image.open(filename)))))
        os.remove(filename)
        text = text.replace('-\n', '')
        f.append(text)

    with open('txt.txt', 'w', encoding='UTF-8') as doc:
        for item in f:
            doc.write("%s\n" % item)
    
    with open('txt.txt', 'r') as scan:
        pls = scan.read()



    query = """INSERT INTO pdfs(pdf, plaintext) VALUES (%s, %s)""" 
    vals = (file, pls)

    engine.execute(query, vals)

    return "all done"
