## Model Task Description
*  Text classification
*  Represent text in meaningful way

# Labs37 - DS
## Tools
* **get_aws.ipynb** get files from AWS S3 buckets
* **scrapper_accuracy.ipynb** use the manually_scrapped.csv and compare to the data scrapped by ocr
## Tasks not done
* Get the correct dicision date not the date of notice
* Get_Credibility function accuracy is very low. Almost always return False
* Improve the accuracy of protected grounds which is the most important field stakeholders want.
* Panel_members function sometimes cannot get the full members. Need to improve accuracy
* Country of origins sometimes miss the correct country.
* Keep improving accuracy all functions

### *** Exploratory_works are previous work from other cohorts. Some are used in the main app, some are not.
### *** Read further down to get domain knowledge on how aylum case work

# Labs30 - DS
# Asylum Decision  -- Human Rights First
An application to assist immigration advocates in winning asylum cases


## Description
We built an application for human rights first, a 501(c)3 organization. Our application uses optical character recognition to scan input court decisions for such values as the name of the presiding judge, the decision, and the asylum seeker's country of origin, and inserts these values into a database. The hope is that advocates for asylum seekers can use these data to better tailor their arguments before a particular judge and maximize their client's chances of receiving asylum. Based on our stakeholder meeting HRF wants to know the trend and exploratory of the judge's decision, for example:

 *How many percent is the case rejected with certain nationality or gender?  
 *Is there any trend based on religion or social group?  
 *Is certain judge in favor of an applicant from a certain case? or country?  

In order to answer those questions, we need to extract those keywords and put them into dataframe, and from there we store them
in our database in order for the web team to use the to be published.


Note:
DS team on Labs29 has tried to extract the keywords using spacy only with small model (en_core_web_sm). In this work (Labs30) we implemented the large model of spacy (en_core_web_lg) with expectation to get a more accurate keywords. We also tried to use "regex" to extract the desired words based on its location,  but it turned out that this solution also can not give us the accurate keywords.


## Process
* We received some foundation documents from Human Rights First to start building the database and then scraped more pdf documents of asylum cases of the internet.

* Each pdf document was read in through optical character recognition (OCR), and converted the corresponding text to plain text which will allow us to search through each document and retrieve the keywords, like the judge’s name.

Note:
After combining large model of spacy, regex, and OCR, we still found some erros in extracting words such as:
 * Attorney's name
 * Country of origin
 * The court's county
 * Name of the asylum applicant

For example: On some documents, we see the name of the judge but on other documents, that names are just empty.
The reason of inaccuracy could be because of the spacy model tself, but another reason is because the format of the document is not 100% uniform.


## Installation
Initial work of Lab30 is using Google colab and the important module to install are:

!python3 -m spacy download en_core_web_sm  
!pip3 install Pillow # Python Image Library  
!pip3 install pytesseract  # text recognition (OCR) Engine  
!pip3 install pdf2image  
!sudo apt-get install tesseract-ocr  



## Recommendation:
We need to find out different models to extract the important keywords.
Note: a small error in a legal document could cause us a big trouble in the future.

## Task Description
1.  Text classification
2.  Represent text in meaningful way

  *  labelled inputs (supervised learning)
  *  multi-classification model (unsupervised learning)
3.  Prediction and descriptive statistical analysis based on classification patterns

There are many different approaches to text mining: data mining, machine learning, information retrieval and knowledge management.  Each seeks to extract, identify and use information from large collections of textual data.  

Text classification is a learning process of text mining.  In this use case it involves preprocessing the data,  weighting terms, using the KNN algorithm in combination with  the K-means clustering algorithim.

Evaluation of this classification methodology will be assessed using precision, recall, and f-measure.

--Note: until we have a populated database, the exploratory model notebook will serve only as an option for future teams (the inherited DB from Labs29 was empty with no schema; we had to build all tables and relations to meet evolving stakeholder expectations)

