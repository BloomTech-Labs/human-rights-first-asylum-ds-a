import re

class textScraper:
    '''
    Contains different scraping functions and named entities
    text is a list of strings representing the text from a document

    '''
    def __init__(self, text: list):
        self.textList = text
        self.Judge = self.getJudge(text)
    
    def getJudge(self, text: list) -> str:
        '''
        In an appeal document, finds the name of the judge on the appeal
        returns the name of the judge if it is found
        otherwise returns 'Unknown'
        '''
        patterns = [
        # Judge name is above the phrase 'immigration judge'
        re.compile(r'([a-zA-Z-.]+\s){2,3}(I\w+n|Immigration) Judge$'),
        # Judge name is on the line before title
        re.compile(r'(^U.S. )?I\w+n Judge$'),
        # Judge name is in a certification page
        re.compile(r'JUDGE ([a-zA-Z-.]+([\s, ])){2,3}$'),
        ]
        for idx, line in enumerate(text):
            # All lines should contain a first, last name and title
            if (any([pattern.search(line) for pattern in patterns]) and 
                len(line.split()) >= 4):
                return line
        return 'Unknown'