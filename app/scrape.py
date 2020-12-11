import re
import spacy


class textScraper:
    '''
    Contains different scraping functions and named entities
    text is a list of strings representing the text from a document

    '''
    def __init__(self, text: list):
        self.textList = text
        self.Judge = self.getJudge(text)
    
    def getJudge(self, text: list) -> tuple:
        '''
        In an appeal document, finds the name of the judge on the appeal
        returns a tuple of 'high confidence' or 'low confidence' 
        and the name of the judge
        If the word 'judge' is near the token, high confidence is returned
        This is because the judge name is followed or preceded by their title
        '''
        nlp = spacy.load('en_core_web_sm')


        spaceSepText = ' '.join(text)
        doc = nlp(spaceSepText)
        people = [ent for ent in doc.ents if ent.label_ == 'PERSON'
                        and len(ent.text.split(' ')) in (2,3)][-5:]
        # print(people)
        possibleJudges = [doc[person.start-4:person.end+4] for person in people]
        # print(possibleJudges)
        for idx, tokens in enumerate(possibleJudges):
            if 'judge' in str(tokens).lower():
            return ('High confidence', people[idx])
        return ('low confidence', max(sorted(people, key = len)))