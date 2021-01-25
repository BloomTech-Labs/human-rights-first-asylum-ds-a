# Exploratory Model and Visualizations
The purpose of the model is to classify the legal documents containing judicial decisions for immigration assylum seekers:

1. Judicial decision

--Asylum Granted
--Asylum Relief Denied
--Other Relief Granted
--Admin Closure (expired)

2. Insights from patterns in data of individual judges (IJ cases only)

3. Insights from patterns in data of appeallate (panel) judges (BIA cases only)

4. Insights from patterns in all data

---

## Task Description

* Text classification
* Represent text in meaningful way
    * labelled inputs (supervised learning)
    * multi-classification model (unsupervised learning)
* Prediction based on classification patterns

There are many different approaches to text mining: data mining, machine learning, information retrieval and knowledge management.  Each seeks to extract, identify and use information from large collections of textual data.  

Text classification is a learning process of text mining.  In this use case it involves preprocessing the data,  weighting terms, using the KNN algorithm in combination with  the K-means clustering algorithim.

Evaluation of this classification methodology will be assessed using precisin, recall, and f-measure.

Note: until we have a populated database, the exploratory model notebook will serve only as an option for future teams  (inherited DB from Labs29 is empty with no schema)

[Labs 29  HRF Asylum B DS AWS RDS PostgresSQL](https://master:***@asylum.catpmmwmrkhp.us-east-1.rds.amazonaws.com/asylum)

[Labs 29 HRF Asylum A DS AWS RDS PostgresSQL](https://master:***rds_endpoint=hrfasylum-database-a.catpmmwmrkhp.us-east-1.rds.amazonaws.com)

---
