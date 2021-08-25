import json
import geonamescache
import pytesseract
import pickle
from pdf2image import convert_from_bytes
from spacy import load
from spacy.tokens import Doc, Span
from spacy.matcher import Matcher, PhraseMatcher
from typing import List, Iterator


nlp = load("en_core_web_sm")


def make_fields(uuid, file) -> dict:
    """ This is the main overall function that creates a dictionary of the
    desired fields and their respective values; info that goes into those fields.
    """
    pages = convert_from_bytes(file, dpi=90)
    text = map(pytesseract.image_to_string, pages)
    string = " ".join(text)
    case_data = BIACase(uuid, string).to_dict()
    return case_data


def similar(doc, matcher_pattern):
    """
    A function that uses a spacy Matcher object to search for words or
    consecutive words as a phrase.

    Format: pattern = [{"LOWER": <word>}, {"LOWER": <the next word>}, ...etc]
    Can look for multiple patterns simultaneously using list of patterns;
        [[{"ARG": word}], [{"ARG": word}], [{"ARG": word}]]

    DOC: https://spacy.io/usage/rule-based-matching
    """
    # create matcher object
    matcher = Matcher(nlp.vocab)

    # Add the pattern that will be searched for
    matcher.add('matcher_pattern', matcher_pattern)

    # return the "matcher" objects; as Span objects(human readable text)
    return matcher(doc, as_spans=True)


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
    if (i == len(str1) - 1 and len(str1) == len(str2)
            and (str1[-1] == 'd' or str2[-1] == 'd')):
        return False

    # We're looking at a substitution other than 'd' at the end
    if str1[i + 1:] == str2[i + 1:]:
        return True

    # We're in the middle, str1 has an extra character
    if str1[i + 1:] == str2[i:]:
        return True

    # We're in the middle, str2 has an extra character
    if str1[i:] == str2[i + 1:]:
        return True

    return False


def in_parenthetical(match):
    """
    Checks for text wrapped in parenthesis, and removes any
    returned protected grounds if they we're wrapped in parenthesis
    used in protected grounds in order to improve accuracy
    """
    open_parens = 0
    # search the rest of the sentence
    for i in range(match.end, match.sent.end):
        if match.doc[i].text == '(':
            open_parens += 1
        elif match.doc[i].text == ')':
            if open_parens > 0:
                open_parens -= 1
            else:
                return True
    return False


