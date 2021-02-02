# Human Rights First - Asylum
An application to assist immigration attorneys and refugee representatives in advocating for cilents in asylum cases by identifying patterns in judicial decisions and predicting possible outcomes based on those patterns

## Description
We participated in the building of an application for human rights first, a 501(c)3 organization. Our application uses optical character recognition to scan input court decisions for such values as the name of the presiding judge, the decision, and the asylum seeker's country of origin, and inserts these values into a database. The hope is that advocates for asylum seekers can use these data to better tailor their arguments before a particular judge and maximize their client's chances of receiving asylum. To use the application offline, follow the steps under Installation.

## Architecture
![image](assets/HRF_architecture_diagram_DavidH_rjproctor.png)

## Process
*  The stakeholder provided documents that became the foundation of our database schema.  We built database, scraped pdf documents from the internet, and filtered from them asylum cases only to populate the corpus of documents in our database.

*  Each pdf document was read using optical character recognition (OCR), converted to text to plain text and then to json which allowed us to search through each document and retrieve keywords.  These keywords will become fields in tables in our relational database.

*  We created an API connecting the database to the web development back-end with the result that user uploaded case files can be inserted into the database.

*  We created a model that, once the database has persiting data and the model is adjusted to the specificity of that data, will predict a posible outcome of an individual judge's or panels of judges decision(s) based on his/her/their past rulings of similar cases.  This model will also render results that display easy to interpret and use (from UX perspective) visualizations on micro-patterns within the data

## Tools

 * [Pytesseract](https://github.com/madmaze/pytesseract)
 * [FastAPI](https://github.com/tiangolo/fastapi)
 * [AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/)

## Installation

 After cloning the repository, in your command line run the following commands:
 ```
 pipenv shell
 cd app
 python main.py
 ```
 Then open localhost:8000 in your browser. The application should be running. 

 ## Contributors

 [Tristan Brown](https://github.com/Tristan-Brown1096)

 [Sean Byrne](https://github.com/ssbyrne89)

 [Henry Gultom](https://github.com/henrygp)
 
 [Liam Cloud Hogan](https://github.com/liam-cloud-hogan)
 
 [Steven Lee](https://github.com/StevenBryceLee)

 [Edwina Palmer](https://github.com/edwinapalmer)

 [Tomas Phillips](https://github.com/tomashphill)

 [RJ Proctor](https://github.com/jproctor-rebecca)

![Team2_cross_functional_team](assets/HRF_cross_functional_product_dev_team_rjproctor.png)

 ## License

 This project is licensed under the terms of the MIT license.