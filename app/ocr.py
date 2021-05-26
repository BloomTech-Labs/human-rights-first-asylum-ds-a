"""
IMPORTS/LIBS
Imports of libraries and packages, including spacy nlp library, and reading in
court location dictionary
"""

import datetime
import json
import time
import geonamescache
import re
import requests
import pytesseract
from collections import Counter, defaultdict
from pdf2image import convert_from_bytes
from spacy import load
from spacy.tokens import Doc, Span, Token
from spacy.matcher import Matcher, PhraseMatcher



nlp = load("en_core_web_sm")

# Read in dictionary of all court locations
with open('./app/court_locations.json') as f:
    court_locs = json.load(f)

"""
MAKE FIELDS
This is the main overall function that creates a dictionary of the desired
fields and their respective values; info that goes into those fields.
"""

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
        'precedent cases': case.get_precedent_cases(),
        'statutes': case.get_statutes(),
    }
    time_taken = time.time() - start
    case_data["time to process"] = f"{time_taken:.2f} seconds"
    return case_data

"""
SIMILAR/Matcher functions
functions that search court document texts for phrases or specific words; used
in get_outcome, get_country_of_origin, get_outcome
"""

def similar(matcher_pattern, file):
    # create matcher object
    matcher = Matcher(nlp.vocab)
    # Add the pattern that is being searched for
        # make pattern within attribute functions below that use similar
        # Format: pattern = [{"LOWER": <word>}, {"LOWER": <the next word>}, ...etc]
    matcher.add('matcher_pattern', matcher_pattern)
    # return the "matcher" objects; as Span objects(human readable)
    return matcher(file, as_spans=True)

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


"""
LISTS
global info about judges; states and their court circuits
"""
# TODO: Find a way to add old immigration judges and new immigrations judges
    # not in this static list. Like, How do we keep an updated list of all
    # judges?
# I think only the appelate judge are below...nationwide there are around
    # 435
