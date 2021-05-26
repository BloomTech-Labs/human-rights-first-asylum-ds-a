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
        self.appellate = False

    
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

    
    