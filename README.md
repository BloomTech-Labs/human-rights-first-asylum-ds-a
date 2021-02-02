# Labs DS template
# Asylum Decision  -- Human Rights First
An application to assist immigration advocates in winning asylum cases


## Description
We built an application for human rights first, a 501(c)3 organization. Our application uses optical character recognition to scan input court decisions for such values as the name of the presiding judge, the decision, and the asylum seeker's country of origin, and inserts these values into a database. The hope is that advocates for asylum seekers can use these data to better tailor their arguments before a particular judge and maximize their client's chances of receiving asylum. Based on our stakeholder meeting HRF wants to know the trend and exploratory of the judge's decision, for example:

 *How many procent is the case rejected with certain nationality or gender?
 *Is there any trend based on religion or social group?
 *Is certain judge in favor of an applicant from a certain case? or country?

In order to answer those questions, we need to extract those keywords and put them into dataframe, and from there we store them
in our database in order for the web team to use the to be published.


Lab30-note:
Lab29 has tried to extract the keywords using spacy only with small model (en_core_web_sm). In this work we implemented the large model of spacy (en_core_web_lg) with expectation to get a more accurate keywords. We also tried to use "regex" to extract the desired words based on its location,  but it turned out that this solution also can not give us the accurate keywords.


## Process
* We received some foundation documents from Human Rights First to start building the database and then scraped more pdf documents of asylum cases of the internet.

* Each pdf document was read in through optical character recognition (OCR), and converted the corresponding text to plain text which will allow us to search through each document and retrieve the keywords, like the judge’s name.

Lab30-note:
After combining large model of spacy, regex, and OCR, we still found some erros in extracting words such as:
 * judge's name
 * Country of origin
 * The court's county
 * name of the asylum applicant

For example: On some documents, we see the name of the judge, but on other documents, the names are just empty.
The reason of inaccuracy could be because of the spacy model tself, but another reason is because the format of the document is not 100% uniform.


## Installation
Initial work of Lab30 is using Google colab and the important module to install are:

!python3 -m spacy download en_core_web_lg
!pip3 install Pillow # Python Image Library

!pip3 install pytesseract  # text recognition (OCR) Engine, 
!pip3 install pdf2image
!sudo apt-get install tesseract-ocr



## Recommendation:
We need to find out a different model to extract the important keywords.
Note: a small error in a legal document could cause us a big trouble in the future.

