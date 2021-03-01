import os

os.environ["OMP_NUM_THREADS"]= '1'
os.environ["OMP_THREAD_LIMIT"] = '1'
os.environ["MKL_NUM_THREADS"] = '1'
os.environ["NUMEXPR_NUM_THREADS"] = '1'
os.environ["OMP_NUM_THREADS"] = '1'
os.environ["PAPERLESS_AVX2_AVAILABLE"]="false"
os.environ["OCR_THREADS"] = '1'

import poppler
import pytesseract
from pdf2image import convert_from_bytes
from fastapi import APIRouter, File
import sqlalchemy
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from app.BIA_Scraper import BIACase
import requests
import pandas as pd
import numpy as np
from PIL import Image

router = APIRouter()

load_dotenv(find_dotenv())
database_url = os.getenv('DATABASE_URL')

engine = sqlalchemy.create_engine(database_url)

@router.post('/insert')
async def create_upload_file(file: bytes = File(...)):
    '''
    This function inserts a PDF and the OCR converted text into a database
    '''
    
    text = []

    ### Converts the bytes object recieved from fastapi
    pages = convert_from_bytes(file,200,fmt='png',thread_count=2)
    
    ### Uses pytesseract to convert each page of pdf to txt
    
    text.append(pytesseract.image_to_string(pages))

    ### Joins the list to an output string
    string_to_return = " ".join(text)

    return {'Text': string_to_return}


@router.post('/get_fields')
async def create_upload_file_get_fields(file: bytes = File(...)):
    

    text = []

    ### Converts the bytes object recieved from fastapi
    pages = convert_from_bytes(file,200,fmt='png',thread_count=2)

    ### Uses pytesseract to convert each page of pdf to txt
    for item in pages:
        text.append(pytesseract.image_to_string(item))

    ### Joins the list to an output string
    string = " ".join(text)

    ### Using the BIACase Class to populate fields
    case = BIACase(string)

    ### Json object / dictionary to be returned
    case_data = {}

    ### Application field
    app = case.get_application()
    app = [ap for ap, b in app.items() if b]
    case_data['application'] = '; '.join(app) if app else None

    ### Date field
    case_data['date'] = case.get_date()

    ### Country of origin 
    case_data['country_of_origin'] = case.get_country_of_origin()

    ### Getting Panel members
    panel = case.get_panel()
    case_data['panel_members'] = '; '.join(panel) if panel else None

    ### Getting case outcome
    case_data['outcome'] = case.get_outcome()

    ### Getting protected grounds
    pgs = case.get_protected_grounds()
    case_data['protected_grounds'] = '; '.join(pgs) if pgs else None

    ### Getting the violence type on the asylum seeker
    based_violence = case.get_based_violence()
    violence = '; '.join([k for k, v in based_violence.items() if v]) \
              if based_violence \
              else None
    
    ### Getting keywords
    keywords = '; '.join(['; '.join(v) for v in based_violence.values()]) \
              if based_violence \
              else None
      
    case_data['based_violence'] = violence
    case_data['keywords'] = keywords

    ### Getting references / sex of applicant
    references = [
    'Matter of AB, 27 I&N Dec. 316 (A.G. 2018)' 
    if case.references_AB27_216() else None,
    'Matter of L-E-A-, 27 I&N Dec. 581 (A.G. 2019)'
    if case.references_LEA27_581() else None
    ]

    case_data['references'] = '; '.join([r for r in references if r])
    case_data['sex_of_applicant'] = case.get_seeker_sex()
    
    
    return case_data
