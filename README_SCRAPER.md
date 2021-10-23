# Fields Being Pulled By Scraper

### Application Details
- **Function name: ** `get_application()`
- **Details:** This function returns legal reasons listed in document as to why the applicant  should not be deported.
- **Returns:** This function returns one to four strings:
	1. Asylum
	2. Withholding of Removal - *The U.S. government legally cannot remove someone to a country where their freedom would be threatened. In other words, if someone's political opinion, race, nationality, or politial opinion puts them at risk, they qualify for asylum.***
	3. Protection under the United Nations Convention Against Torture (CAT): *The U.S. Government cannot deport someone who is at risk of being tortured if sent back.*
	4. Other
- **Current Status:** Currently is pulled correctly by scraper.

### Decision Date
- **Function name: ** `get_date()`
- **Returns:** String in format 'YYYY-DD-M'
- **Current Status:** Currently is pulled correctly by scraper.

### State
- **Function name: **`get_state()`
- **Details:** Searches for the phrase "Immigration Court" which usually appears at the top of the case, then grabs the sentence that contains the searched phrase + 12 tokens after the end the sentence. The span is then cleaned, split on ','. The State is the second element (after another split by " ") in either the second or third element of the list (depending on how many commas are grabbed by the spaCy matcher). Returns state where case was filed.
- **Returns:** String like 'AL' or 'ALABAMA'
- **Current Status:** Currently is pulled correctly by scraper.
- **Known Bug:** This method as written will likely return the incorrect state if there are more than 2 commas in the state_clean_sent variable.

### City
- **Function name: **`get_city()`
- **Details:** Searches for the phrase "Immigration Court" which usually appears at the top of the case, then grabs the sentence that contains the searched phrase + 12 tokens after the end the sentence. The span is then cleaned, split on ','. The State is the second element (after another split by " ") in either the first or second element of the list (depending on how many commas are grabbed by the spaCy matcher). Returns city where case was filed
- **Returns:** String like 'Montgomery'
- **Current Status:** Currently is pulled correctly by scraper.
- **Known Bug:** This method as written will likely return the incorrect city if there are more than 2 commas in the city_clean_sent variable.

### Applicant's Country of Origin
- **Function name: **`get_country_of_origin()`
- **Details:** Returns country where applicant is from
- **Returns:** String like 'Tunisia'
- **Current Status:** While SpaCy's Matcher functionality was experimented with, nothing has been produced to show whether the current implementation is better or worse.

### Judge
- **Function name: **`get_panel()`
- **Details:** Returns Unknown due to switch from appellate BIA cases to immigration court cases
- **Note:** In immigration court cases, name of the judge is usually at the bottom below a handwritten signature; often the signature crosses the name, which makes it nearly impossible to OCR correctly
- **Returns:** Unknown
- **Current Status:** Returns Unknown
  
### Outcomes
- **Function name: **`get_outcome()`
- **Details:** Returns outcome of case (usually located at the bottom of the case after "ORDER" or "ORDERS")
- **Returns:** A string consisting of one or more of the following:
            'dismissed',
            'terminated',
            'granted',
            'denied'
- **Current Status:** Currently is pulled correctly by scraper.

### Protected Grounds
- **Function name: **`get_protected_grounds()`
- **Details:** This will return the protected ground(s) of the applicant. 
- **Known Bug:** The method as written returns all 5 protected grounds for each case because there is a sentence in nearly every document which lists all 5 protected grounds when it explains the bases upon which asylum can be granted (e.g. "To satisfy the “refugee” definition, an applicant must demonstrate that she is unable or unwilling to return to her country of origin because of a “well-founded fear” of future persecution on account of one of the five statutory grounds: race, religion, nationality, membership in a particular social group, or political opinion.") The function multi_prot_grounds_fix was written to solve this bug but it does not work.
- **Current solution:** Method is commented out and returns "Unknown". Frontend will implement a drop-down menu for user to manually enter the protected ground.
- **Returns:** Unknown
- **Current Status:** Method is commented out and returns "Unknown". Frontend will implement a drop-down menu for user to manually enter the protected ground.

### Based Violence
- **Function name: **`get_based_violence()`
- **Details:** Returns type of violence the applicant experienced if they experienced violence. Looks for words like *'abduct', 'abuse', 'assassinate', 'assault', 'coerce', 'exploit', 'fear', 'harm', 'hurt', 'kidnap', 'kill', 'murder', 'persecute', 'rape', 'scare', 'shoot', 'suffer', 'threat', 'torture'* and returns them if they exist with the document
- **Returns:** String
- **Current Status:** Currently is pulled correctly by scraper.

### Gender
- **Function name: **`get_gender()`
- **Details:** Returns gender of applicant or unknown. Uses `PhraseMatcher` with 'LEMMA' attribute activated to match to root word. Suffers accuracy when refugee is a family or more than one.
- **Returns:** String example 'Male'
- **Current Status:** Currently is pulled correctly by scraper.

### Credibility
- **Function name: **`get_credibility()`
- **Details:** Returns the judge's decision on whether the applicant is a credible witness.
- **Returns:** Bool
- **Current Status:** Currently getting super low accuracy

### If Applicant Met Filing Deadline 
- **Function name: **`check_for_one_year()`
- **Details:** An applicant for asylum is required to file their request for asylum within one year of arriving in the US, unless there are extraordinary or changed circumstances that justify the delay. This method determines whether the issue of this filing deadline is discussed in the case.
- **Returns:** Bool
- **Current Status:** Currently getting 100% accuracy on the training data. Contact River Bellamy with any questions.