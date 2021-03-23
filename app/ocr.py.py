import pytesseract
from pdf2image import convert_from_bytes
from fastapi import APIRouter, File
import sqlalchemy
from dotenv import load_dotenv, find_dotenv
from app.BIA_Scraper import BIACase
import os

os.environ["OMP_NUM_THREADS"]= "1"
os.environ["OMP_THREAD_LIMIT"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["PAPERLESS_AVX2_AVAILABLE"]="false"
os.environ["OCR_THREADS"] = "1"



router = APIRouter()

load_dotenv(find_dotenv())
database_url = os.getenv("DATABASE_URL")
engine = sqlalchemy.create_engine(database_url)

@router.post("/insert")
async def create_upload_file(file: bytes = File(...)):
    """
    This function inserts a PDF and the OCR converted text into a database
    """
    
    text = []

    # Converts the bytes object recieved from fastapi
    pages = convert_from_bytes(file, 200, fmt="png", thread_count=2)
    
    # Uses pytesseract to convert each page of pdf to txt
    
    text.append(pytesseract.image_to_string(pages))

    # Joins the list to an output string
    string_to_return = " ".join(text)

    return {"Text": string_to_return}


@router.post("/get_fields")
async def create_upload_file_get_fields(file: bytes = File(...)):
    

    text = []

    # Converts the bytes object recieved from fastapi
    pages = convert_from_bytes(file, 200, fmt="png", thread_count=2)

    # Uses pytesseract to convert each page of pdf to txt
    for item in pages:
        text.append(pytesseract.image_to_string(item))

    # Joins the list to an output string
    string = " ".join(text)

    # Using the BIACase Class to populate fields
    case = BIACase(string)

    # Json object / dictionary to be returned
    case_data = {}

    # Case ID (dummy data)
    case_data["case_id"] = "test"

    # Initial or appelate (dummy data)
    case_data["initial_or_appellate"] = "test"

    # Case origin
    case_data["case_origin"] = "test"

    # Application field
    app = case.get_application()
    app = [ap for ap, b in app.items() if b]
    case_data["application_type"] = "; ".join(app) if app else None

    # Date field
    case_data["hearing_date"] = case.get_date()

    # Country of origin
    case_data["nation_of_origin"] = case.get_country_of_origin()

    # Getting Panel members
    panel = case.get_panel()
    case_data["judge"] = "; ".join(panel) if panel else None

    # Getting case outcome
    case_data["case_outcome"] = case.get_outcome()

    # Getting protected grounds
    pgs = case.get_protected_grounds()
    case_data["protected_ground"] = "; ".join(pgs) if pgs else None

    # Getting the violence type on the asylum seeker
    based_violence = case.get_based_violence()
    violence = "; ".join([k for k, v in based_violence.items() if v]) \
              if based_violence \
              else None
    
    # Getting keywords
    keywords = "; ".join(["; ".join(v) for v in based_violence.values()]) \
              if based_violence \
              else None
      
    case_data["type_of_violence_experienced"] = violence
    case_data["keywords"] = keywords

    # Getting references / sex of applicant
    references = [
    "Matter of AB, 27 I&N Dec. 316 (A.G. 2018)"
    if case.references_AB27_216() else None,
    "Matter of L-E-A-, 27 I&N Dec. 581 (A.G. 2019)"
    if case.references_LEA27_581() else None
    ]

    case_data["references"] = "; ".join([r for r in references if r])
    case_data["applicant_sex"] = case.get_seeker_sex()
    
    # Getting applicant's indigenous status
    indigenous_status = case.get_applicant_indigenous_status()
    case_data["applicant_indigenous_group"] = indigenous_status

    # Getting applicant's native language
    applicant_lang = case.get_applicant_language()
    case_data["applicant_language"] = applicant_lang

    # Getting ability to access interpreter
    access_to_interpreter = case.get_applicant_access_interpeter()
    case_data["applicant_access_to_interpreter"] = access_to_interpreter
    
    # Getting applicant's credibility status
    determined_applicant_credibility = case.get_applicant_determined_credibility()
    case_data["applicant_perceived_credibility"] = determined_applicant_credibility
    
    # Getting whether the case argued against the one-year guideline
    case_data["case_filed_within_one_year"] = f"{case.check_for_one_year}"

    return case_data
