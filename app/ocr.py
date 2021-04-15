import time
from typing import List, Tuple, Union, Callable, Dict, Iterator
from collections import defaultdict
from difflib import SequenceMatcher

import pytesseract
from pdf2image import convert_from_bytes
from bs4 import BeautifulSoup
import geonamescache
import requests
from spacy import load
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.tokens.token import Token
from spacy.matcher import Matcher

nlp = load("en_core_web_sm")

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


class Judges:
    """Grabs a list of judges from Wikipedia"""

    def __init__(self):
        judges_url = 'https://en.wikipedia.org/wiki/Board_of_Immigration_Appeals'
        html = requests.get(judges_url).text
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find("table", class_="wikitable")
        self.names = [itm.get_text().strip() for itm in table.select("td")[1::4]]


class BIACase:
    def __init__(self, text: str):
        """
        • Input will be text from a BIA case pdf file, after the pdf has
        been converted from PDF to text.
        • Scraping works utilizing spaCy, tokenizing the text, and iterating
        token by token searching for matching keywords.
        """
        self.matcher = Matcher(nlp.vocab)
        self.doc: Doc = nlp(text)
        self.ents: Tuple[Span] = self.doc.ents
        self.names = Judges()

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
        • Returns date of the document. Easy to validate by the PDF filename.
        """
        dates = map(str, self.get_ents(['DATE']))
        for s in dates:
            if len(s.split()) == 3:
                return s

    def get_panel(self) -> str:
        """
        • Returns the panel members of case in document.
        """
        # Go through our list of judges and check if they are in our document
        for judge in self.judges.names:
            # We need to put the last name first. Start by splitting the name
            judge_name_list = judge.split()

            # empty list to hold spacy pattern
            pattern = []

            # Go through each part of the name (first -> last), and place accordingly
            for part_of_name in judge_name_list:
                # If it is the last name, put it at the beginning
                if part_of_name == judge_name_list[-1]:
                    pattern.insert(0, {'TEXT' : part_of_name})
                else: # append first or middle name
                    pattern.append({'TEXT' : part_of_name})
            
            # Insert a comma at index 1 (after last name at index 0)
            pattern.insert(1, {'TEXT' : ','}) 
            
            # add pattern to matcher -> (<pattern_id>, <callback>, <pattern>)
            self.matcher.add('JUDGES_PATTERN', None, pattern)
            # Run matcher over document and get matches
            matches = self.matcher(self.doc)

        # container for panel members
        panel_members = []

        # for match in in matches
        for match_id, start, end in matches:
            # create a spacy span from values given to encapsulate the name
            matched_span = self.doc[start:end]
            # Append the text of the span to panel_members list
            panel_members.append(matched_span.text)

        # Join the set of panel members into a string
        return '; '.join(set(panel_members))

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
        except:
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
                for i in range(1, 30):
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

        return '; '.join(k for k, v in application.items() if v)

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
