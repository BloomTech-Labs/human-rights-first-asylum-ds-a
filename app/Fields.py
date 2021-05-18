#Libraries and packages used:

import time
import json
import datetime
import pytesseract
import geonamescache
import requests
from pdf2image import convert_from_bytes
from collections import Counter
from spacy import load
from spacy.tokens import Doc, Span, Token
from spacy.matcher import Matcher, PhraseMatcher
from scraping_tool import Doc_Scraper


nlp = load("en_core_web_md")

# Read in dictionary of all court locations
with open('./app/court_locations.json') as f:
    court_locs = json.load(f)


def make_fields(file) -> dict:
    start = time.time()
    pages = convert_from_bytes(file, dpi=90)
    text = map(pytesseract.image_to_string, pages)
    string = " ".join(text)
    case = Doc_Scraper(string)
    case_data = {
        'application': case.get_application(),
        'date': case.get_date(),
        'country of origin': case.get_country_of_origin(),
        'Appellate Case': case.is_appellate,
        'state of origin': case.state,
        'city of origin': case.city,
        'gender': case.get_gender(),
        'applicant language': case.get_applicant_language(),
        'check for one year': case.check_for_one_year(),
        'judges': case.appellate_judges(),
        'protected grounds': case.get_protected_grounds(),
        'based violence': case.get_based_violence(),
        'outcome': case.get_outcome(),
        
    }
    time_taken = time.time() - start
    case_data["time to process"] = f"{time_taken:.2f} seconds"
    return case_data


def similar(a, return_b, min_score):
    """
    • Returns 2nd string if similarity score is above supplied
    minimum score. Else, returns None.
    """
    if SequenceMatcher(None, a, return_b).ratio() >= min_score:
        return return_b


def similar_in_list(lst):
    """
    • Uses a closure on supplied list to return a function that iterates over
    the list in order to search for the first similar term. It's used widely
    in the scraper.
    """

    def impl(item, min_score):
        for s in lst:
            s = similar(item, s, min_score)
            if s:
                return s

    return impl


