# History
This project began with the Labs 29 cohort. Here is a brief history of what each team worked on.

## Time structures
Each team worked in weekly sprints with a total time constraint of one month for the total project.  Teams met with stakeholder(s) during each sprint to present progress, ask questions, receive feedback and explore evolving stakeholder expectations.  The structure of each sprint was set:
  * Week 1 - Planning
  * Week 2 & 3 Working the Plan (coding and revising the plan according to evolving stakeholder needs and new understandings of the business problem)
  * Week 4 - Documentation and Presenting Work


## Cohort progress
Labs 29 chose to work together on all tasks and accomplished:
  * create an empty database with no schema
  * create a PDF scraper using OCR that converted PDF images to text
  * create a pathway to completion of FastAPI

Labs 30 chose to work asynchronously, yet supporting one another through pair-coding sessions and peer reviews and accomplished:
  * creating a relational database with [schema](assets/HRF_DS_DB_schema_diagram_SeanB.png)
  * completed connections between FastAPI and the back-end of the web application
  * adapting Team 1's PDF scraper to filter out only asylum cases and then convert PDF images to text and then to json
  * create a PDF scraper for search terms in all categories except social groups (time constraints)
  * explore alternative scraping methods for PDFs and keywords in search of efficiencies
  * create a pathway for data processing, model and visualization completion once there is persistent data

Labs 31 chose to work asynchronously, yet supporting one another through pair-coding sessions and peer reviews and accomplished:
  * created an API hook implementing the scraper and OCR that returns a json object of fields the scraper finds in a PDF
  * created new fields for the scraper to search for
  * started the process of deploying the API
  * refined the dockerfile for fixing dependency issues
  * started refining the scraper class

Labs 32 chose to work collaboratively to achieve:
  * aligned our endpoints to those of the FE & BE Web teams
  * further refined dockfile for AWS Elastic Beanstalk
  * deployed the functional scraper application to AWS EB
  * code now reads files from BE connected S3 bucket
  * started creating visualizations for FE implementation

Labs 33 chose to work collaboratively and accomplished:
  * updates to the `get_panel`, `get_gender`, `get_date` functions in `ocr.py`
  * creation of `court_locations.json`
  * reorganization of documentation

Labs 34 chose to work collaboratively, split into scraper and visualization teams, to:
### Visualization
  * create an API endpoint for taking in case data and responding with Plotly schema JSON so the front-end can recreate charts and get stakeholder and user feedback

### Scraper
  * create `similar` function that utilizes SpaCy Matcher class which is implemented in several functions
  * create methods `is_appellate`, `get_circuit`
  * split `get_citystate` into methods `get_city` and `get_state`
  * improved accuracy of `get_panel`, `get_outcome`, `get_gender`, `check_for_one_year`, `get_protected_grounds`, `get_country_of_origin`
  * improved readability of code to facilitate future work
  * rewrote some methods to consistently use SpaCy matcher rather than matchers used in the past
  * restructure `BIACase` class to facilitate interactions with different scraping methods 
  
Labs 38 chose to do what the team above did and split into scraper and visualization teams, to:
[VISUALIZATION_INFO](VISUALIZATION_INFO.md)
  * implemented `get_judge_vis` and it's endpoint to successfully display judge results
  * started work `on get_judge_feature_vis`, please look at VISUALIZATION_INFO
  * refactored old functions that weren't working perfectly. Please look at VISUALIZATION_INFO again

[SCRAPER_INFO](SCRAPER_INFO.md)
  * implemented a wider vocabulary
  * worked to improve the accuracy in other manners than just key words.
  * redesigned the SCRAPER_INFO file to be much more accurate and descriptive please read SCRAPER_INFO 



