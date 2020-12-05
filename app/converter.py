"""depositing pdfs into the database"""

from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
from fastapi import APIRouter, File


router = APIRouter()

description = """
hacky solution, it does all the OCR stuff and if you put in a pdf
it becomes a jpg and then has to become a list before it becomes a .txt
bc i couldn't figure out how else to do it, right now it writes everything
to the repo which isn't ideal, next up is writing a function that sends it
to the right column in the right table in the database.. this also only
functions for 1 pdf at a time and it names every pdf the same thing. but it's a start!
thank u steven for writing the function in the first place, took me 8 hours
to add like 5 lines of code to it to get it to work. this is way too long, gn
"""


@router.post('/converter')
async def pdf(file: bytes = File(...)):

    pages = convert_from_bytes(file, dpi=300, fmt='jpg')

    num_images = 0
    for image_counter, page in enumerate(pages):
        filename = "page_"+str(image_counter)+".jpg"
        page.save(filename, 'JPEG')
        num_images += 1

    f = []

    for i in range(num_images):
        filename = "page_"+str(i)+".jpg"
        text = str(((pytesseract.image_to_string(Image.open(filename)))))
        text = text.replace('-\n', '')
        f.append(text)

    with open('plaintext.txt', 'w') as plaintext:
        for item in f:
            plaintext.write("%s\n" % item)

    return plaintext
