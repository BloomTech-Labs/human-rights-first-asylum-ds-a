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
- **Details:** Returns date of case in format M-DD-YYYY. Specified as ‘date of notice’ within page 1 of an appeal
- **Returns:** String in format 'YYYY-DD-M'
- **Current Status:** Currently is pulled correctly by scraper.

### State
- **Function name: **`get_state()`
- **Details:** Returns state where case was filed
- **Returns:** String like 'AL'
- **Current Status:** Currently is pulled correctly by scraper.

### City
- **Function name: **`get_city()`
- **Details:** Returns city where case was filed
- **Returns:** String like 'Montgomery'
- **Current Status:** Currently is pulled correctly by scraper.

### Applicant's Country of Origin
- **Function name: **`get_country_of_origin()`
- **Details:** Returns country where applicant is from
- **Returns:** String like 'Tunisia'
- **Current Status:** While SpaCy's Matcher functionality was experimented with, nothing has been produced to show whether the current implementation is better or worse.

### Judge
- **Function name: **`get_panel()`
- **Details:** Returns judge presiding over the original decision- this is located at the bottom of an original decision, if one exists in the document. Judges are not mentioned in appeals cases so those cases will return 'Null'
- **Returns:** String like ‘Clarease Rankin Yates’
- **Current Status:** WIP returning the first member in the panel as the judge This should be the primary judge making the deciusion.
### Outcomes
- **Function name: **`get_outcome()`
- **Details:** Returns outcome of case
- **Returns:** A string consisting of one or more of the following:
            'reversed',
	    'remanded',
            'dismissed',
            'sustained',
            'terminated',
            'granted',
            'denied',
            'affirmed',
- **Current Status:** Currently getting 100% accuracy on training data. Contact River Bellamy with any questions.

### Protected Grounds
- **Function name: **`get_protected_grounds()`
- **Details:** In order to qualify for asylum, applicant must show they've experienced persecution based on one of the follow five categories: race, religion, nationality, membership in a particular social group or political opinion.
- **Returns:** String
- **Current Status:** Unknown. Contact Alex Krieger

### Based Violence
- **Function name: **`get_based_violence()`
- **Details:** Returns type of violence the applicant experienced if they experienced violence. Looks for words like *'abduct', 'abuse', 'assassinate', 'assault', 'coerce', 'exploit', 'fear', 'harm', 'hurt', 'kidnap', 'kill', 'murder', 'persecute', 'rape', 'scare', 'shoot', 'suffer', 'threat', 'torture'* and returns them if they exist with the document
- **Returns:** String
- **Current Status:** Unknown

### Gender
- **Function name: **`get_gender()`
- **Details:** Returns gender of applicant or unknown. Uses `PhraseMatcher` with 'LEMMA' attribute activated to match to root word. Suffers accuracy when refugee is a family or more than one.
- **Returns:** String example 'Male'
- **Current Status:** Updates were made 4/30/21 Labs 33. 
### Credibility
- **Function name: **`get_credibility()`
- **Details:** Returns the judge's decision on whether the applicant is a credible witness.
- **Returns:** Bool
- **Current Status:** Currently getting super low accuracy
### If Applicant Met Filing Deadline 
- **Function name: **`check_for_one_year()`
- **Details:** An applicant for asylum is required to file their request for asylum within one year of arriving in the US, unless there are extraordinary or changed circumstances that justify the delay. This method determines whether the issue of this filing deadline is discussed in the case.
- **Returns:** Bool
- **Current Status:** Currently getting 100% accuracy on the trainign data. Contact River Bellamy with any questions.