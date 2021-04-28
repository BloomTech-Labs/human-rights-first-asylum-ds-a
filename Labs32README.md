# Human Rights First - Asylum
An application to assist immigration attorneys and refugee representatives in advocating for clients in asylum cases by identifying patterns in judicial decisions and predicting possible outcomes based on those patterns.

## Description
We participated in the building of an application for human rights first, a 501(c)3 organization. Our application uses optical character recognition to scan input court decisions for such values as the name of the presiding judge, the decision, and the asylum seeker's country of origin, and inserts these values into a database. The hope is that advocates for asylum seekers can use these data to better tailor their arguments before a particular judge and maximize their client's chances of receiving asylum. To use the application offline, follow the steps under Installation.

## Architecture
![image](assets/HRF_architecture_diagram_DavidH_rjproctor.png)

## Process
*  The stakeholder provided documents that became the foundation of our database schema.  We built database, scraped pdf documents from the internet, and filtered from them asylum cases only to populate the corpus of documents in our database.

*  Each pdf document was read using optical character recognition (OCR), converted to text to plain text and then to json which allowed us to search through each document and retrieve keywords.  These keywords will become fields in tables in our relational database.

*  We created an API connecting the database to the web development back-end with the result that user uploaded case files can be inserted into the database.

*  We created a model that, once the database has persisting data, and the model is adjusted to the specificity of that data, will predict a possible outcome of an individual judge's or panels of judges decision(s) based on his/her/their past rulings of similar cases.  This model will also render results that display easy to interpret and use (from UX perspective) visualizations on micro-patterns within the data

## Time structures
Each team worked in weekly sprints with a total time constraint of one month for the total project.  Teams met with stakeholder(s) during each sprint to present progress, ask questions, receive feedback and explore evolving stakeholder expectations.  The structure of each sprint was set:
  * Week 1 - Planning
  * Week 2 & 3 Working the Plan (coding and revising the plan according to evolving stakeholder needs and new understandings of the business problem)
  * Week 4 - Documentation and Presenting Work

Labs 29 chose to work together on all tasks and accomplished:
  * create an empty database with no schema
  * create a PDF scraper using OCR that converted PDF images to text
  * create a pathway to completion of FastAPI

Labs 30 chose to work asynchronously, yet supporting one another through pair-coding sessions and peer reviews and acomplished:
  * creating a relational database with [schema](assets/HRF_DS_DB_schema_diagram_SeanB.png)
  * completed connections between FastAPI and the back-end of the web application
  * adapting Team 1's PDF scraper to filter out only asylum cases and then convert PDF images to text and then to json
  * create a PDF scraper for search terms in all categories except social groups (time constraints)
  * explore alternative scraping methods for PDFs and keywords in search of efficiencies
  * create a pathway for data processing, model and visualization completion once there is persistent data

Labs 31 chose to work asynchronously, yet supporting one another through pair-coding sessions and peer reviews and acomplished:
  * created an API hook implementing the scraper and OCR that returns a json object of fields the scraper finds in a PDF
  * created new fields for the scraper to search for
  * started the process of deploying the API
  * refined the dockerfile for fixing dependency issues
  * started refining the scraper class

Labs 32 chose to work collaboratively in order to achieve:
  * aligned our endpoints to those of the FE & BE Web teams
  * further refined dockfile for AWS Elastic Beanstalk
  * deployed the functional scraper application to AWS EB
  * code now reads files from BE connected S3 bucket
  * started creating visualizations for FE implementation

## Next Steps
Inside our team’s Google Drive you will find two important documents. A screenshot of a Product Road Map and a description of tasks associated with the road map. Please reference that for additional user stories such as:
  * An additional field of Criminal Record, return a paragraph of crime associated if so
  * Interactive World and USA map to check statistics on who is approved or denied
  * Itterating on visuals to make them 

## Tools

 * [Pytesseract](https://github.com/madmaze/pytesseract)
 * [FastAPI](https://github.com/tiangolo/fastapi)
 * [AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/)

## Installation

 After cloning the repository, in your command line run the following commands:
 Replace <name> with a name of your choice.
 ```
docker build . -t <name>
docker run -it -p 5000:5000 <name> uvicorn app.main:app --host=0.0.0.0 --port=5000

NOTE: An error may be thrown when trying to run the app if you have not added the .env file with aws credentials
 ```
 Then open http://0.0.0.0:5000 in your browser. The application should be running. 

 ## Contributors

 [Bharath Gogineni, Labs32](https://github.com/begogineni)

 [Jace Hambrick, Labs32](https://github.com/Jace-Hambrick)

 [Nicholas Adamski, Labs32](https://github.com/boscolio)

 [Rassamy J. Soumphonphakdy, Labs32](https://github.com/rassamyjs)

 [Rebecca Duke Wiesenberg, Labs31](https://github.com/rdukewiesenb)

 [Reid Harris, Labs31](https://github.com/codealamode)

 [Lucas Petrus, Labs31](https://github.com/lucaspetrus)

 [Noah Caldwell, Labs31](https://github.com/noahnisbet)

 [Tomas Phillips, Labs30](https://github.com/tomashphill)

 [Sean Byrne, Labs30](https://github.com/ssbyrne89)

 [Henry Gultom, Labs30](https://github.com/henryspg)
 
 [RJ Proctor, Labs30](https://github.com/jproctor-rebecca)

 [Liam Cloud Hogan, Labs29](https://github.com/liam-cloud-hogan)
 
 [Steven Lee, Labs29](https://github.com/StevenBryceLee)

 [Edwina Palmer, Labs29](https://github.com/edwinapalmer)

 [Tristan Brown, Labs29](https://github.com/Tristan-Brown1096)
 
![Team2 Cross-functional Whole Team Structure](assets/HRF_cross_functional_product_dev_team_rjproctor.png)

 ## License

 This project is licensed under the terms of the MIT license.
