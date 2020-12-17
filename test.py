
import os









from dotenv import load_dotenv


from fastapi import APIRouter, File


from pdf2image import convert_from_bytes


from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter


from pdfminer.converter import TextConverter


from pdfminer.layout import LAParams


from pdfminer.pdfpage import PDFPage


from PIL import Image


import pytesseract


import sqlalchemy


from sqlalchemy import create_engine







router = APIRouter()


load_dotenv()


database_url = os.getenv('DATABASE_URL')


print('db url name', database_url)
