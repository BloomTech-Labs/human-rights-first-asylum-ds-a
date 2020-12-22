import os
from dotenv import load_dotenv
from fastapi import APIRouter, File
from pdf2image import convert_from_bytes
from PIL import Image
# import pytesseract
import sqlalchemy
from sqlalchemy import create_engine

load_dotenv()
database_url = os.getenv('DATABASE_URL')

print('db url name', database_url)
engine = create_engine(database_url)
selQuery = """SELECT COUNT(*) from pdfs;"""
truncateQuery = """TRUNCATE TABLE pdfs"""
# print(engine.execute(selQuery))
print('initial values prior to wipe', engine.execute(selQuery).fetchall())
# engine.execute(truncateQuery)
print(engine.execute(selQuery).fetchall())