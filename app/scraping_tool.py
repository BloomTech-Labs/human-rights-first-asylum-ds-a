class Doc_Scraper:
    def __init__(self, text: str):
        """
        • Input will be text from a BIA case pdf file, after the pdf has
        been converted from PDF to text.
        • Scraping works utilizing spaCy, tokenizing the text, and iterating
        token by token searching for matching keywords.
        """
        self.doc = nlp(text)
        self.ents = self.doc.ents
        self.state = None
        self.city = None
        self.is_appellate = False

    def get_ents(self, labels):
        """
        • Retrieves entities of a specified label(s) in the document,
        if no label is specified, returns all entities
        """
        return (ent for ent in self.ents if ent.label_ in labels)

    def is_appellate(self):
        matcher = PhraseMatcher(nlp.vocab)
        BoIA = 'Board of Immigration Appeals'
        phrase_patterns = [nlp(text) for text in BoIA]

        matcher.add("Board of Immigration Appeals", 
                    None, 
                    *phrase_patterns)

        matches = matcher(self.doc)
        if matcher:
            self.is_appellate = True
        return self.is_appellate

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

    def get_country_of_origin(self):
        """
        • Returns the country of origin of the applicant. Currently just checks
        the document for a country that is NOT the United States.
        """
        gc = geonamescache.GeonamesCache()
        countries = gc.get_countries_by_names().keys()
        locations = map(lambda ent: ent.text, self.get_ents(['GPE']))

        similar_country = similar_in_list(countries)
        
        for loc in locations:
            origin = similar_country(loc, 0.8)
            if origin and origin != "United States":
                return origin

    def get_state(self):
        """
        IF the case is an appellate decision the first page will show 
        the legal teams' address on page 1, and the respondents address 
        on page 2. We need to decide if appellate before getting state.

        Finds the city & state the respondent originally applied in. The function
        returns the state. City can be accessed as an attribute.
        """
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
        
        for k, v in US_abbrev.items():
            if self.is_appellate == True:
                #skip page 1
                for f in self.doc:
                    if f == 'Files':
                        self.doc = self.doc[token.i - sent.start]
                for s in self.doc:
                    if s == k:
                        self.state = k
            else:
                for s in self.doc:
                    if s == k:
                        self.state = k
        return self.state

    def get_city(self, self.state):
        #uses the abbreviation from self.state
        citycache = set()
        for v in court_locs.get(self.state)['city']:
            citycache.add(v)
        
        if len(citycache) < 1: 
            return None
        
        elif len(citycache) == 1:
                return list(citycache)[0]
        else:
            #Need to finish This
            pass

    def get_gender(self):
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

    def judges(self):
        """
        • Returns a list of panel members for appellate case documents.
        """
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


        matcher = PhraseMatcher(nlp.vocab) # Create the phrase matcher
        uuid = 0 # Unique identifier for each judge's patterns

        # Add two patterns to the matcher for each judge
        for judge in panel_members:
            matcher.add(f'PATTERN_{uuid}', [nlp(judge)]) # Just the name as it is in the list
            matcher.add(f'PATTERNX_{uuid}', [nlp(judge.replace(".",""))]) # A pattern that looks for the names without periods, sometimes not picked up by the scan
            uuid += 1

        matches = matcher(self.doc) # Run the phrase matcher over the doc
        case_panel_members = set()

        if len(matches) > 0: # If a judge from our list is found in the document
            for match_id, start, end in matches:
                judge = self.doc[start:end] # A span object of the match, fetched with its `start` and `end` indecies within the doc
                case_panel_members.add(judge.text) # Extract the text from the span object, and add to the set of panel members

        return list(case_panel_members)

    def get_protected_grounds(self):
        """
        • This will return the protected ground(s) of the applicant. Special
        checks are needed. Checking for keywords is not enough, as sometimes
        documents label laws that describe each protected ground. Examples
        are 'Purely Political Offense' and 'Real Id Act'.
        
        protected_grounds = [
            'race',
            'religion',
            'nationality',
            'social',
            'political',
        ]
        """
        pgs = []


        for sent in doc.sents[:-1]:
            for token in sent:
                if token == "ORDER":
                    judges_ruling = self.doc[token.i - sent.start].text.lower()
                    break
        for token in judges_ruling:
            

            if s == 'social' and judges_ruling[token.i +1] != 'group':
                pgs.append('Social')

            elif s == 'political' and judges_ruling[token.i +1] != 'offense':
                pgs.append('Political')

            elif s == 'nationality' and judges_ruling[token.i +1] != 'act':
                pgs.append('Nationality')
            
            elif s == 'race':
                pgs.append('Race')
            
            elif s == 'religion':
                pgs.append('Religion')

            elif s == 'no' and judges_ruling[token.i +1] == 'claim':
                pgs.append = []
                break
            
            #elif s == 'real' and judges_ruling[token.i +1] == 'id':
            #    pass

            else:
                pass
            
        return '; '.join(set(pgs))

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

    def get_outcome(self) -> List[str]:
        """
        • Returns list of outcome terms from the case in a list.
          These will appear after 'ORDER' at the end of the document.
        """
        def get_following_sents(self, token):
            """
            • This function will return the two sentences surrounding the token,
            including the sentence holding the token.
            """
            start = token.sent.start
            end = token.sent.end

            try:
                sent_before_start = self.doc[start].sent.start
                sent_after_end = self.doc[end + 1].sent.end
            except (IndexError, AttributeError):
                return token.sent

            surrounding = self.doc[sent_before_start:sent_after_end + 1]

            return surrounding

        ordered_outcome = {'ORDER', 'ORDERED'}
        outcomes_list = ['denied', 'dismissed', 'granted', 'remanded', 'returned',
                         'reversal', 'sustained', 'terminated', 'terninated', 'vacated']
        for sent in doc.sents[:-1]:
            for token in sent:
                if token in ordered_outcome:
                    judges_ruling = self.doc[token.i - sent.start].text.lower()
                    break
        
        # Interesting edge case in 349320269- typo on 'terminated' present in the pdf: fuzzywuzzy matches terminated
        # to [(terninated, 90)]
        for token in judges_ruling:
            if token in outcomes_list:
                # Can be changed to append on partial match: len(fuzzy_match[0][0]) > 5 and fuzzy_match[0][1] >= 90
                return get_following_sents(self, token)

    
    