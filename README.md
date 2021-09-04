# Human Rights First - Asylum
An application to assist immigration attorneys and refugee representatives in advocating for clients in asylum cases by identifying patterns in judicial decisions and predicting possible outcomes based on those patterns.

## Product Mission and Goals
[Human Rights First (HRF)](https://www.humanrightsfirst.org/about) is a non-profit, nonpartisan, 501(c)(3), international human rights organization based in New York, Washington D.C., Houston, and Los Angeles. [HRF](https://www.humanrightsfirst.org/asylum) works to link immigration attorneys and advocates with asylum seekers and provide those attorneys with resources to represent their clients. Our application leverages historical data to inform advocates better of a judge's past decisions. The hope is that advocates for asylum seekers can use our tools to tailor their arguments before a particular judge and maximize their client's chances of receiving asylum.



## Architecture
![image](https://github.com/Lambda-School-Labs/human-rights-first-asylum-be-a/blob/main/reference/architecture.png?raw=true)  
This diagram shows the current state of the architecture.

## Codebases
[Front-End](https://github.com/Lambda-School-Labs/human-rights-first-asylum-fe-a/blob/main/README.md)  
Uses NodeJS to create the web-based user interface for uploading case documents, managing users, and viewing data in the form of tables and visualizations. 

[Back-End](https://github.com/Lambda-School-Labs/human-rights-first-asylum-be-a/blob/main/README.md)  
Uses Javascript and Postgres to manage databases containing tables for users, judges, and cases.

[Data Science](https://github.com/Lambda-School-Labs/human-rights-first-asylum-ds-a/blob/main/README.md)  
Uses Python and Tesseract for optical character recognition (OCR) to convert pdf images into text data that can be searched via natural language processing (NLP) techniques. Key data, which we refer to as structured fields, are extracted from the text data and sent to the back-end for storage.

## Our Role

See this team's history [here](ProjectHistory.md).


## Files

The **app** folder contains the FastAPI application which creates an endpoint for processing a single `.pdf` file stored in the AWS S3 bucket. 

### Additional Readmes
- [SCRAPER_INFO](SCRAPER_INFO.md) contains important information about the status of each function used to extract fields from documents.
- [READMEdev](READMEdev.md) contains AWS CLI2 installation instruction
- [KnownDefects](KnownDefects.md) contains information about potential issues to be aware of.
- [NOTEBOOKS](notebooks/NOTEBOOKS.md) contains helpful information about the notebooks and scripts used to explore solutions for scrapper.
- [visualizations/README](visualizations/README.md) contains helpful information about notebooks, scripts, and data used to explore visualizations.

## Tools

 * [Pytesseract](https://github.com/madmaze/pytesseract) - package for converting pdfs to text
 * [FastAPI](https://github.com/tiangolo/fastapi) - API for endpoint that processes pdfs and data visualizations
 * [AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/) - Service for app deployment

## API Installation

After cloning the repository, in your command line run the following commands:
Replace <name> with a name of your choice.

```
docker build . -t <name>
docker run -it -p 5000:5000 <name> uvicorn app.main:app --host=0.0.0.0 --port=5000

NOTE: An error may be thrown when trying to run the app if you have not added the .env file with aws credentials
NOTE: env file should have 4 env variables namely ACCESS_KEY,SECRET_KEY, BUCKET_NAME, DB_URL
NOTE: Uncomment COPY .env .env in dockerfile before run docker locally
```

Then open http://0.0.0.0:5000 in your browser. The application should be running.   
*If `0.0.0.0` does not work, try `http://localhost:5000`*
  
## Contributors
  
###### Labs 37
[Minh Nguyen](https://github.com/minh14496)   
[Waqas Khwaja](https://github.com/WaqasKhwaja)   
[Jason Young](https://github.com/yaobviously)   
[Andrew Lee](https://github.com/andrewlee977)   
[Michael Carrier](https://github.com/mikecarrier4)   

###### Labs 35
[Dylan Sivori](https://github.com/Dylan-Sivori)  
[Frank Howd](https://github.com/Frank-Howd)  
[Malachi Ivey](https://github.com/zarekivey)    
  
###### Labs 34
[Jacob Bohlen](https://github.com/JRBOH)  
[Kevin Weatherwalks](https://github.com/KWeatherwalks)  
[River Bellamy](https://github.com/RiverBellamy)  
[Patrick Raborn](https://github.com/PatrickRaborn)  
[Ricardo Rodriguez](https://github.com/reesh19)  
[Filipe Collares](https://github.com/fcollares)  
[Nicholas Major](https://github.com/SophistryDude)  
[Evan Grinalds](https://github.com/evangrinalds)    
[Joe Sasson](https://github.com/j0sephsasson)  

###### Labs 33
[Michael Kolek](https://github.com/InqM)  
[Francis LaBounty](https://github.com/francislabountyjr)  
[Jennifer Faith](https://github.com/JenFaith)  
[Brett Doffing](https://github.com/doffing81)  
[Daniel Fernandez](https://github.com/Daniel-Fernandez-951)  
[Kevin Weatherwalks](https://github.com/KWeatherwalks)   
[Alex Krieger](https://github.com/kriegersaurusrex)  

###### Labs 32
[Bharath Gogineni](https://github.com/begogineni)  
[Jace Hambrick](https://github.com/Jace-Hambrick)  
[Nicholas Adamski](https://github.com/boscolio)  
[Rassamy J. Soumphonphakdy](https://github.com/rassamyjs)  

###### Labs 31
[Rebecca Duke Wiesenberg](https://github.com/rdukewiesenb)  
[Reid Harris](https://github.com/codealamode)  
[Lucas Petrus](https://github.com/lucaspetrus)  
[Noah Caldwell](https://github.com/noahnisbet)  

###### Labs 30
[Tomas Phillips](https://github.com/tomashphill)  
[Sean Byrne](https://github.com/ssbyrne89)  
[Henry Gultom](https://github.com/henryspg)  
[RJ Proctor](https://github.com/jproctor-rebecca)  

###### Labs 29
[Liam Cloud Hogan](https://github.com/liam-cloud-hogan)  
[Steven Lee](https://github.com/StevenBryceLee)  
[Edwina Palmer](https://github.com/edwinapalmer)  
[Tristan Brown](https://github.com/Tristan-Brown1096)  


## License
This project is licensed under the terms of the MIT license.
