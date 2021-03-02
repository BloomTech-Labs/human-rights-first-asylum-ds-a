from typing import List, Tuple, Union, Callable, Dict, Iterator
from collections import defaultdict
from pprint import pprint
from difflib import SequenceMatcher
from datetime import datetime
import bs4
from bs4 import BeautifulSoup, element
import geonamescache
import requests
import pandas as pd
import numpy as np
from pathlib import Path
import re
import os
import spacy
import poppler
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.tokens.token import Token
from spacy import load

nlp = spacy.load('en_core_web_sm')


###BIA CLASS 
"""
This is the class used in ocr.py for extracting fields from the txt file.
"""


### Below is code for Web scraping the judges from wikipedia


# Extracting current Appellate Immigration Judges
# From Wikipedia, using Beautiful Soup. Code is mostly biolerplate
judges_url: str
judges_url = 'https://en.wikipedia.org/wiki/Board_of_Immigration_Appeals'

html: str
html = requests.get(judges_url).text

soup: BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

table: element.Tag
table = soup.findAll(lambda tag: tag.name =='table')[1]

rows: element.ResultSet
rows = table.findAll(lambda tag: tag.name == 'tr')

column_names: List[str]
column_names = [
    col.get_text().strip().lower().replace(' ', '_')
    for col in rows.pop(0) if col.name == 'th'
]

rows: List[List[str]]
rows = [
    [
        cell.get_text().strip().replace(',', '') 
        for cell in row if cell.name == 'td'
    ] 
    for row in rows
]

as_dict: List[Dict[str, str]]
as_dict = [
    dict(zip(column_names, row)) for row in rows
]

judges_df: pd.DataFrame
judges_df = pd.DataFrame.from_dict(as_dict)


### Getting countries from geonames cache
### This is used for finding country of origin from the case file

gc = geonamescache.GeonamesCache()

COUNTRIES: Iterator[str]
COUNTRIES = gc.get_countries_by_names().keys()


### These are methods used in the BIA Class


def similar(a: str, return_b: str, min_score: float) -> str:
    '''
    • Returns 2nd string if similarity score is above supplied
    minimum score. Else, returns None.
    '''
    return return_b \
        if SequenceMatcher(None, a, return_b).ratio() >= min_score \
        else None


def similar_in_list(lst: List[str]) -> Callable:
    '''
    • Uses a closure on supplied list to return a function that iterates over
    the list in order to search for the first similar term. It's used widely
    in the scraper.
    '''
    def impl(item: str, min_score: float) -> Union[str, None]:
        for s in lst:
            s = similar(item, s, min_score)
            if s:
                return s
        return None
    return impl


def get_if_judge(name: str) -> Union[str, None]:
    '''
    • Returns the judge's name if a match is found. Currently, the match
    is very strictly defined by the current judge's names found through
    Wikipedia. It will 100% stop any false positives, but some leniency should
    be introduced in order to prevent any false negatives.
    '''
    clean_name: Callable[[str], str]
    clean_name = lambda s: s.lower() \
                            .replace(',', '') \
                            .replace('.', '')

    judges_names = judges_df['name'] \
                    .apply(lambda s: clean_name(s).split()[-1])

    name = clean_name(name).split()[-1]

    for i, jn in enumerate(judges_names):
        if jn in name:
            return judges_df['name'].iloc[i]
    
    return None


### BIACase Class

