import time
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
from fuzzywuzzy import process


nlp = load("en_core_web_sm")

# Read in dictionary of all court locations
with open('./app/court_locations.json') as f:
    court_locs = json.load(f)


def make_fields(file) -> dict:
    start = time.time()
    pages = convert_from_bytes(file, dpi=90)
    text = map(pytesseract.image_to_string, pages)
    string = " ".join(text)
    case = BIACase(string)
    case_data = {
        'application': case.application,
        'date': case.date,
        'country of origin': case.country_of_origin,
        'panel members': case.panel,
        'outcome': case.outcome,
        'state of origin': case.state,
        'city of origin': case.city,
        'circuit of origin': case.circuit,
        'protected grounds': case.protected_grounds,
        'based violence': case.based_violence,
        'gender': case.gender,
        'indigenous': case.indigenous_status,
        'applicant language': case.applicant_language,
        'credibility': case.credibility,
        'check for one year': case.one_year,
        'precedent cases': case.precedent_cases,
        'statutes': case.statutes,
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

def similar_outcome(str1, str2):
    """
    Returns True if the strings are off by a single character, and that 
    character is not a 'd' at the end. That 'd' at the end of a word is highly 
    indicative of whether something is actually an outcome.
    
    This is used in the get_outcome() method.
    """
    if abs(len(str1) - len(str2)) > 1:
        return False
    min_len = min(len(str1), len(str2))
    i = 0
    while i < min_len and str1[i] == str2[i]:
        i += 1

    # We've reached the end of one string, the other is one character longer
    if i == min_len:
        # If that character is a 'd', return False, otherwise True
        if ((len(str1) > len(str2) and str1[-1] == 'd') 
            or (len(str2) > len(str1) and str2[-1] == 'd')):
            return False
        else:
            return True

    # We're looking at a substitution that is 'd' at the end
    if (i == len(str1) -1 and len(str1) == len(str2) 
        and (str1[-1] == 'd' or str2[-1] == 'd')):
        return False

    # We're looking at a substitution other than 'd' at the end
    i2 = i + 1
    while i2 < min_len and str1[i2] == str2[i2]:
        i2 += 1
    if i2 == len(str1) and i2 == len(str2):
        return True

    # We're in the middle, str1 has an extra character
    if len(str1) == len(str2) + 1:
        i2 = i
        while i2 < min_len and str1[i2+1] == str2[i2]:
            i2 += 1
        if i2 + 1 == len(str1) and i2 == len(str2):
            return True

    # We're in the middle, str2 has an extra character
    if len(str1) + 1 == len(str2):
        i2 = i
        while i2 < min_len and str1[i2] == str2[i2+1]:
            i2 += 1
        if i2 == len(str1) and i2 + 1 == len(str2):
            return True

    return False

def similar_protected_grounds(target_phrases, file):
    ''' 
    Creates SpaCy matcher that searches for specified target_phrases
    '''
    matcher = Matcher(nlp.vocab)
    matcher.add('target_phrases', target_phrases)
    matches = matcher(file, as_spans=True)
    # matches returned are SpaCy Spans object
    # in the functions where similiar is used
    # must present target_phrases in a list of dictionary using Spacy pattern syntax
    # example pattern = [[{"LOWER": "race"}]

    return matches

def in_parenthetical(match, doc):
    '''
    Checks for text wrapped in parathesis, and removes any
    returned protected grounds if they we're wrapped in parenthesis 
    used in protected grounds in order to improve accuracy
    '''
    open_parens = 0
    for i in range(match.end, len(doc)):
        if doc[i].text == '(':
            open_parens += 1
        elif doc[i].text == ')':
            if open_parens > 0:
                open_parens -= 1
            else:
                return True
        elif doc[i] in {'.', '?', '!'}:
            return False
    return False

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


circuit_dict = {
    '''used by get_circuit'''
    'DC': 'DC', 'ME': '1', 'MA': '1', 'VT': '1', 'RI': '1', 'PR': '1', 
    'CT': '2', 'NY': '2', 'VT': '2', 'DE': '3', 'PA': '3', 'NJ': '3', 'VI': '3',
    'MD': '4', 'VA': '4', 'NC': '4', 'SC': '4', 'WV': '4', 'LA': '5', 'MS': '5',
    'TX': '5', 'KY': '6', 'OH': '6', 'TN': '6', 'MI': '6', 'IL': '7', 'IN': '7',
    'WI': '7', 'AK': '8', 'IA': '8', 'MN': '8', 'MO': '8', 'NE': '8', 'ND': '8',
    'SD': '8', 'AK': '9', 'AZ': '9', 'CA': '9', 'GU': '9', 'HI': '9', 'ID': '9',
    'MT': '9', 'NV': '9', 'MP': '9', 'OR': '9', 'WA': '9', 'CO': '10', 
    'KS': '10', 'NM': '10', 'OK': '10', 'UT': '10', 'WY': '10', 'AL': '11',
    'FL': '11', 'GA': '11'
 }

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
        # get_appellate() needs to be called before get_panel()
        self.appellate = self.get_appellate(), 
        self.application = self.get_application(),
        self.date = self.get_date(),
        self.country_of_origin = self.get_country_of_origin(),
        self.panel = self.get_panel(),
        # get_outcome() needs to be called before get_protected_grounds()
        self.outcome = self.get_outcome(), 
        # get_state() needs to be called before get_city() and get_circuit()
        self.state = self.get_state(), 
        self.city = self.get_city()
        self.circuit = self.get_circuit()
        self.protected_grounds = self.get_protected_grounds(),
        self.based_violence = self.get_based_violence(),
        self.gender = self.get_gender(),
        self.indigenous_status = self.get_indigenous_status(),
        self.applicant_language = self.get_applicant_language(),
        self.credibility = self.get_credibility(),
        self.one_year = self.check_for_one_year(),
        self.precedent_cases = self.get_precedent_cases(),
        self.statutes = self.get_statutes(),

    def get_ents(self, labels: List[str]) -> Iterator[Span]:
        """
        • Retrieves entitiess of a specified label(s) in the document,
        if no label is specified, returns all entities
        """
        return (ent for ent in self.ents if ent.label_ in labels)

    def get_circuit(self):
        '''returns the circuit the case started in.'''
        return circuit_dict[self.state]
    
    def get_appellate(self):
        '''this still needs to be implemented'''
        return True

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
        # Format: MM/DD/YYYY
        pattern_1 = [{'TEXT': {'REGEX': r'^\d{1,2}/\d{1,2}/\d{2}(?:\d{2})?$'}}]

        # Format: Month DD, YYYY
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
        # Backend requested output format: 'yyyy-mm-dd'
        return '{}-{}-{}'.format(sorted_dates[0].year, sorted_dates[0].month, sorted_dates[0].day)

    def get_panel(self) -> List[str]:
         """
         • Returns a list of panel members for appellate case documents.
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

         return list(case_panel_members)


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

    def get_protected_grounds(self):
        """
        • This will return the protected ground(s) of the applicant. Special
        checks are needed. Checking for keywords is not enough, as sometimes
        documents label laws that describe each protected ground. Examples
        are 'Purely Political Offense' and 'Real Id Act'.
        """
        pattern = [
        [{"LOWER": "race"}], 
        [{"LOWER": "religion"}], # expand to check for list of religions
        [{"LOWER": "nationality"}], # currently, phrase is pulled but out of context
        [{"LOWER": "social"}, {"LOWER": "group"}], 
        [{"LOWER": "political"}, {"LOWER": "opinion"}],
        [{"LOWER": "political"}, {"LOWER": "offense"}],
        [{"LOWER": "political"}],
        ]

        religions = ['christianity','christian','islam','atheist','hinduism',
                     'buddihism','jewish','judaism','islamist','sunni','shia',
                    'muslim','buddhist','atheists','jew','hindu', 'atheism']

        politicals = ['political opinion', 'political offense']

        confirmed_matches = []

        # create pattern for specified religions
        for religion in religions:
            pattern.append([{"LOWER": religion}])

        potential_grounds = similar_protected_grounds(target_phrases=pattern, file=self.doc)

        for match in potential_grounds:
        # remove 'nationality act' from potential_grounds
            if match.text.lower() == 'nationality':
                if 'act' in match.sent.text.lower():
                    continue

                else:
                    if 'nationality' not in confirmed_matches:
                        confirmed_matches.append('nationality')

        # check for specified religion, replace with 'religion'
            elif match.text.lower() in religions:
                if 'religion' not in confirmed_matches:
                    confirmed_matches.append('religion')

            elif match.text.lower() in politicals:
                if 'political' not in confirmed_matches:
                    confirmed_matches.append('political')
            
            else:
                confirmed_matches.append(match.text.lower())
        
        if confirmed_matches:
            return list(set(confirmed_matches))
        
        else:
            return []

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
                      'Cancellation of removal', 'Deferral of removal']
        }

        start = 0

        for token in self.doc:
            if token.text == 'APPLICATION':
                start += token.idx
                break

        outcome = set()
        for k, v in app_types.items():
            for x in v:
                if x in self.doc.text[start: start + 300]:
                    if k == "Other":
                        outcome.add(x)
                    else:
                        outcome.add(k)
        return "; ".join(list(outcome))

    def get_outcome(self) -> List[str]:
        """
        • Returns list of outcome terms from the case in a list.
          These will appear after 'ORDER' at the end of the document.
        """

        outcomes_return = []
        ordered_outcome = {'ORDER', 'ORDERED'}
        outcomes_list = ['denied', 'dismissed', 'granted', 'remanded',
                         'returned', 'sustained', 'terminated',
                         'vacated', 'affirmed']
        two_before_exclusion = {'may', 'any', 'has'}
        one_before_exclusion = {'it', 'has'}

        # locate where in the document the orders start
        order_start_i = -1
        for token in self.doc:
            if token.text in ordered_outcome:
                order_start_i = token.i
                break

        # If we can't find where the orders start, check the whole opinion
        if order_start_i == -1:
            order_start_i = 0

        # Locate where in the document the orders end
        order_end_i = len(self.doc)
        # Orders end when we see "FOR THE BOARD" or "WARNING"
        # - this avoids finding keywords in footnotes or warnings
        for i in range(order_start_i+1, min(order_end_i, len(self.doc) - 2)):
            if (self.doc[i:i+3].text == "FOR THE BOARD" or
                self.doc[i].text == "WARNING"):
                order_end_i = i
                break

        # Check the range for each type of outcome
        for outcome in outcomes_list:
            for i in range(order_start_i, order_end_i):
                if (similar_outcome(self.doc[i].text, outcome) and
                    self.doc[i-2].text not in two_before_exclusion and
                    self.doc[i-1].text not in one_before_exclusion):
                    outcomes_return.append(outcome)
                    break

        return outcomes_return

    def get_state(self):
        '''this still needs to be implemented'''
        return 'New California'

    def get_city(self):
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

    def get_based_violence(self) -> List[str]:
        """
        Returns a list of keyword buckets which indicate certain types of violence mentioned in a case,
        current buckets are: Violence, Family, Gender, and Gangs.
        These keywords can be changed in their respective lists, and an item being present in the list
        means that the given type of violence is mentioned in the document.
        """

        # Converts words to lemmas & inputs to nlp-list, then searches for matches in the text
        def get_matches(input_list, topic, full_text):
            temp_matcher = PhraseMatcher(full_text.vocab, attr="LEMMA")
            for n in range(0, len(input_list)):
                input_list[n] = nlp(input_list[n])
            temp_matcher.add(topic, input_list)
            temp_matches = temp_matcher(full_text)
            return temp_matches

        # Lists of keywords that fall within a bucket to search for
        terms_list = []
        violent_list = ['abduct', 'abuse', 'assassinate', 'assault', 'coerce', 'exploit',
                        'fear', 'harm', 'hurt', 'kidnap', 'kill', 'murder', 'persecute',
                        'rape', 'scare', 'shoot', 'suffer', 'threat', 'torture']
        family_list = ['child', 'daughter', 'family', 'husband', 'parent', 'partner', 'son', 'wife', 'woman']
        gender_list = ['fgm', 'gay', 'gender', 'homosexual', 'homosexuality', 'lesbian', 'lgbt', 'lgbtq', 'lgbtqia',
                       'queer', 'sexuality', 'transgender']
        gang_list = ['cartel', 'gang', 'militia']

        # Outputs a list of PhraseMatch occurrences for a given list of keywords
        violence_match = get_matches(violent_list, 'Violent', self.doc)
        family_match = get_matches(family_list, 'Family', self.doc)
        gender_match = get_matches(gender_list, 'Gender', self.doc)
        gang_match = get_matches(gang_list, 'Gang', self.doc)

        # Printing full_text[judge_match2[0][1]:judge_match2[0][2]] gives word it matches on, can put in the [0] a
        # for loop to see all matches
        if len(violence_match) != 0:
            terms_list.append('Violent')
        if len(family_match) != 0:
            terms_list.append('Family')
        if len(gender_match) != 0:
            terms_list.append('Gender')
        if len(gang_match) != 0:
            terms_list.append('Gang')
        return terms_list

    def get_precedent_cases(self) -> List[str]:
        """"
        Returns a list of court cases mentioned within the document, i.e. 'Matter of A-B-' and 'Urbina-Mejia v. Holder'
         """
        # These lists were largely gotten through trial and error & don't work as well on non-GCP documents initially
        # set rules were broken & hardcoded stops made most sense when considering punctuation & mis-reads by OCR
        cases_with_dupes = []
        ok_words = {'&', "'", ',', '-', '.', 'al', 'et', 'ex', 'n', 'rel'}
        reverse_break_words = {'(', '(IJ', 'Cf', 'Compare', 'He', 'I&N', 'IN', 'In', 'Section', 'See', 'She', 'Under',
                               'While', 'and', 'as', 'at', 'because', 'cf', 'e.g.', 'in', 'is', 'procedural', 'section',
                               'see', 'was'}
        break_words = {'(', '(IJ', ',', '.', '....', 'Compare', 'He', 'I&N', 'IN', 'In', 'Section', 'See', 'She',
                       'Under', 'While', 'and', 'as', 'at', 'because', 'e.g.', 'in', 'is', 'procedural', 'section',
                       'see', 'was'}
        for token in self.doc:
            # Append 'X v. Y' precedent case: k loop extracts X, l loop extracts Y
            if str(token) == 'v.':
                test_index = token.i
                vs_start = 0
                vs_end = 0
                for k in range(test_index - 1, test_index - 15, -1):
                    if (str(self.doc[k])[0].isupper() == False and str(self.doc[k]) not in ok_words):
                        vs_start = k + 1
                        break
                    if (str(self.doc[k])[0].isupper() == True and str(self.doc[k]) in reverse_break_words):
                        vs_start = k + 1
                        break
                for l in range(test_index, test_index + 15):
                    if (str(self.doc[l]) == ',' or str(self.doc[l]).isnumeric() == True or str(
                            self.doc[l]) in break_words):
                        vs_end = l
                        break
                if str(self.doc[vs_start:vs_end]) not in cases_with_dupes:
                    cases_with_dupes.append(str(self.doc[vs_start:vs_end]))

            # Append 'Matter of X' precedent cases 
            if str(token) == 'Matter':
                start_index = token.i
                false_flag = False
                end_index = 0
                for j in range(start_index, start_index + 15):
                    # OCR misclassifies 'Matter of Z-Z-O-' as 'Matter of 2-2-0' enough times to need to hardcode this in
                    if str(self.doc[j]).isnumeric() == True:
                        if (str(self.doc[j])) == '2' or (str(self.doc[j]) == '0'):
                            continue
                        else:
                            end_index += 1
                            break
                    if (str(self.doc[j])) in break_words or (str(self.doc[j]).isnumeric() == True):
                        end_index = j
                        break
                    if str(self.doc[j]) == ':':
                        false_flag = True
                        break
                if not false_flag:
                    temp_var = str(self.doc[start_index:end_index])
                    if temp_var not in cases_with_dupes:
                        cases_with_dupes.append(temp_var)
        cases_with_dupes = sorted(cases_with_dupes)

        # k loop removes incorrect suffixes, l loop removes incorrect prefixes & prevents duplicates from being added.
        clean_cases = []
        final_cases = []
        for k in range(0, len(cases_with_dupes)):
            if (cases_with_dupes[k][0:-1] not in clean_cases and cases_with_dupes[k][0:-1] != ''):
                clean_cases.append(cases_with_dupes[k])
        for l in range(0, len(clean_cases)):
            if (clean_cases[l][0:2] == '. ' or clean_cases[l][0:2] == ', '):
                if clean_cases[l][0:2] not in final_cases:
                    final_cases.append(clean_cases[l][2:])
            elif clean_cases[l][0:3] == '., ':
                if clean_cases[l][0:2] not in final_cases:
                    final_cases.append(clean_cases[l][3:])
            elif clean_cases[l] not in final_cases:
                final_cases.append(clean_cases[l])
        return [s.replace('\n', ' ').replace('  ', ' ') for s in final_cases]

    def get_statutes(self) -> dict:
        """Returns statutes mentioned in a given .txt document as a dictionary: {"""
        # Removes patterns with only words instead of numbers,
        # and matches known statute patterns' shape using spacy to be added
        not_in_test = {'Xxx', 'xxx', 'XXX'}
        statutes_list = []
        for token in self.doc:
            word_shape_match = str(token.shape_)
            if word_shape_match[0:3] not in not_in_test:

                # Matches shape of statutes- these can have 3-4 prefixes, 0-2 suffixes,
                # and extracts all subsections if there isn't a space between any of them
                statute_shape_match = str(token.shape_).replace('x','d').replace('X','d')
                if(statute_shape_match[0:4] == 'ddd(' or statute_shape_match[0:4] == 'ddd.' or statute_shape_match[0:5] == 'dddd.' or statute_shape_match[0:5] == 'dddd(' or statute_shape_match[0:6] == 'ddddd.' or statute_shape_match[0:6] == 'ddddd('):
                    # Close any open parentheses & append if not already present
                    has_open_paren = False
                    temp_token3 = str(token)
                    for i in range(0, len(temp_token3)):
                        if temp_token3[i] == "(":
                            has_open_paren = True
                        if temp_token3[i] == ")":
                            has_open_paren = False
                    if has_open_paren == True:
                        temp_token3 = temp_token3 + ')'
                    if temp_token3 not in statutes_list:
                        statutes_list.append(temp_token3)
        statutes_list = sorted(statutes_list)

        # Creates a dictionary with the key being the type of statute,
        # and value being the listed statutes determined by the first 4 numbers in a statute.
        return_dict = {}
        CFR = []
        INA = []
        other = []
        USC = []
        for j in range(0, len(statutes_list)):
            if (statutes_list[j][0:4].isnumeric() == True):
                if (int(statutes_list[j][0:4]) >= 1000 and int(statutes_list[j][0:4]) <= 1003):
                    CFR.append(statutes_list[j])
                    continue
                elif (int(statutes_list[j][0:4]) >= 1100 and int(statutes_list[j][0:4]) <= 1999):
                    USC.append(statutes_list[j])
                    continue
                else:
                    other.append(statutes_list[j])
                    continue
            elif (statutes_list[j][0:3].isnumeric() == True):
                if (int(statutes_list[j][0:3]) >= 100 and int(statutes_list[j][0:3]) <= 199):
                    USC.append(statutes_list[j])
                    continue
                elif (int(statutes_list[j][0:3]) >= 200 and int(statutes_list[j][0:3]) <= 399):
                    INA.append(statutes_list[j])
                    continue
                else:
                    other.append(statutes_list[j])
                    continue
            else:
                other.append(statutes_list[j])

        return_dict["CFR"] = CFR
        return_dict["INA"] = INA
        return_dict["Other"] = other
        return_dict["USC"] = USC
        return return_dict

    def get_gender(self) -> str:
        """
        Based on sentences where the Respondent/Applicant keywords are found,
        count the instances of gendered pronouns. This approach assumes the
        sentence refers to subject in shorthand by using gendered pronouns
        as opposed to keywords multiple times in sentence. This function
        returns a final result to be packaged into json.
        Parameters:
        spacy.doc (obj):
        Returns:
        str: Gender
        """

        # Search terms formatted
        phrases = ["respondent", "respondents", "applicant", 'filed an application']
        patterns = [nlp(text) for text in phrases]

        # Gender constants
        male_prons = ['he', "he's", 'his', 'himself']
        female_prons = ['she', "she's", 'her', 'herself']

        # Variables for analysis storage
        male_found = []
        female_found = []

        # PhraseMatcher setup, add tag (RESP) and pass in patterns
        phrase_matcher = PhraseMatcher(nlp.vocab, attr='LEMMA')
        phrase_matcher.add("RESP", None, *patterns)

        # Sentences with both 'RESP' tag and gendered pronouns added to respective list
        for sent in self.doc.sents:
            for match_id, _, _ in phrase_matcher(nlp(sent.text)):
                if nlp.vocab.strings[match_id] in ['RESP', *male_prons]:
                    male_found.append(sent.text)
                elif nlp.vocab.strings[match_id] in ['RESP', *female_prons]:
                    female_found.append(sent.text)

        # Make `set()` of list to eliminate duplicates and compare lengths
        if len(set(female_found)) > len(set(male_found)):
            return "Female"
        elif len(set(male_found)) > len(set(female_found)):
            return "Male"
        else:
            return "Unknown"

    def get_indigenous_status(self) -> str:
        """
        • If the term "indigenous" appears in the document, the field will return
        the name of asylum seeker's tribe/nation/group. Currently, the field will return
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
