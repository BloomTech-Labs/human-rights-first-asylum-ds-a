import time
import re
import json
from collections import Counter
from typing import List, Tuple, Union, Callable, Dict, Iterator
from collections import defaultdict
from difflib import SequenceMatcher
import re
import datetime
import pytesseract
from pdf2image import convert_from_bytes
from bs4 import BeautifulSoup
import geonamescache
import requests
from spacy import load
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.tokens.token import Token
from spacy.matcher import Matcher, PhraseMatcher

nlp = load("en_core_web_sm")

# read in dictionary of all court locations
with open('./app/court_locations.json') as f:
  court_locs = json.load(f)


def make_fields(file) -> dict:
    start = time.time()
    pages = convert_from_bytes(file, dpi=90)
    text = map(pytesseract.image_to_string, pages)
    string = " ".join(text)
    case = BIACase(string)
    case_data = {
        'application': case.get_application(),
        'date': case.get_date(),
        'country of origin': case.get_country_of_origin(),
        'panel members': case.get_panel(),
        'outcome': case.get_outcome(),
        'state of origin': case.get_city_state(),
        'city of origin': case.city,
        'protected grounds': case.get_protected_grounds(),
        'based violence': case.get_based_violence(),
        'keywords': "Test",
        'references': "Test",
        'gender': case.get_gender(),
        'indigenous': case.get_indigenous_status(),
        'applicant language': case.get_applicant_language(),
        'credibility': case.get_credibility(),
        'check for one year': case.check_for_one_year(),
    }
    time_taken = time.time() - start
    case_data["time to process"] = f"{time_taken:.2f} seconds"
    return case_data


def similar(a: str, return_b: str, min_score: float) -> Union[str, None]:
    """
    • Returns 2nd string if similarity score is above supplied
    minimum score. Else, returns None.
    """
    if SequenceMatcher(None, a, return_b).ratio() >= min_score:
        return return_b


def similar_in_list(lst: Union[List[str], Iterator[str]]) -> Callable:
    """
    • Uses a closure on supplied list to return a function that iterates over
    the list in order to search for the first similar term. It's used widely
    in the scraper.
    """

    def impl(item: str, min_score: float) -> Union[str, None]:
        for s in lst:
            s = similar(item, s, min_score)
            if s:
                return s

    return impl

# TODO: This static list should be stored and accessed via the backend 
panel_members = [
     "Adkins-Blanch, Charles K.",
     "Michael P. Baird",
     "Cassidy, William A.",
     "Cole, Patricia A.",
     "Couch, V. Stuart",
     "Creppy, Michael J.",
     "Crossett, John P.",
     "Donovan, Teresa L.",
     "Foote, Megan E.",
     "Geller, Joan B.",
     "Gemoets, Marcos",
     "Gonzalez, Gabriel",
     "Goodwin, Deborah K.",
     "Gorman, Stephanie E.",
     "Grant, Edward R.",
     "Greer, Anne J.",
     "Guendelsberger, John",
     "Hunsucker, Keith E.",
     "Kelly, Edward F.",
     "Kendall Clark, Molly",
     "Liebmann, Beth S.",
     "Liebowitz, Ellen C.",
     "Mahtabfar, Sunita B.",
     "Malphrus, Garry D.",
     "Mann, Ana",
     "Miller, Neil P.",
     "Monsky, Megan Foote",
     "Montante Jr., Phillip J.",
     "Morris, Daniel",
     "Mullane, Hugh G.",
     "Neal, David L.",
     "Noferi, Mark",
     "O'Connor, Blair",
     "O'Herron, Margaret M.",
     "O'Leary, Brian M.",
     "Owen, Sirce E.",
     "Pauley, Roger",
     "Petty, Aaron R.",
     "Pepper, S. Kathleen",
     "RILEY, KEVIN W.",
     "Rosen, Scott",
     "Snow, Thomas G.",
     "Swanwick, Daniel L.",
     "Wendtland, Linda S.",
     "Wetmore, David H.",
     "Wilson, Earle B."
 ]