[Labs 29  HRF Asylum B DS AWS RDS PostgresSQL](https://master:***@asylum.catpmmwmrkhp.us-east-1.rds.amazonaws.com/asylum)

[Labs 29 HRF Asylum A DS AWS RDS PostgresSQL](https://master:***rds_endpoint=hrfasylum-database-a.catpmmwmrkhp.us-east-1.rds.amazonaws.com)

---

## Search Terms Provided by Stakeholder
1. Country of origin
2. Judge Name (Both IJs and members of the Board) 
  *  [Source 1](https://trac.syr.edu/immigration/reports/judge2020/denialrates.html)
  *  [Source 2](https://www.justice.gov/eoir/board-of-immigration-appeals-bios) 
3. Case Outcome
4. Protected Ground
  *  Race 
  *  Religion
  *  Nationality
  *  Political Opinion
  *  Particular Social Group (Acronym PSG) 
5. If Particular Social Group (How detailed do you need these to be?) 
  *  Family
  *  Women in X Country
  *  Gender 
  *  Witnesses 
  *  Gang
  *  LGBTQ
6.  Precedential Decisions 
  *  Matter of A-B
  *  Matter of L-E-A-
7.  Policies 
  *  Safe third country
  *  Migrant protection protocols (Acronym MPP)
  *  Transit ban 
  *  Unaccompanied minor (Acronym UAC)
8.  Bars to asylum 
  *  One year deadline
  *  Serious non-political crime
  *  Particularly serious crime 
  *  Firm resettlement 
  *  Safe third country 

---
## General Domain Knowledge

Immigration Application Type (3):
1. Asylum:  These are the primary cases we want to track.  
These are IJ cases/claims with the language (DS key phrases!):
  *  ‘Fear of persecution’
  *  ‘Serious physical harm’
  *  ‘Coercive medical and psychological treatment’
  *  ‘Indivious prosecution or Disproportionate punishment for a criminal offense’
  *  ‘Economic Persecution and other forms of severe discrimination’
  *  ‘Severe criminal extortion or robbery’
2. Withholding of Removal
3. Convention Against Torture

--Majority of cases we’re tracking will file for all 3 (only tracking Asylum cases, all other cases are being filtered out prior to scraping process)

Outcomes (8 total, 3 common):
With only the current BIA documents to scrape, the majority of outcomes seem to fall into one of the following categories: 
*  Granted
*  Denied
*  Dismissed

Other Possible Outcomes:
*  Remanded 
*  Reversal 
*  Sustained 
*  Terminated
*  Returned 

--The question(s) then become(s):
1. How does this change when we look at larger amounts of data?
2. Are there other outcomes when we look at IJ cases?

Protected Grounds:
5 types: 
*  Race
*  Religion
*  Nationality
*  Political Opinion
*  Protected Social Group

--Note:  An application can list multiple Protected Grounds.

Protected Social Groups:
There are 100+ PSGs.  Examples include:
*  Domestic Violence
*  Family or Kinship Ties
*  Sexual Orientation
*  Transgendered
*  Gender
*  Ethnic Group
*  Military or Police
*  Occupation
*  Female Genital Mutilation
*  A single case may list multiple PSGs.

--These can be used as a starting point for scraping the PDFs.

Court_Type
<dl>
<dd>Immigration (IJ)</dd>
<dd>Appellate (BIA)</dd>
 

Hearing Locations:
--Examples of IJ courts: Arlington Immigration Court, Baltimore Immigration Court

--BIA court is located in Falls Church, Virginia

Other Terminology:
IJ - Immigration Judge.  Usually there’s only one Immigration Judge per case.  These judges and the cases that they rule on are the primary info we want to track.  We need more of these case PDFs.

<dl>
<dd>[Immigration Judges Names and Courts](https://trac.syr.edu/immigration/reports/judge2020/denialrates.html 
https://www.justice.gov/eoir/eoir-immigration-court-listing)</dd>

As of 2/1/2021 under “Office of Chief Immigration Judge” description (conflicting information on single site source):

<dd>[58 locations and ~330 immigration judges](https://www.justice.gov/eoir/eoir-organization-chart)</dd>
<dd>[67 locations and ~460 judges](https://www.justice.gov/eoir/office-of-the-chief-immigration-judge)</dd>

BIA - Board of Immigration Appeals  Usually there’s multiple BIA judges per appeal case. Most BIA case PDFs lack usable info on the case (esp PG and PSG), as they do not consistently have the original claim attached to the BIA resolution document:

<dd>[BIA Resource 1](https://en.wikipedia.org/wiki/Board_of_Immigration_Appeals)</dd>

<dd>[BIA Resource 2](https://www.justice.gov/eoir/board-of-immigration-appeals)</dd>

--As of 2/1/2021, there are 25 BIA judges.
--Their location is always “Virginia Falls”
</dl>

To get an idea of how Web incorporates the information we collect:


![image](human-rights-first-asylum-ds-b/assets/HRF_case_seeds_2020_0114_DavidH.png)

![image](human-rights-first-asylum-ds-b/assets/HRF_case_table_2020_0114_DavidH.png)

![Case Seed](assets/HRF_case_seeds_2020_0114_DavidH.png)

![Case Table](assets/HRF_case_table_2020_0114_DavidH.png)


---

## Exploratory Model and  Visualizations 

The purpose of the model is to classify the legal documents containing judicial decisions for immigration asylum seekers and gain insights from these documents that will aid representatives to advocate for thier client:

1.   Judicial decision
  *   Asylum Granted
  *   Asylum Relief Denied
  *   Other Relief Granted
  *   Admin Closure (expired)

2.   Insights from patterns in data of individual judges (IJ cases only - initial hearings)
3.   Insights from patterns in data of appellate (panel) judges (BIA cases only - appellate hearings)
4.   Insights from patterns in all data (IJ and BIA cases - combined initial and appellate hearings)


![image](human-rights-first-asylum-ds-b/assets/HRF_predictive_descriptive_analysis_model_methodology_RJProctor.png)

![Model Methodology](assets/HRF_predictive_descriptive_analysis_model_methodology_RJProctor.png)


---

## General Description
We built an application for human rights first, a 501(c)3 organization. Our application uses optical character recognition to scan input court decisions for such values as the name of the presiding judge, the decision, and the asylum seeker's country of origin, and inserts these values into a database. The hope is that advocates for asylum seekers can use these data to better tailor their arguments before a particular judge and maximize their client's chances of receiving asylum. Based on our stakeholder meeting HRF wants to know the trend and exploratory of the judge's decision, for example:

 *How many percent is the case rejected with certain nationality or gender?  
 *Is there any trend based on religion or social group?  
 *Is certain judge in favor of an applicant from a certain case? or country?  

In order to answer those questions, we need to extract those keywords and put them into dataframe, and from there we store them
in our database in order for the web team to use the to be published.


Note:
DS team on Labs29 has tried to extract the keywords using spacy only with small model (en_core_web_sm). In this work (Labs30) we implemented the large model of spacy (en_core_web_lg) with expectation to get a more accurate keywords. We also tried to use "regex" to extract the desired words based on its location,  but it turned out that this solution also can not give us the accurate keywords.


## General Process
* We received some foundation documents from Human Rights First to start building the database and then scraped more pdf documents of asylum cases of the internet.

* Each pdf document was read in through optical character recognition (OCR), and converted the corresponding text to plain text which will allow us to search through each document and retrieve the keywords, like the judge’s name.

Note:
After combining large model of spacy, regex, and OCR, we still found some erros in extracting words such as:
 * Attorney's name
 * Country of origin
 * The court's county
 * Name of the asylum applicant

For example: On some documents, we see the name of the judge but on other documents, that names are just empty.
The reason of inaccuracy could be because of the spacy model tself, but another reason is because the format of the document is not 100% uniform.

