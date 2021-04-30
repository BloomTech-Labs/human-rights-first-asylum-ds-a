# HRF Asylum DS Notebooks

## Description
This folder contains `.ipynb` notebooks and `.py` scripts created by team members to help themselves gain a better understanding of the case data and try out potentially useful ideas.


## Notebooks

| Filename                                               | Created | Description                                                                                                                                                                                                                                                                                                                                                                             | Dependencies                                                                    |
|--------------------------------------------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| BIA_SCRAPER.ipynb                                      | Labs 30 |                                                                                                                                                                                                                                                                                                                                                                                         | `spacy`,`bs4`,`geonamescache`                                                   |
| NLP_to_extract_judge_court_and_country_of_origin.ipynb | Labs 29 |                                                                                                                                                                                                                                                                                                                                                                                         | `spacy`, `Pillow`,`pytesseract`,`pdf2image`,`tesseract-ocr`, `poppler-utils`    |
| OneYearLimit.ipynb                                     | Labs 31 | This notebook is a start at answering the following questions posed by the stakeholder and communicated to the team by Frank: **1)** Number of decisions where the one-year filing deadline was an issue. **2)** Number of appeals that were affirmed/denied because the applicant did not apply within one year. **3)** Any other interesting statistics the students see in the data. |                                                                                 |
| PDF2Text.ipynb                                         | Labs 30 |                                                                                                                                                                                                                                                                                                                                                                                         | `tesseract-ocr`, `poppler-utils`, `pytesseract`, `pdf2image`                    |
| base_model_and_visualizations.ipynb                    | Labs 30 |                                                                                                                                                                                                                                                                                                                                                                                         | `sqlalchemy`,`psycopg2-binary`,`pydantic`                                       |
| lab30_DS_henry_pdf_text_scraping.ipynb                 | Labs 30 |                                                                                                                                                                                                                                                                                                                                                                                         | `spacy`, `Pillow`, `pytesseract`, `pdf2image`, `tesseract-ocr`, `poppler-utils` |
| ocr_accuraccy_testing.ipynb                            | Labs 32 | This notebook is designed to find the best method of converting pdf to text                                                                                                                                                                                                                                                                                                             | `poppler-utils`,`tesseract-ocr`,`pyPDF2`,`pdf2image`,`pytesseract`              |
 



## Scripts
| Filename                      | Created | Description | Dependencies                                  |
|-------------------------------|---------|-------------|-----------------------------------------------|
| loop_all_cases.py             | Labs 33 | Function that allows looping over the .txt files of documents stored locally for testing. | `spacy`                                       |
| json_to_txt_conversion.py     | Labs 33 | Converts JSON responses downloaded from GCP into the .txt files used for analysis. Comments include directions on how to save the list of files located on a GCP bucket. | `bs4`                                         |
| cPython_wrapper.py            | Labs 33 | Can be appended to the OCR function to output a file that contains the runtime and number of indivdual function calls ran within the ocr.py file.            | `cProfile`                                    |
| GCP_pdf_to_json_conversion.py | Labs 33 | Pings the GCP storage bucket to run the Google Cloud Vision API on each pdf in the bucket, which creates a JSON response that contains confidence percentages for each letter and the full resulting text to be extracted by 'json_to_txt_conversion.py' | `google.cloud.vision`, `google.cloud.storage` |



## Contribute
Please contribute to this document so that future team members can quickly gain insight into what work has been done and which avenues have been explored already.
You can help by
- filling out the Description column for a file,
- adding a new row to the appropriate column every time you add a new notebook or script.
