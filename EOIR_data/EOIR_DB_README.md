### The Executive Office for Immigration Review Dataset

Each month the EOIR dataset is uploaded and made available at [https://www.justice.gov/eoir/foia-library-0](https://www.justice.gov/eoir/foia-library-0)
You can download the zip file containing the entire dataset at [https://fileshare.eoir.justice.gov/FOIA-TRAC-Report.zip](https://fileshare.eoir.justice.gov/FOIA-TRAC-Report.zip)

The schema for the EOIR dataset is in this folder. It includes all summary data for cases, proceedings, motions, judges, and attorneys. The data include the applicant's nationality, language, city and state of application and/or arrest. All judges and hearing locations are included for both the immigration and appellate courts. It can be ascertained whether the application for asylum is affirmative or defensive, i.e., whether the applicant first applied to the USCIS (U.S. Citizens and Immigration Services) or whether they sought asylum as relief during the removal process. 

The only variable Human Rights First wants that is not included is the 'Protected Grounds' of the application. That is valuable information and the main benefit of uploading and processing specific case files.

It would be challenging to integrate this dataset into the project, but it would be worthwhile. There is enough data to build robust statistical models to predict judicial rulings and thus compare the decision patterns of different judges. If this information was combined with, say, the geopolitical situation of the applicant's country at the time of application, e.g., whether human rights abuses were known to be occurring, or LGBTQ persecution, etc., it may be possible to infer potential biases without having specific information on the Protected Grounds arguments of specific cases. 

I've included a Notebook showing how to extract the data from the dataset and a few visualizations to demonstrate the relevant information is available. 

There is also a research paper from the Government Accountability Office using the EOIR dataset. They specifically mention the differences between affirmative and defensive applications, as well as other details of potential interest to Human Rights First and this project's mission: [https://www.gao.gov/assets/gao-17-72.pdf](https://www.gao.gov/assets/gao-17-72.pdf)

