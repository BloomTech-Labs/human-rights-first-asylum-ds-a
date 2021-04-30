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
from fuzzywuzzy import process


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
        'precedent cases': case.get_precedent_cases(),
        'statutes': case.get_statutes(),
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


class GetJudge:
    """ Returns the judge's name if a match is found. """
    accuracy = 0.7

    def __init__(self):
        judges_url = 'https://www.justice.gov/eoir/eoir-immigration-court-listing#MP'
        html = requests.get(judges_url).text
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all("tbody")
        names = []
        for table in tables:
            for judges in table.find_all('tr')[2:]:
                names.extend(list(judges)[4].get_text().strip().replace('\t', '').split('\n'))

        judges_url = 'https://www.justice.gov/eoir/board-of-immigration-appeals-bios'
        html = requests.get(judges_url).text
        soup = BeautifulSoup(html, 'html.parser')
        body_div = soup.find("div", class_='bodytext')
        bolded_names = body_div.find_all('b')
        names.extend([name.get_text() for name in bolded_names])
        strong_names = body_div.find_all('strong')
        names.extend([name.get_text() for name in strong_names][1:-1])
        self.is_judge: Callable = similar_in_list(names)

    def __call__(self, name):
        result = self.is_judge(name, self.accuracy)
        if not result:
            flip_name = ' '.join(reversed(name.split(', ')))
            result = self.is_judge(flip_name, self.accuracy)
        return result


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
        self.if_judge = GetJudge()
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
        • Returns the panel members of case in document.
        """
        panel_members: List[str]
        panel_members = []
        possible_members: Iterator[Span]
        possible_members = map(
            lambda ent: ent.text, self.get_ents(['PERSON'])
        )
        for member in possible_members:
            judge: Union[str, None]
            judge = self.if_judge(member)
            if judge:
                panel_members.append(judge)

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
        • Returns list of outcome terms from the case in a list. These will appear after 'ORDER' at the end of the document.
        """
        outcomes_return = []
        ordered_outcome = {'ORDER', 'ORDERED'}
        outcomes_list = ['denied','dismissed','granted','remanded','returned','reversal','sustained','terminated','terninated','vacated']
        #Interesting edge case in 349320269- typo on 'terminated' present in the pdf: fuzzywuzzy matches terminated to [(terninated, 90)]
        for token in self.doc:
            if(str(token) in ordered_outcome):
                # Can be changed to append on partial match: len(fuzzy_match[0][0]) > 5 and fuzzy_match[0][1] >= 90
                for n in range(0, len(outcomes_list)):
                    fuzzy_match = process.extract(outcomes_list[n], self.doc[token.i:token.i+175], limit=1)
                    if(fuzzy_match[0][1] == 100):
                        outcomes_return.append(outcomes_list[n])
                break
        return outcomes_return
    
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


    def get_based_violence(self) -> List[str]:
        """
        Returns a list of keyword buckets which indicate certain types of violence mentioned in a case, current buckets are: Violence, Family, Gender, and Gangs.
        These keywords can be changed in their respective lists, and an item being present in the list means that the given type of violence is mentioned in the document.
        """
        #Converts words to lemmas & inputs to nlp-list, then searches for matches in the text
        def get_matches(input_list, topic, full_text):
            temp_matcher = PhraseMatcher(full_text.vocab, attr="LEMMA")
            for n in range(0, len(input_list)):
                input_list[n] = nlp(input_list[n])
            temp_matcher.add(topic, input_list)    
            temp_matches = temp_matcher(full_text)
            return temp_matches

        # Lists of keywords that fall within a bucket to search for
        terms_list = []
        violent_list = ['abduct', 'abuse', 'assassinate', 'assault', 'coerce', 'exploit', 'fear', 'harm', 'hurt', 'kidnap', 'kill', 'murder', 'persecute', 'rape', 'scare', 'shoot', 'suffer', 'threat', 'torture']
        family_list = ['child', 'daughter', 'family', 'husband', 'parent', 'partner', 'son', 'wife', 'woman']
        gender_list = ['fgm', 'gay', 'gender', 'homosexual', 'homosexuality', 'lesbian', 'lgbt', 'lgbtq', 'lgbtqia', 'queer', 'sexuality', 'transgender']
        gang_list = ['cartel', 'gang', 'militia']    

        # Outputs a list of phrasematch occurences for a given list of keywords
        violence_match = get_matches(violent_list, 'Violent', self.doc)
        family_match = get_matches(family_list, 'Family', self.doc)
        gender_match = get_matches(gender_list, 'Gender', self.doc)
        gang_match = get_matches(gang_list, 'Gang', self.doc)

        # Printing full_text[judge_match2[0][1]:judge_match2[0][2]] gives word it matches on, can put in the [0] a for loop to see all matches
        if(len(violence_match) != 0):
            terms_list.append('Violent')
        if(len(family_match) != 0):
            terms_list.append('Family')
        if(len(gender_match) != 0):
            terms_list.append('Gender')
        if(len(gang_match) != 0):
            terms_list.append('Gang')
        return terms_list

    def get_precedent_cases(self) -> List[str]:
        """"Returns a list of court cases mentioned within the document, i.e. 'Matter of A-B-' and 'Urbina-Mejia v. Holder'"""
        # These lists were largely gotten through trial and error & don't work as well on non-GCP documents- initially set rules were broken & hardcoded stops made most sense when considering punctuation & mis-reads by OCR
        cases_with_dupes = []
        ok_words = {'&', "'", ',', '-', '.', 'al', 'et', 'ex', 'n', 'rel'}
        reverse_break_words = {'(', '(IJ', 'Cf', 'Compare', 'He', 'I&N', 'IN', 'In', 'Section', 'See', 'She', 'Under', 'While', 'and', 'as', 'at', 'because', 'cf', 'e.g.', 'in', 'is', 'procedural', 'section', 'see', 'was'}
        break_words = {'(', '(IJ', ',', '.', '....', 'Compare', 'He', 'I&N', 'IN', 'In', 'Section', 'See', 'She', 'Under', 'While', 'and', 'as', 'at', 'because', 'e.g.', 'in', 'is', 'procedural', 'section', 'see', 'was'}
        for token in self.doc:  
            # Append 'X v. Y' precedent case: k loop extracts X, l loop extracts Y
            if(str(token) == 'v.'):
                test_index = token.i
                vs_start = 0
                vs_end = 0            
                for k in range(test_index-1, test_index-15, -1):
                    if(str(self.doc[k])[0].isupper() == False and str(self.doc[k]) not in ok_words):
                        vs_start = k+1
                        break
                    if(str(self.doc[k])[0].isupper() == True and str(self.doc[k]) in reverse_break_words):
                        vs_start = k+1
                        break
                for l in range(test_index, test_index+15):
                    if(str(self.doc[l]) == ',' or str(self.doc[l]).isnumeric() == True or str(self.doc[l]) in break_words):
                        vs_end = l
                        break
                if str(self.doc[vs_start:vs_end]) not in cases_with_dupes:
                    cases_with_dupes.append(str(self.doc[vs_start:vs_end]))

            # Append 'Matter of X' precedent cases 
            if(str(token) == 'Matter'):
                start_index = token.i
                false_flag = False
                end_index = 0
                for j in range(start_index, start_index+15):
                    # OCR misclassifies 'Matter of Z-Z-O-' as 'Matter of 2-2-0' enough times to need to hardcode this in
                    if(str(self.doc[j]).isnumeric() == True):
                        if(str(self.doc[j]) == '2' or str(self.doc[j]) == '0'):
                            continue 
                        else:
                            end_index+=1
                            break
                    if(str(self.doc[j]) in break_words or str(self.doc[j]).isnumeric() == True):
                        end_index = j
                        break
                    if(str(self.doc[j]) == ':'):
                        false_flag = True
                        break  
                if(false_flag == False):
                    temp_var = str(self.doc[start_index:end_index])
                    if temp_var not in cases_with_dupes:
                        cases_with_dupes.append(temp_var)
        cases_with_dupes = sorted(cases_with_dupes)

        # k loop removes incorrect suffixes, l loop removes incorrect prefixes & prevents duplicates from being added.
        clean_cases = []
        final_cases = []
        for k in range(0, len(cases_with_dupes)):
            if(cases_with_dupes[k][0:-1] not in clean_cases and cases_with_dupes[k][0:-1] != ''):
                clean_cases.append(cases_with_dupes[k])
        for l in range(0, len(clean_cases)):
            if(clean_cases[l][0:2] == '. ' or clean_cases[l][0:2] == ', '):
                if clean_cases[l][0:2] not in final_cases:                
                    final_cases.append(clean_cases[l][2:])
            elif(clean_cases[l][0:3] == '., '):
                if clean_cases[l][0:2] not in final_cases:                
                    final_cases.append(clean_cases[l][3:])
            elif clean_cases[l] not in final_cases:                
                final_cases.append(clean_cases[l])
        return final_cases

    def get_statutes(self) -> dict: 
        """Returns statutes mentioned in a given .txt document as a dictionary: {"""
        # Removes patterns with only words instead of numbers, and matches known statute patterns' shape using spacy to be added
        not_in_test = {'Xxx','xxx','XXX'}
        statutes_list = []
        for token in self.doc:
            word_shape_match = str(token.shape_)
            if(word_shape_match[0:3] not in not_in_test):

                # Matches shape of statutes- these can have 3-4 prefixes, 0-2 suffixes, and extracts all subsections if there isn't a space between any of them
                statute_shape_match = str(token.shape_).replace('x','d').replace('X','d')
                if(statute_shape_match[0:4] == 'ddd(' or statute_shape_match[0:4] == 'ddd.' or statute_shape_match[0:5] == 'dddd.' or statute_shape_match[0:5] == 'dddd(' or statute_shape_match[0:6] == 'ddddd.' or statute_shape_match[0:6] == 'ddddd('):                
                    # Close any open parentheses & append if not already present
                    has_open_paren = False
                    temp_token3 = str(token)
                    for i in range(0, len(temp_token3)):
                        if(temp_token3[i] == '('):
                            has_open_paren = True
                        if(temp_token3[i] == ')'):
                            has_open_paren = False
                    if(has_open_paren == True):                    
                        temp_token3 = temp_token3 + ')'
                    if temp_token3 not in statutes_list:
                        statutes_list.append(temp_token3)
        statutes_list = sorted(statutes_list)
        
        # Creates a dictionary with the key being the type of statute, and value being the listed statutes determined by the first 4 numbers in a statute.
        return_dict = {}
        CFR = []
        INA = []
        other = []
        USC = []
        for j in range(0, len(statutes_list)):
            if(statutes_list[j][0:4].isnumeric() == True):
                if(int(statutes_list[j][0:4]) >= 1000 and int(statutes_list[j][0:4]) <= 1003):
                    CFR.append(statutes_list[j])
                    continue
                elif(int(statutes_list[j][0:4]) >= 1100 and int(statutes_list[j][0:4]) <= 1999):
                    USC.append(statutes_list[j])
                    continue
                else:
                    other.append(statutes_list[j])
                    continue        
            elif(statutes_list[j][0:3].isnumeric() == True):
                if(int(statutes_list[j][0:3]) >= 100 and int(statutes_list[j][0:3]) <= 199):
                    USC.append(statutes_list[j])
                    continue
                elif(int(statutes_list[j][0:3]) >= 200 and int(statutes_list[j][0:3]) <= 399):
                    INA.append(statutes_list[j])
                    continue
                else:
                    other.append(statutes_list[j])
                    continue
            else:
                other.append(statutes_list[j])
        #TODO: Remove overlap between corresponding INA and USC statutes, recreate this table- https://www.uscis.gov/laws-and-policy/legislation/immigration-and-nationality-act
        #TODO: Make a dictionary that has the laws for a corresponding statute, map those to a certain level of granularity that can be displayed to the end user
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
        phrases = ["Respondent's", "Respondent", "respondent's", "respondent", "respondents",
                   "Applicant", "applicant", "Applicant's", "applicant's", 'filed an application']
        patterns = [nlp(text) for text in phrases]

        # Gender constants
        male_prons = ['he', "he's", 'his', 'himself']
        female_prons = ['she', "she's", 'her', 'herself']

        # Variables for analysis storage
        male_count = 0
        female_count = 0
        found = ""

        # PhraseMatcher setup, add tag (RESP) and pass in patterns
        phrase_matcher = PhraseMatcher(nlp.vocab)
        phrase_matcher.add("RESP", None, *patterns)

        # Append all sentences with target-tag to string storage variable
        for sentences in self.doc.sents:
            for match_id, start, end in phrase_matcher(nlp(sentences.text)):
                if nlp.vocab.strings[match_id] in ['RESP']:
                    found += sentences.text

        # Pass string of sentences with target phrases to tag POS
        found_nlp = nlp(found)

        # Count instances of part-of-speech tagged as pronouns in sentences
        for word_pos in found_nlp:
            if word_pos.pos_ == 'PRON':
                if word_pos.text.lower() in male_prons:
                    male_count += 1
                elif word_pos.text.lower() in female_prons:
                    female_count += 1
            if word_pos.text.lower() in male_prons:
                male_count += 1
            elif word_pos.text.lower() in female_prons:
                female_count += 1

        # Analyze highest count and return that gender or empty string for equal
        if female_count > male_count:
            return "Female"
        elif male_count > female_count:
            return "Male"
        else:
            return "Unknown"

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