class BIACase:
    def __init__(self, text: str):
        '''
        • Input will be text from a BIA case pdf file, after the pdf has
        been converted from PDF to text. 
        • Scraping works utilizing spaCy, tokenizing the text, and iterating
        token by token searching for matching keywords.
        '''

        self.doc: Doc 
        self.doc = nlp(text)

        self.ents: Tuple[Span] 
        self.ents = self.doc.ents

    def get_ents(self, labels: List[str] = None) -> Iterator[Span]:
        '''
        • Retrieves entitiess of a specified label(s) in the document,
        if no label is specified, returns all entities
        '''
        return (ent for ent in self.ents if ent.label_ in labels) \
                if labels \
                else self.ents

    def get_country_of_origin(self) -> str:
        '''
        • Returns the country of origin of the applicant. Currently just checks
        the document for a country that is NOT the United States.
        '''
        locations: Iterator[str]
        locations = map(lambda ent: ent.text,
                        self.get_ents(['GPE']))
        
        similar_country: Callable[[str, float], Union[str, None]]
        similar_country = similar_in_list(COUNTRIES)

        for loc in locations:
            if not similar(loc, 'United States', 0.9):
                origin: Union[str, None]
                origin = similar_country(loc, 0.9)

                if origin: return origin
                else: continue
        
        return None


    def get_date(self) -> Union[str, None]:
        '''
        • Returns date of the document. Easy to validate by the PDF filename,
        whether its hosted on scribd or somewhere else.
        '''
        clean_date: Callable[[str], str]
        clean_date = lambda s: ''.join([
            char for char in s
                if char.isalnum()
                or char.isspace()
        ])

        dates: Iterator[str] 
        dates = map(lambda ent: clean_date(ent.text), 
                    self.get_ents(['DATE']))

        for date in dates:
            try:
                # SHOULD return list of length 3,
                # Such as ['Sept', '2', '2019']
                d: List[str]
                d = date.split()
                if len(d) != 3:
                    continue
                else:
                    # Ex. Jan, Feb, ..., Sep, Oct, Dec
                    month: str
                    month = d[0][:3].title()
                    # Ex. 01, 02, 03, ..., 29, 30, 31
                    day: str
                    day = '0' + d[1] \
                        if len(d[1]) == 1 else d[1]
                    # Ex. 1991, 1992, ..., 2020, 2021
                    year: str
                    year = d[2]
                    # Ex. Jan 09 2014
                    parsed_date: str
                    parsed_date = ' '.join([month, day, year])
                    # datetime obj, Ex Repr: 2020-09-24 00:00:00
                    dt: datetime
                    dt = datetime.strptime(parsed_date, '%b %d %Y')
                    # strip time of hours/min/sec, save as str
                    dt: str
                    dt = str(dt).split()[0]
                    
                    return dt
            except:
                continue

        return None

    def get_panel(self) -> Union[List[str], None]:
        '''
        • Returns the panel members of case in document. 
        TODO: Check judges names less strictly - I've seen a document
        that named the Judge Monsky differently than how she regularly 
        appears.
        '''
        panel_members = List[str]
        panel_members = []

        possible_members: Iterator[Span]
        possible_members = map(lambda ent: ent.text,
                               self.get_ents(['PERSON', 'ORG']))

        for member in possible_members:
            judge: Union[str, None]
            judge = get_if_judge(member)

            if judge:
                panel_members.append(judge)

        return list(set(panel_members)) \
               if panel_members \
               else None

    def get_surrounding_sents(self, token: Token) -> Span:
        '''
        • This function will return the two sentences surrounding the token,
        including the sentence holding the token.
        '''
        start: int
        start = token.sent.start

        end: int
        end = token.sent.end

        try:
            sent_before_start: int
            sent_before_start = self.doc[start-1].sent.start
            sent_after_end: int
            sent_after_end = self.doc[end+1].sent.end
        except:
            return token.sent

        surrounding: Span
        surrounding = self.doc[sent_before_start:sent_after_end+1]

        return surrounding

    def get_protected_grounds(self) -> Union[List[str], None]:
        '''
        • This will return the protected ground(s) of the applicant. Special
        checks are needed. Checking for keywords is not enough, as sometimes
        documents label laws that describe each protected ground. Examples
        are 'Purely Political Offense' and 'Real Id Act'.
        '''
        protected_grounds: List[str]
        protected_grounds = [
            'race',
            'religion',
            'nationality',
            'social',
            'political',
        ]

        pgs = []

        similar_pg: Callable[[str, float], Union[str, None]]
        similar_pg = similar_in_list(protected_grounds)

        for token in self.doc:

            sent: str
            sent = token.sent.text.lower()

            s: Union[str, None]
            s = similar_pg(token.text.lower(), 0.9)

            if s == 'social':
                next_word = self.doc[token.i+1].text.lower()
                if not similar(next_word, 'group', 0.95): 
                    continue

            elif s == 'political':
                next_word = self.doc[token.i+1].text.lower()
                if similar(next_word, 'offense', 0.95): 
                    continue

            elif s == 'nationality':
                next_word = self.doc[token.i+1].text.lower()
                if similar(next_word, 'act', 1):
                    continue

            if s:
                surrounding: Span
                surrounding = self.get_surrounding_sents(token)
                
                if 'real id' in sent:
                    continue
                elif 'grounds specified' in surrounding.text.lower():
                    continue 
                elif 'no claim' in surrounding.text.lower():
                    continue

                pgs.append(s)

        return list(set(pgs)) if pgs else None

    def get_application(self) -> Dict[str, bool]:
        '''
        • This will return the seeker's application, found after 'APPLICATION'.
        Because HRF is only interested in Asylum, Withholding of Removal,
        and Convention Against Torture applications, the others should be
        ignored and not included in the dataset.
        '''

        relevant_applications: List[str]
        relevant_applications = [
            'asylum',
            'withholding',
            'torture'    
        ]

        similar_app: Callable[[str, float], Union[str, None]]
        similar_app = similar_in_list(relevant_applications)

        app: Dict[str, bool]
        application = {
            'asylum': False,
            'withholding_of_removal': False,
            'CAT': False
        }

        for token in self.doc:
            if similar(token.text, 'APPLICATION', .86):
                for i in range(1,30):
                    word: str
                    word = self.doc[i + token.i].text.lower()

                    app: Union[str, None]
                    app = similar_app(word, 0.9)

                    if app == 'asylum':
                        application['asylum'] = True
                    elif app == 'withholding':
                        application['withholding_of_removal'] = True
                    elif app == 'torture':
                        application['CAT'] = True

        return application

    def get_outcome(self) -> Union[str, None]:
        '''
        • Returns the outcome of the case. This will appear after 'ORDER'
        at the end of the document.
        '''
        outcomes: List[str]
        outcomes = [
            'remanded', 
            'reversal', 
            'dismissed', 
            'sustained', 
            'terminated', 
            'granted', 
            'denied', 
            'returned'
        ]

        outcomes: Iterator[str]
        outcomes_lemma = map(lambda s: nlp(s)[0].lemma_, outcomes)

        similar_outcome: Callable[[str, float], Union[str, None]]
        similar_outcome = similar_in_list(outcomes)

        similar_outcome_l: Callable[[str, float], Union[str, None]]
        similar_outcome_l = similar_in_list(outcomes)

        dlen: int
        dlen = len(self.doc)

        # iterating token by token through document in reverse
        # improves efficiency only slightly
        for i in reversed(range(dlen-1)):
            token: Token
            token = self.doc[i]

            if similar(token.text, 'ORDER', 0.9):
                for ii in range(i+1, dlen):
                    o: Union[str, None]
                    o = similar_outcome(self.doc[ii].text, 0.9)
                    o = o if o else similar_outcome_l(self.doc[ii].text, 0.92)
                    if o:
                        return nlp(o)[0].lemma_
        return None

    def get_based_violence(self) -> Union[Dict[str, List[str]], None]:
        '''
        • Returns a dictionary where the keys are:
            Family-based violence,
            Gender-based violence,
            Gang-based violence
        • If a key is in the dict, it means the based_violence is present
        in the document, and the relevant sentence(s) where the information is
        contained in the key's value
        '''
        violent_terms: List[str]
        violent_terms = [
            'hurt',
            'kill',
            'rape',
            'assassinate',
            'abuse',
            'threat',
            'murder',
            'torture',
            'assault',
            'shoot',
            'suffer',
            'abduct',
            'kidnap',
            'harm',
            'persecute',
            'scare',
            'fear'
        ]

        sg_family: List[str]
        sg_family = [
            'family',
            'woman',
            'partner',
            'husband',
            'wife',
            'son',
            'daughter',
            'child',
            'ethnicity',
            'parent'
        ]

        sg_gender: List[str]
        sg_gender = [
            'sex'
            'gender',
            'sexuality',
            'woman',
            'transgender',
            'lgbt',
            'lgbtq',
            'lgbtqia',
            'homosexual',
            'homosexuality',
            'gay',
            'lesbian',
            'queer',
        ]

        similar_vterm: Callable[[str, float], Union[str, None]]
        similar_vterm = similar_in_list(violent_terms)

        similar_sg_family: Callable[[str, float], Union[str, None]]
        similar_sg_family = similar_in_list(sg_family)

        similar_sg_gender: Callable[[str, float], Union[str, None]]
        similar_sg_gender = similar_in_list(sg_gender)

        based_v = defaultdict(lambda: [])

        for token in self.doc:
            if similar_sg_family(token.lemma_.lower(), 0.9):
                sent: Span
                sent = token.sent
                for w in sent:
                    vterm = similar_vterm(w.lemma_.lower(), 0.86)
                    if vterm and 'statute' not in token.sent.text:
                        based_v['family-based'] += [token.lemma_.lower()]

            elif similar_sg_gender(token.text.lower(), 0.86):
                sent: Span
                sent = self.get_surrounding_sents(token)
                for w in sent:
                    vterm = similar_vterm(w.lemma_.lower(), 0.86)
                    if vterm and 'statute' not in token.sent.text:
                        based_v['gender-based'] += [token.lemma_.lower()]
            
            elif similar(token.text.lower(), 'gang', 0.9):
                sent = token.sent
                based_v['gang-based'] += [token.lemma_.lower()]

        if based_v:
            based_v: Dict[str, List[str]]
            based_v = {k:list(set(v)) for k, v in based_v.items()}

        return based_v if based_v else None

    def references_AB27_216(self) -> bool:
        '''
        • Returns True if the case file mentions 
        Matter of AB, 27 I&N Dec. 316 (A.G. 2018)
        '''
        for token in self.doc:
            if token.text == 'I&N':
                sent = token.sent.text
                if '316' in sent and '27' in sent:
                    return True
        return False

    def references_LEA27_581(self) -> bool:
        '''
        • Returns True if the case file mentions 
        Matter of L-E-A-, 27 I&N Dec. 581 (A.G. 2019)
        '''
        for sent in self.doc.sents:
            if 'L-E-A-' in sent.text:
                if '27' in sent.text:
                    return True
        return False
                
    def get_seeker_sex(self) -> str:
        '''
        • This field needs to be validated. Currently, it assumes the 
        sex of the seeker by the number of instances of pronouns in the 
        document.
        '''
        male: int
        male = 0

        female: int
        female = 0

        for token in self.doc:
            if similar(token.text, 'he', 1) \
                or similar(token.text, 'him', 1) \
                or similar(token.text, 'his', 1):
                male += 1
            elif similar(token.text, 'she', 1) \
                or similar(token.text, 'her', 1):
                female += 1

        return 'male' if male > female \
                else 'female' if female > male \
                else 'unkown'