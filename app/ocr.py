from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import os
from fastapi import APIRouter, File

router = APIRouter()


@router.post('/convert')
async def ocr_func(file: bytes = File(...)):
    '''
    Takes an uploaded .pdf file, converts it to plain text, and saves it as a
    .txt file
    '''
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
        os.remove(filename)
        text = text.replace('-\n', '')
        f.append(text)

    with open('plaintext.txt', 'w') as plaintext:
        for item in f:
            plaintext.write("%s\n" % item)

    return plaintext