class BIACase:
    """
    The following defines the BIACase Class. When receiving a court doc,
    we use this to extract info for the desired fields/info
    that are scraped from the text of the court docs.
    """
    with open('./app/court_locations.json') as f:
        court_locs = json.load(f)

    with open('./app/judge_names.pkl', 'rb') as j:
        appellate_panel_members = pickle.load(j)

    def __init__(self, uuid: str, text: str):
        """
        • Input will be text from a BIA case pdf file, after the pdf has
        been converted from PDF to text.
        • Scraping works utilizing spaCy, tokenizing the text, and iterating
        token by token searching for matching keywords.
        """
        self.doc: Doc = nlp(text)
        self.uuid = uuid

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'panel_members': ', '.join(self.get_panel()) or 'Unknown',
            'decision_type': self.get_decision_type() or 'Unknown',
            'application_type': self.get_application() or "Unknown",
            'date': self.get_date() or 'Unknown',
            'country_of_origin': self.get_country_of_origin() or 'Unknown',
            'outcome': self.get_outcome() or 'Unknown',
            'case_origin_state': self.get_state() or 'Unknown',
            'case_origin_city': self.get_city() or "Unknown",
            'protected_grounds': ', '.join(self.get_protected_grounds()) or 'Unknown',
            'type_of_violence': ', '.join(self.get_based_violence()) or 'Unknown',
            'gender': self.get_gender() or 'Unknown',
            'credibility': self.get_credibility() or 'Unknown',
            'check_for_one_year': str(self.check_for_one_year()) or 'Unknown',
        }

    def get_ents(self, labels: List[str]) -> Iterator[Span]:
        """
        • Retrieves entities of a specified label(s) in the document,
        if no label is specified, returns all entities
        """
        return (ent for ent in self.doc.ents if ent.label_ in labels)

    def get_country_of_origin(self):
        """
        RETURNS the respondent's or respondents' country of origin:
        """
        # sorted list of all current countries
        gc = geonamescache.GeonamesCache()
        countries = sorted(gc.get_countries_by_names().keys())
        # remove U.S. and its territories from countries
        countries = set(countries)
        non_matches = {"American Samoa", "Guam", "Northern Mariana Islands", "Puerto Rico", 
                       "United States", "United States Minor Outlying Islands", "U.S. Virgin Islands"}
        countries = countries.difference(non_matches)

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
        spans = similar(self.doc, primary_pattern)
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

        # SECONDARY search:
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
        • Returns decision date of the document.

        This is the code to return hearing date 
        # get_ents function only use in this function
        # can be deleted from BIA class if not use 

        dates = map(str, self.get_ents(['DATE']))
        for s in dates:
            if len(s.split()) == 3:
                return s
        """
        primary_pattern = [
            [{"LOWER": "date"}, {"LOWER": "of"}, 
            {"LOWER": "this"}, {"LOWER": "notice"}]
        ]
        # instantiate a list of pattern matches
        spans = similar(self.doc, primary_pattern)
        # if there are matches
        if spans:
            # grab the surrounding sentence and turn it into a string
            sentence = str(spans[0].sent)
            # remove line breaks, edge case
            clean_sent = sentence.replace("\n", " ")
            # iterate through the list of tokens in sentence
            # pick out the date in format xxxx/xx/xx
            for i in clean_sent.split():
                temp = i.split('/')
                if len(temp) == 3:
                    if temp[0] != 2:
                        temp[0] = '0' + temp[0]
                    result_date = temp[2] + '-' + temp[0] + '-' + temp[1]
                    return result_date

    def get_panel(self):
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
        matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        patterns = [nlp.make_doc(text) for text in self.appellate_panel_members]
        matcher.add("panel_names", patterns)
        matches = set()
        for match_id, start, end in matcher(self.doc):
            span = self.doc[start:end]
            matches.add(' '.join(span.text.split(", ")[-1::-1]))
        return sorted(list(matches))

    def get_gender(self):
        """
        Searches through a given document and counts the TOTAL number of
        "male" pronoun uses and "female" pronoun uses. Whichever
        count("M" or "F") is higher, that gender is returned.
        In the event of a tie; currently returns "Unknown"; may be able to
        code this edge case. Current accuracy is >95%, low priority fix.
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
            f_patterns.append([{'LOWER': prons}])
        for prons in male_prons:
            m_patterns.append([{'LOWER': prons}])

        # use similar() function (Above) to find patterns(pronouns)
        m_similar = similar(self.doc, m_patterns)
        f_similar = similar(self.doc, f_patterns)

        # check the number of gendered pronoun occurrences and return gender
        if len(m_similar) > len(f_similar):
            return 'Male'
        elif len(f_similar) > len(m_similar):
            return 'Female'
        else:
            return 'Unknown'

    def get_protected_grounds(self):
        """
        This will return the protected ground(s) of the applicant. Special
        checks are needed. Checking for keywords is not enough, as sometimes
        documents label laws that describe each protected ground. Examples
        are 'Purely Political Offense' and 'Real Id Act'.
        """
        pattern = [
            [{"LOWER": "race"}],
            [{"LOWER": "religion"}],  # expand to check for list of religions
            [{"LOWER": "nationality"}],  # phrase is pulled but out of context
            [{"LOWER": "social"}, {"LOWER": "group"}],
            [{"LOWER": "political"}, {"LOWER": "opinion"}],
            [{"LOWER": "political"}, {"LOWER": "offense"}],
            [{"LOWER": "political"}],
        ]

        religions = ['christianity', 'christian', 'islam', 'atheist',
                     'hinduism', 'buddihism', 'jewish', 'judaism', 'islamist',
                     'sunni', 'shia', 'muslim', 'buddhist', 'atheists', 'jew',
                     'hindu', 'atheism']

        politicals = ['political opinion', 'political offense']

        confirmed_matches = []
        # create pattern for specified religions
        for religion in religions:
            pattern.append([{"LOWER": religion}])

        potential_grounds = similar(self.doc, pattern)

        for match in potential_grounds:
            # skip matches that appear in parenthesis, the opinion is probably
            # just quoting a list of all the protected grounds in the statute
            if in_parenthetical(match):
                continue
            # remove 'nationality act' from potential_grounds
            if match.text.lower() == 'nationality' \
                    and 'act' not in match.sent.text.lower() \
                    and 'nationality' not in confirmed_matches:
                confirmed_matches.append('nationality')

            # check for specified religion, replace with 'religion'
            elif match.text.lower() in religions:
                if 'religion' not in confirmed_matches:
                    confirmed_matches.append('religion')

            elif match.text.lower() in politicals:
                if 'political' not in confirmed_matches:
                    confirmed_matches.append('political')

            else:
                if match.text.lower() not in confirmed_matches:
                    confirmed_matches.append(match.text.lower())
        return confirmed_matches

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
            'Withholding of Removal': ['Withholding of Removal',
                                       'withholding of removal'],
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

    def get_decision_type(self):
        return "Appellate" if len(self.get_panel()) > 1 else "Initial"
        # It seems decision_type is looking for appellate decision or else
        # intial decision, not immigration court decision.

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
            if token.text in {"ORDER", 'ORDERED'}:
                start, stop = token.sent.start, token.sent.end + 280
                outcome = self.doc[start:stop].text.strip().replace("\n", " ")
                outcome = outcome.split('.')[0].lower()
                for result in outcomes:
                    if result in outcome:
                        return result.title()

    def get_state(self):
        """
        get_state: Get the state of the original hearing location
        Find the "File:" pattern in the document and after that
        pattern is the State 

        Returns: The name of the state
        """
        """
        Previous code to find state defeciency
        for place in self.doc:
            place = place.text
            if place in StateLookup.states.keys():
                return place
            elif place in StateLookup.states.values():
                return StateLookup.abbrev_lookup(place)
        return "Unknown"
        """
        primary_pattern = [
            [{"LOWER": "file"}, {"LOWER": ":"}],
            [{"LOWER": "files"}, {"LOWER": ":"}]
        ]
        # instantiate a list of pattern matches
        spans = similar(self.doc, primary_pattern)
        # if there are matches
        if spans:
            # grab the surrounding sentence and turn it into a string
            sentence = str(spans[0].sent)
            # remove line breaks, edge case
            clean_sent = sentence.replace("\n", " ")
            state = clean_sent.split(',')[1].split()[0].strip()
            return state
        return "Unknown"

    def get_city(self):
        """
        get_city: Get the state of the original hearing location
        Find the "File:" pattern in the document and after that
        pattern is the City 

        Returns: The name of the city
        """
        primary_pattern = [
            [{"LOWER": "file"}, {"LOWER": ":"}],
            [{"LOWER": "files"}, {"LOWER": ":"}]
        ]
        # instantiate a list of pattern matches
        spans = similar(self.doc, primary_pattern)
        # if there are matches
        if spans:
            # grab the surrounding sentence and turn it into a string
            sentence = str(spans[0].sent)
            # remove line breaks, edge case
            clean_sent = sentence.replace("\n", " ")
            city = clean_sent.split(',')[0].split()[-1].strip()
            return city
        return "Unknown"

    def get_based_violence(self) -> List[str]:
        """
        Returns a list of keyword buckets which indicate certain types of
        violence mentioned in a case, current buckets are: Violence, Family,
        Gender, and Gangs. These keywords can be changed in their respective
        lists, and an item being present in the list means that the given type
        of violence is mentioned in the document.
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
        violent_list = ['abduct', 'abuse', 'assassinate', 'assault', 'coerce',
                        'exploit', 'fear', 'harm', 'hurt', 'kidnap', 'kill',
                        'murder', 'persecute', 'rape', 'scare', 'shoot',
                        'suffer', 'threat', 'torture']
        family_list = ['child', 'daughter', 'family', 'husband', 'parent',
                       'partner', 'son', 'wife', 'woman']
        gender_list = ['fgm', 'gay', 'gender', 'homosexual', 'homosexuality',
                       'lesbian', 'lgbt', 'lgbtq', 'lgbtqia',
                       'queer', 'sexuality', 'transgender']
        gang_list = ['cartel', 'gang', 'militia']

        # Outputs a list of PhraseMatch occurrences for a given list of keywords
        violence_match = get_matches(violent_list, 'Violent', self.doc)
        family_match = get_matches(family_list, 'Family', self.doc)
        gender_match = get_matches(gender_list, 'Gender', self.doc)
        gang_match = get_matches(gang_list, 'Gang', self.doc)

        # Printing full_text[judge_match2[0][1]:judge_match2[0][2]] gives word
        # it matches on, can put in the [0] a for loop to see all matches
        if len(violence_match) != 0:
            terms_list.append('Violent')
        if len(family_match) != 0:
            terms_list.append('Family')
        if len(gender_match) != 0:
            terms_list.append('Gender')
        if len(gang_match) != 0:
            terms_list.append('Gang')
        return terms_list

    def get_credibility(self) -> str:
        """
        Returns the judge's decision on whether the applicant is a credible witness.
        The process starts by adding rules/phrases to SpaCy's Matcher, they were obtained by manually 
        parsing through case files and finding all sentences related to credibility. 
        There are three separate rules, narrow, medium and wide, which decrease in the phrasing
        specificity, this allows for some wiggle room as opposed to searching for exact matches. 
        All instances of a match are returned by Matcher, so checking whether these objects are empty 
        or not dictates the output of this function.
        """
        # Speciifying phrase patterns / rules to use in SpaCy's Matcher
        # narrow_scope = [[{"LOWER": "court"}, {"LOWER": "finds"},
        #                  {"LOWER": "respondent"}, {"LOWER": "generally"},
        #                  {"LOWER": "credible"}],
        #                 [{"LOWER": "court"}, {"LOWER": "finds"},
        #                  {"LOWER": "respondent"}, {"LOWER": "testimony"},
        #                  {"LOWER": "credible"}],
        #                 [{"LOWER": "court"}, {"LOWER": "finds"}, 
        #                  {"LOWER": "respondent"}, {"LOWER": "credible"}]]

        # medium_scope = [[{"LOWER": "credible"}, {"LOWER": "witness"}],
        #                 [{"LOWER": "generally"}, {"LOWER": "consistent"}],
        #                 [{"LOWER": "internally"}, {"LOWER": "consistent"}],
        #                 [{"LOWER": "sufficiently"}, {"LOWER": "consistent"}],
        #                 [{"LOWER": "testified"}, {"LOWER": "credibly"}],
        #                 [{"LOWER": "testimony"}, {"LOWER": "credible"}],
        #                 [{"LOWER": "testimony"}, {"LOWER": "consistent"}]]

        # wide_scope = [{"LEMMA": {"IN": ["coherent", 
        #                                 "possible", 
        #                                 "credible", 
        #                                 "consistent"]}}]
        
        # # instantiating Matcher
        # matcher = Matcher(nlp.vocab)
        
        # # adding each rule to Matcher, then using global function similar() to find 
        # # and store matches in similar_****** variables
        # matcher.add('narrow_cred', narrow_scope)
        # similar_narrow = similar(target_phrases=narrow_scope, file=self.doc)

        # matcher.add('medium_cred', medium_scope)
        # similar_medium = similar(target_phrases=medium_scope, file=self.doc)

        # matcher.add('wide_cred', wide_scope)
        # similar_wide = similar(target_phrases=wide_scope, file=self.doc)
        
        # # output logic checks wheteher similar_***** variables are empty or not
        # if similar_narrow:
        #     return True

        # elif similar_medium and similar_wide:
        #     return True

        # else:
        #     return False
        return "Unkown"
        
    def check_for_one_year(self) -> bool:
        """
        Checks whether or not the asylum-seeker argued to be exempt from the
        one-year guideline.

        Returns true if the phrases "within one-year", "untimely application",
        "extraordinary circumstances" or "changed circumstances" appeaer in the
        same sentence as a time-based word. Otherwise returns False.
        """
        time_terms = {'year', 'delay', 'time', 'period', 'deadline'}
        # The 'OP':'?' notation means this token is optional, it will match
        # sequences with the token and without the token.
        circumstance_pattern = [
            [{'LEMMA': {'IN': ['change', 'extraordinary']}},
             {'LOWER': {'IN': ['"', '”']}, 'OP': '?'},
             {'LEMMA': 'circumstance'}]
        ]
        application_pattern = [
            [{'LOWER': 'untimely'}, {'LOWER': 'application'}]
        ]
        year_pattern = [
            [{'LOWER': 'within'}, {'LOWER': {'IN': ['1', 'one']}},
             {'LOWER': '-', 'OP': '?'}, {'LOWER': 'year'}]
        ]
        matcher = Matcher(nlp.vocab)
        matcher.add('year pattern', year_pattern)
        matcher.add('circumstance pattern', circumstance_pattern)
        matcher.add('application pattern', application_pattern)
        matches = matcher(self.doc, as_spans=True)

        for match in matches:
            for token in match.sent:
                if token.lemma_ in time_terms:
                    return True
        return False
