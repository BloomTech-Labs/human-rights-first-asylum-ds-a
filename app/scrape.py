from fastapi import APIRouter, BackgroundTasks, File
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
import re
import os

class textScraper:
    '''
    Contains different scraping functions and named entities
    text is a list of strings representing the text from a document

    '''
    def __init__(self, file: bytes = File(...)):
        self.textList = self.pdfOCR(file)
        self.text = ''.join(self.textList)
        self.judge = self.getJudge(self.text)
    
    def pdfOCR(self, pdfBytes: bytes = File(...), txt_folder: str = './temp/') -> list:
        '''
        Takes an uploaded .pdf file, converts it to plain text, and saves it as a
        .txt file
        '''

        pages = convert_from_bytes(pdfBytes, dpi=300)
        num_pages = 0
        
        for image_counter, page in enumerate(pages):
            filename = 'page_' + str(image_counter) + '.jpg'
            page.save(filename, 'JPEG')
            num_pages += 1
        
        fulltext = []
    
        for i in range(num_pages):
            try:
                filename = 'page_' + str(i) + '.jpg'
                fileReader = Image.open(filename)
                text = str(((pytesseract.image_to_string(fileReader))))
                os.remove(filename)
                text = text.replace('-\n', '')
                fulltext.append(text)
            except:
                return ['Error on page '+str(i)]
        return ''.join(fulltext).split('\n\n')

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