appellate_panel_members = [
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

US_abbrev = {
        'AL': 'Alabama',
        'AK': 'Alaska',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'AR': 'Arkansas',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DE': 'Delaware',
        'DC': 'District of Columbia',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'IA': 'Iowa',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'ME': 'Maine',
        'MD': 'Maryland',
        'MA': 'Massachusetts',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MS': 'Mississippi',
        'MO': 'Missouri',
        'MT': 'Montana',
        'NE': 'Nebraska',
        'NV': 'Nevada',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NY': 'New York',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'MP': 'Northern Mariana Islands',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VT': 'Vermont',
        'VI': 'Virgin Islands',
        'VA': 'Virginia',
        'WA': 'Washington',
        'WV': 'West Virginia',
        'WI': 'Wisconsin',
        'WY': 'Wyoming'
        }

"""CLASS and Get methods
The following defines the BIACase Class. When receiving a court doc, we use this
Class and the algorithms/methods to extract info for the desired fields/info
that are scraped from the text of the court docs.
"""

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
        # !!!get_appellate() needs to be called before get_panel()
        self.appellate = self.is_appellate(),
        self.application = self.get_application(),
        self.date = self.get_date(),
        self.country_of_origin = self.get_country_of_origin(),
        self.panel = self.get_panel(),
        # !!!get_outcome() needs to be called before get_protected_grounds()
        self.outcome = self.get_outcome(),
        # !!!get_state() needs to be called before get_city() and get_circuit()
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
    
    def get_ents(self, labels):
        """
        • Retrieves entitiess of a specified label(s) in the document,
        if no label is specified, returns all entities
        for example:
            if you input dates into this function it will return all of the dates in the corpus
        """
        return (ent for ent in self.ents if ent.label_ in labels)
    
    def get_circuit(self):
        '''returns the circuit the case started in.'''
        return circuit_dict[self.state]

    def get_country_of_origin(self) -> Union[str, None]:
        """
        RETURNS the respondent's or respondents' country of origin:
        """
        """Generate COUNTRIES list"""
        # sorted list of all current countries
        gc = geonamescache.GeonamesCache()
        countries = sorted(gc.get_countries_by_names().keys())
        # remove U.S. and its territories from countries
        if "American Samoa" in countries:
            countries.remove("American Samoa")
        if "Guam" in countries:
            countries.remove("Guam")
        if "Northern Mariana Islands" in countries:
            countries.remove("Northern Mariana Islands")
        if "Puerto Rico" in countries:
            countries.remove("Puerto Rico")
        if "United States" in countries:
            countries.remove("United States")
        if "United States Minor Outlying Islands" in countries:
            countries.remove("United States Minor Outlying Islands")
        if "U.S. Virgin Islands" in countries:
            countries.remove("U.S. Virgin Islands")
        """
        PRIMARY search:
        in most cases, the term/pattern "citizen(s) of" appears in the same
            sentence the country of origin spacy.matcher patterns list, looking
            for the following phrase matches following these patterns is
            practically guaranteed to be the country of origin
        """
        # create a spacy matcher pattern
        primary_pattern = [
            [{"LOWER": "citizen"}, {"LOWER": "of"}],
            [{"LOWER": "citizens"}, {"LOWER": "of"}],
        ]
        # instantiate a list of pattern matches
        spans = similar(primary_pattern, self.doc)
        # if there are matches
        if spans:
            # grab the surrounding sentence and turn it into a string
            sentence = str(spans[0].sent)
            # remove line breaks, edge case
            clean_sent = sentence.replace("\n", " ")
            # iterate through the countries list, and return it if it's in the
                # cleaned sentence
            for country in countries:
                if country in clean_sent:
                    return country
        
        #SECONDARY search:
        # If citizen of wasn't found or if it WAS found but no country followed,
        # look through the whole doc for the first instance of a non-U.S. country.
        else:
            # untokenize and normalize
            tok_text = str(self.doc).lower()
            # edge case where line breaks appear in the middle of a multi-word
                # country, an effect of turning the tokenized text to a string
            clean_text = tok_text.replace("\n", " ")
            # iterate through countries for a foreign entity.
            for country in countries:
                if country.lower() in clean_text:
                    return country
        
    def get_date(self) -> str:        
        """        
        • Returns date of the document. Easy to validate by the PDF filename.        
        """        
        dates = map(str, self.get_ents(['DATE']))        
        for s in dates:            
            if len(s.split()) == 3:                
                return s

    def get_panel(self) -> List[str]:
        """
        Uses the appellate_panel_members list and spacy PhraseMatcher to check a
        document for members in the appellate_panel_member list.
        !!! Currently only works for this static list of judges. If not appelate
            or the list of apppelate judges changes, or there's an appelate
            judge not in the list.
            May want to generate an updatable list.
            May want to generate a non-appellate judge list
            This has important interactions with "is_appellate()" function. If
                this function returns a judge, it IS from the appellate list,
                and is therefore an appellate case.
        """
         # create PhraseMatcher object with en_cor_web_md
        matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        # generate a list of patterns
        patterns = [nlp.make_doc(text) for text in appellate_panel_members]
        # add the patterns to the matcher's library
        matcher.add("panel_names", patterns)

        # Create a list for phrase matches(judge names) to go.
        matches = []
        # find all matches, anywhere in the doc, that is a name from the
        # appellate panel members list, and append them as spans(human readable)
        for match_id, start, end in matcher(self.doc):
            # to matches list
            span = self.doc[start:end]
            matches.append(span.text)
        # if matches were found, return the list of panel members
        if matches:
            return sorted(set(matches))
        # otherwise, the judge is in the appellate list; either not in the list
            # or not an appellate judge
        else:
            return [] # IS THIS OKAY?

    def get_gender(self):
        """
        Searches through a given document and counts the TOTAL number of "male"
        pronoun uses and "female" pronoun uses. Whichever count("M" or "F") is
        higher, that gender is returned.
        In the event of a tie; currently returns "Unknown"; may be able to code
        for this edge case. Current accuracy is >95%, low priority fix.
        """
        # List if gendered pronouns
        male_prons = ['he', "he's", 'his', 'him', 'himself']
        female_prons = ['she', "she's", 'her', 'hers', 'herself']

        # list for spacy.matcher pattens
        f_patterns = []
        m_patterns = []

        # generating list of patterns (f: pattern = [{'LOWER': word}]), for
            # spacy matcher search

        for prons in female_prons:
            f_patterns.append([{'LOWER':prons}])
        for prons in male_prons:
            m_patterns.append([{'LOWER':prons}])

        # use simlar() function (Above) to find patterns(pronouns) in whole text
        m_similar = similar(m_patterns, self.doc)
        f_similar = similar(f_patterns, self.doc)

        # check the number of gendered pronoun occurrences and return gender
        if len(m_similar) > len(f_similar):
            return 'Male'
        elif len(f_similar) > len(m_similar):
            return 'Female'
        else:
            return 'Unknown'

    def get_protected_grounds(self) -> str:
        """
        This will return the protected ground(s) of the applicant. Special
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

        religions = ['christianity','christian','islam','atheist','hinduism',
                     'buddihism','jewish','judaism','islamist','sunni','shia',
                     'muslim','buddhist','atheists','jew','hindu', 'atheism']

        politicals = ['political opinion', 'political offense']
        confirmed_matches = []
        # create pattern for specified religions
        for religion in religions:
            pattern.append([{"LOWER": religion}])


        potential_grounds = similar(matcher_pattern=pattern, file=self.doc)
        
        for match in potential_grounds:
        # remove 'nationality act' from potential_grounds
            if match.text.lower() == 'nationality':
                if 'act' in match.sent.text.lower():
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
        outcomes_list = ['denied', 'dismissed', 'granted', 'remanded', 'returned',
                         'reversal', 'sustained', 'terminated', 'terninated', 'vacated']

        # locate where in the document the orders start
        order_start_i = -1
        for token in self.doc:
            if str(token) in ordered_outcome:
                order_start_i = token.i
                break
                
        # If we can't find where the orders start, assume there aren't any
        if order_start_i == -1:
            return []
        
        # Locate where in the document the orders end
        order_end_i = min(order_start_i+175, len(self.doc))
        # Orders end when we see "FOR THE COURT" - this avoids finding keywords in footnotes
        for i in range(order_start_i+1, min(order_end_i, len(self.doc)-2)):
            if str(self.doc[i]) == "FOR" and str(self.doc[i+1]) == "THE" and str(self.doc[i+2]) == "BOARD":
                order_end_i = i
                break
                
        # If we can find where the orders start, check it for each type of outcome
        for outcome in outcomes_list:
            for i in range(order_start_i, order_end_i):
                if str(self.doc[i]) == outcome:
                    outcomes_return.append(outcome)
                    break
                
        return outcomes_return    

    def is_appellate(self.doc):
        if self.judge_list:
            self.appellate = True
        else:
            self.appellate = False
    

    def get_state(self):
        """
        IF the case is an appellate decision the first page will show 
        the legal teams' address on page 1, and the respondents address 
        on page 2. We need to decide if appellate before getting state.

        Finds the city & state the respondent originally applied in. The function
        returns the state. City can be accessed as an attribute.
        """
        
        pattern = [
            [{"LOWER": 'file'}],
            [{"LOWER": 'files'}]
            ]

        matches = similar(self.doc, pattern)

        sentence = str(matches[0].sent)
        clean_sentence = sentence.replace(',', ' ').replace('\n', ' ')

        #if an appellate case the first page will have the location of the appellate court, NOT origin
        if self.appellate == True:
            
            #finds first state that's in the citycache
            for abbrev in clean_sentence:
                if abbrev in US_abbrev.keys():
                    self.state = abbrev
                    return self.state
            
        else:
            #if non-appellate the first page will have the court location including city & state
            for s in self.doc:
                if s in US_abbrev.keys():
                    self.state = s
                    return self.state

    def get_city(self, self.state):
        #uses the abbreviation from self.state and #gets the list of cities in a state
        citycache = set()
        for v in court_locs.get(self.state)['city']:
            citycache.add(v)

        pattern = [
            [{"LOWER": 'file'}],
            [{"LOWER": 'files'}]
            ]

        matches = similar(self.doc, pattern)

        sentence = str(matches[0].sent)
        clean_sentence = sentence.replace(',', ' ').replace('\n', ' ').title()

        #if an appellate case the first page will have the location of the appellate court, NOT origin
        if self.appellate == True:
            
            #finds first city that's in the citycache
            for word in clean_sentence:
                if word in citycache:
                    self.city = word
                    return self.city
            
        else:
            #if non-appellate the first page will have the court location including city & state
            for s in self.doc:
                if s in citycache:
                    self.city = s
                    return self.city
            

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