class BIACase:
    def __init__(self, text: str):
        """
        • Input will be text from a BIA case pdf file, after the pdf has
        been converted from PDF to text.
        • Scraping works utilizing spaCy, tokenizing the text, and iterating
        token by token searching for matching keywords.
        """
        self.doc: Doc = nlp(text)
        self.ents: Tuple[Span] = self.doc.ents
        self.state = None
        self.city = None

    def get_ents(self, labels: List[str]) -> Iterator[Span]:
        """
        • Retrieves entitiess of a specified label(s) in the document,
        if no label is specified, returns all entities
        """
        return (ent for ent in self.ents if ent.label_ in labels)

    def get_country_of_origin(self) -> Union[str, None]:
        """
        • Returns the country of origin of the applicant. Currently just checks
        the document for a country that is NOT the United States.
        """
        gc = geonamescache.GeonamesCache()
        countries: Iterator[str] = gc.get_countries_by_names().keys()

        locations: Iterator[str]
        locations = map(lambda ent: ent.text, self.get_ents(['GPE']))

        similar_country: Callable[[str, float], Union[str, None]]
        similar_country = similar_in_list(countries)

        for loc in locations:
            origin: Union[str, None]
            origin = similar_country(loc, 0.8)
            if origin and origin != "United States":
                return origin

    def get_date(self) -> str:
        """
        • Finds all dates within document in all different formats
        • Returns most recent date found within document
        • Returns all dates in standard XX/XX/XXXX format 
        """
        #Format: MM/DD/YYYY
        pattern_1 = [{'TEXT':{'REGEX':r'^\d{1,2}/\d{1,2}/\d{2}(?:\d{2})?$'}}]

        #Format: Month DD, YYYY
        pattern_2 = [{'IS_ALPHA': True, 'LENGTH': 3},
                  {'IS_DIGIT': True},
                  {'IS_PUNCT': True},
                  {'IS_DIGIT': True}]

        matcher = Matcher(nlp.vocab)

        matcher.add('Type1', [pattern_1])
        matcher.add('Type2', [pattern_2])
        matches = matcher(self.doc)

        all_dates = []

        for match_id, start, end in matches:
            string_id = nlp.vocab.strings[match_id]
            span = self.doc[start:end]
            if string_id == 'Type2':
              reformat_date = datetime.datetime.strptime(span.text, '%b %d, %Y')
            else:
              reformat_date = datetime.datetime.strptime(span.text, '%m/%d/%Y')
            all_dates.append(reformat_date)

        sorted_dates = sorted(all_dates, reverse=True)
        #Backend requested output format: 'yyyy-mm-dd'
        return '{}-{}-{}'.format(sorted_dates[0].year, sorted_dates[0].month, sorted_dates[0].day)

    def get_panel(self) -> str:
         """
         • Returns a semicolon separated string of panel members for appellate case documents.
         """

         matcher = PhraseMatcher(nlp.vocab) # Create the phrase matcher
         uid = 0 # Unique identifier for each judge's patterns

         # Add two patterns to the matcher for each judge
         for judge in panel_members:
             matcher.add(f'PATTERN_{uid}', [nlp(judge)]) # Just the name as it is in the list
             matcher.add(f'PATTERNX_{uid}', [nlp(judge.replace(".",""))]) # A pattern that looks for the names without periods, sometimes not picked up by the scan
             uid += 1

         matches = matcher(self.doc) # Run the phrase matcher over the doc
         case_panel_members = set()

         if len(matches) > 0: # If a judge from our list is found in the document
             for match_id, start, end in matches:
                 judge = self.doc[start:end] # A span object of the match, fetched with its `start` and `end` indecies within the doc
                 case_panel_members.add(judge.text) # Extract the text from the span object, and add to the set of panel members

         return '; '.join(case_panel_members)

    def get_surrounding_sents(self, token: Token) -> Span:
        """
        • This function will return the two sentences surrounding the token,
        including the sentence holding the token.
        """
        start: int
        start = token.sent.start

        end: int
        end = token.sent.end

        try:
            sent_before_start: int
            sent_before_start = self.doc[start - 1].sent.start
            sent_after_end: int
            sent_after_end = self.doc[end + 1].sent.end
        except (IndexError, AttributeError):
            return token.sent

        surrounding: Span
        surrounding = self.doc[sent_before_start:sent_after_end + 1]

        return surrounding

    def get_protected_grounds(self) -> str:
        """
        • This will return the protected ground(s) of the applicant. Special
        checks are needed. Checking for keywords is not enough, as sometimes
        documents label laws that describe each protected ground. Examples
        are 'Purely Political Offense' and 'Real Id Act'.
        """
        protected_grounds: List[str] = [
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

            sent: str = token.sent.text.lower()

            s: Union[str, None] = similar_pg(token.text.lower(), 0.9)

            if s == 'social':
                next_word = self.doc[token.i + 1].text.lower()
                if not similar(next_word, 'group', 0.95):
                    continue

            elif s == 'political':
                next_word = self.doc[token.i + 1].text.lower()
                if similar(next_word, 'offense', 0.95):
                    continue

            elif s == 'nationality':
                next_word = self.doc[token.i + 1].text.lower()
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

        return '; '.join(set(pgs))

    def get_application(self) -> str:
        """
        • This will return the seeker's application, found after 'APPLICATION'.
        Because HRF is only interested in Asylum, Withholding of Removal,
        and Convention Against Torture applications, the others should be
        ignored and not included in the dataset.
        """
        app_types = {
            'CAT': ['Convention against Torture', 'Convention Against Torture'],
            'Asylum': ['Asylum', 'asylum', 'asylum application'],
            'Withholding of Removal': ['Withholding of Removal', 'withholding of removal'],
            'Other': ['Termination', 'Reopening', "Voluntary Departure",
                    'Cancellation of removal','Deferral of removal']
        }
        
        start = 0
        
        for token in self.doc:
            if token.text == 'APPLICATION':
                start += token.idx
                break
        
        outcome = set()
        for k,v in app_types.items():
            for x in v:
                if x in self.doc.text[start: start + 300]:
                    if k == "Other":
                        outcome.add(x)
                    else:
                        outcome.add(k)
        return "; ".join(list(outcome))

    def get_outcome(self) -> str:
        """
        • Returns the outcome of the case. This will appear after 'ORDER'
        at the end of the document.
        """
        outcomes = {
            'remanded',
            'reversal',
            'dismissed',
            'sustained',
            'terminated',
            'granted',
            'denied',
            'returned',
        }
        for token in self.doc:
            if token.text in {"ORDER", "ORDERED"}:
                start, stop = token.sent.start, token.sent.end + 50
                outcome = self.doc[start:stop].text.strip().replace("\n", " ")
                outcome = outcome.split('.')[0]
                if any(itm.lower() in outcomes for itm in outcome.split()):
                    return outcome
    
    def get_city_state(self):
        """
        Finds the city & state the respondent originally applied in. The function
        returns the state. City can be accessed as an attribute.
        """
        statecache = []
        citycache = set()

        fileloc = 0
        for token in self.doc:
            if token.text == 'File':
                fileloc += token.idx
                break

        for k in court_locs.keys():
            for s in re.findall(f"(?:{k})", self.doc.text[:750]):
                statecache.append(s)

        c = Counter(statecache)
        state = c.most_common(n=1)[0][0]

        for v in court_locs.get(state)['city']:
            for c in re.findall(f"(?:{v}, {state})", self.doc.text[:750]):
                citycache.add(v)
        
        if len(citycache) == 1:
            self.state = state
            self.city = list(citycache)[0]
            return state
        
        elif len(citycache) > 1:
            for c in citycache:
                if c in self.doc.text[fileloc: fileloc + 100]:
                    self.state = state
                    self.city = c
                    return state

        else:
            self.state = state
            self.city = "; ".join(list(citycache))
            return state


    def get_based_violence(self) -> Union[Dict[str, List[str]], None]:
        """
        • Returns a dictionary where the keys are:
            Family-based violence,
            Gender-based violence,
            Gang-based violence
        • If a key is in the dict, it means the based_violence is present
        in the document, and the relevant sentence(s) where the information is
        contained in the key's value
        """
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
            based_v = {k: list(set(v)) for k, v in based_v.items()}

        return based_v if based_v else None

    def references_AB27_216(self) -> bool:
        """
        • Returns True if the case file mentions
        Matter of AB, 27 I&N Dec. 316 (A.G. 2018)
        """
        for token in self.doc:
            if token.text == 'I&N':
                sent = token.sent.text
                if '316' in sent and '27' in sent:
                    return True
        return False

    def references_LEA27_581(self) -> bool:
        """
        • Returns True if the case file mentions
        Matter of L-E-A-, 27 I&N Dec. 581 (A.G. 2019)
        """
        for sent in self.doc.sents:
            if 'L-E-A-' in sent.text:
                if '27' in sent.text:
                    return True
        return False

    def get_gender(self) -> str:
        """
        • This field needs to be validated. Currently, it assumes the
        sex of the seeker by the number of instances of pronouns in the
        document.
        """
        male = 0
        female = 0

        for token in self.doc:
            if token.text in {'him', 'his', 'he'}:
                male += 1
            elif token.text in {'her', 'hers', 'she'}:
                female += 1

        if male > female:
            return 'male'
        elif female > male:
            return 'female'
        else:
            return 'unknown'

    def get_indigenous_status(self) -> str:
        """
        • If the term "indigenous" appears in the document, the field will return
        the name of asylum seeker's tribe/nation/group. Cuurently, the field will return
        the two tokens that precede "indigenous;" this method needs to be fine-tuned and
        validated.
        """
        # indigenous: List[str]
        # indigenous = [
        #     'indigenous'
        # ]
        #
        # similar_indig: Callable[[str, float], Union[str, None]]
        # similar_indig = similar_in_list(indigenous)
        #
        # for token in self.doc:
        #
        #     sent: str
        #     sent = token.sent.text.lower()
        #
        #     s: Union[str, None]
        #     s = similar_indig(token.text.lower(), 0.9)
        #
        #     if s == 'indigenous group':
        #         prev_wrds = self.doc[[token.i-1, token.i-2]].text.lower()
        #         # return the name of the specific group/nation
        #         return prev_wrds
        return "Test"

    def get_applicant_language(self) -> str:
        """
        • If the term "native speaker" appears in the document, the field will return
        the asylum seeker's stated native language. Currently, the field will return
        the two tokens that precede "native speaker;" this method needs to be fine-tuned and
        validated.
        """
        # for token in self.doc:
        #
        #     sent: str
        #     sent = token.sent.text.lower()
        #
        #     s: Union[str, None]
        #     s = similar_pg(token.text.lower(), 0.9)
        #
        #     if s == 'native speaker' or s == 'native speakers':
        #         next_wrds = self.doc[[token.i+1, token.i+2]].text.lower()
        #         return next_wrds
        #
        # return 'Ability to testify in English'
        return "Test"

    def get_access_interpeter(self) -> str:
        """
        • If the terms "interpreter" or "translator" appear in the document,
        the field will return whether the asylum seeker had access to an
        interpreter during their hearings. Currently, the field's output is
        dependent on occurrence of specific tokens in the document; this method
        needs to be fine-tuned and validated.
        """
        # for token in self.doc:
        #
        #     sent: str
        #     sent = token.sent.text.lower()
        #
        #     s: Union[str, None]
        #     s = similar_pg(token.text.lower(), 0.9)
        #
        #     if s == 'interpreter' or s == 'translator':
        #         surrounding: Span
        #         surrounding = self.get_surrounding_sents(token)
        #
        #         next_word = self.doc[token.i+1].text.lower()
        #         if 'requested' in surrounding.text.lower() \
        #             and 'granted' in surrounding.text.lower():
        #             return 'Had access'
        #         elif 'requested' in surrounding.text.lower() \
        #             and 'was present' in surrounding.text.lower():
        #             return 'Yes'
        #         elif 'requested' in surrounding.text.lower() \
        #             and 'granted' not in surrounding.text.lower():
        #             return 'No'
        #         elif 'requested' in surrounding.text.lower() \
        #             and 'was present' in surrounding.text.lower():
        #             return 'No'
        return "Test"

    def get_credibility(self) -> str:
        """
        • Returns the judge's decision on whether the applicant is a credible witness.
        Curently, the field's output is dependent on occurance of specific tokens
        in the document; this method needs to be fine-tuned and validated.
        """
        # credibility = [
        #     'credible'
        # ]
        # similar_cred: Callable[[str, float], Union[str, None]]
        # similar_cred = similar_in_list(credibility)
        # for token in self.doc:
        #     sent: str
        #     sent = token.sent.text.lower()
        #     s: Union[str, None]
        #     s = similar_cred(token.text.lower(), 0.9)
        #     if s == 'credible':
        #         prev_word = self.doc[token.i-1].text.lower()
        #         next_word = self.doc[token.i+1].text.lower()
        #         if not similar(prev_word, 'not', 0.95) \
        #             and not similar(next_word, 'witness', 0.95):
        #             return 'Yes'
        #         else:
        #             return 'No'
        #         if s not in self.doc:
        #             return 'N/A to case'
        return "Test"

    def check_for_one_year(self) -> bool:
        """
        Checks whether or not the asylum-seeker argued to be exempt from the
        one-year guideline.  Specifically, it checks to see if the document
        contains either "changed circumstance" or "extraordinary circumstance".
        If it does, and one of the five terms ("year", "delay", "time",
        "period", "deadline") is within 10 lemmas, then the function
        returns True.  Otherwise, it returns False.

        If one of the four context words are w/in 100 characters of the
        phrase, we conclude that it is related to the one-year rule
        """
        terms = ('year', 'delay', 'time', 'period', 'deadline')
        lemma_list = [token.lemma_.lower() for token in self.doc]

        for idx in range(0, len(lemma_list)):
            if lemma_list[idx] == 'change' and \
                    lemma_list[idx + 1] == 'circumstance':
                idx_start = lemma_list.index('change')
                idx_end = idx_start + 1
                search_list = [
                    lemma for lemma in lemma_list[idx_start - 10: idx_end + 10]
                ]
                if any(term in search_list for term in terms):
                    return True

        for idx in range(0, len(lemma_list)):
            if lemma_list[idx] == 'extraordinary' and \
                    lemma_list[idx + 1] == 'circumstance':
                idx_start = lemma_list.index('extraordinary')
                idx_end = idx_start + 1
                search_list = [
                    lemma for lemma in lemma_list[idx_start - 10: idx_end + 10]
                ]
                if any(term in search_list for term in terms):
                    return True

        return False
