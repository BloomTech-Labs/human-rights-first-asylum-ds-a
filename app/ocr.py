from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os


def ocr_func(pdf):
    '''
    Takes an uploaded .pdf file, converts it to plain text, and saves it as a
    .txt file
    '''
    pdf_file = pdf

    pages = convert_from_path(pdf_file, dpi=300)

    num_pages = 0

    for image_counter, page in enumerate(pages):
        filename = 'page_' + str(image_counter) + '.jpg'
        page.save(filename, 'JPEG')
        num_pages += 1

    outfile = ''.join([pdf_file.split('.')[0], '.txt'])

    f = open(outfile, 'a')

    for i in range(num_pages):
        filename = 'page_' + str(i) + '.jpg'
        text = str(((pytesseract.image_to_string(Image.open(filename)))))
        text = text.replace('-\n', '')
        f.write(text)

    f.close()

    return outfile
