"""
Local Docker Setup:
docker build . -t asylum

Run Docker Locally:
docker run -it -p 5000:5000 asylum uvicorn app.main:app --host=0.0.0.0 --port=5000

Run Locally using Windows:
winpty docker run -it -p 5000:5000 asylum uvicorn app.main:app --host=0.0.0.0 --port=5000
"""
import os

from boto3.session import Session
from botocore.exceptions import ClientError, ConnectionError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.ocr import make_fields
from app.visualizations import get_stacked_bar_chart

import pandas as pd
import json


app = FastAPI(
    title="DS API for HRF Asylum",
    description="PDF OCR",
    docs_url="/",
    version="0.35.1",
)

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get("/pdf-ocr/{uuid}")
async def pdf_ocr(uuid: str):
    """
    Small Test UUID: <b>084d0556-5748-4687-93e3-394707be6cc0</b><br>
    Large Test UUID: <b>477307493-V-J-M-AXXX-XXX-639-BIA-Aug-17-2020</b>
    """
    try:
        s3 = Session(
            aws_access_key_id=os.getenv('ACCESS_KEY'),
            aws_secret_access_key=os.getenv('SECRET_KEY'),
        ).client('s3')
        response = s3.get_object(
            Bucket=os.getenv('BUCKET_NAME'),
            Key=f"{uuid}.pdf",
        )
        fields = make_fields(response['Body'].read())
        return {
            "status": f"File received: {uuid}.pdf",
            "body": fields,
        }
    except ConnectionError:
        return {"status": "Connection refused!"}
    except ClientError:
        return {"status": f"File not found: {uuid}.pdf"}


@app.post("/vis/judges/")
async def vis_judges(request: Request):
    """
    Receives judge_data from BE and stores it in a dataframe.  
    Creates and returns stacked bar charts or historgrams based
    on User selected features for x-axis and y-axis, as well
    as hearing type (initial hearings vs appellate)
    One graph returned per post request  
    """

    columns = [
        'gender', 'credible', 'outcome', 'judge_id', 'filed_in_one_year',
        'applicant_language', 'country_of_origin', 'case_origin_state',
        'case_origin_city', 'protected_grounds', 'type_of_violence',
        'indigenous_group',
    ]
    if request.values:
        col_1, col_2, case_type, bar_type, *_ = request.values.values()
        df = get_cases_df(case_type)
        df_cross = pd.crosstab(df[col_1], df[col_2])
        col_1_name = col_1.title().replace('_', ' ')
        col_2_name = col_2.title().replace('_', ' ')
        if col_1 == col_2:
            title = f"{col_1_name} Totals"
        else:
            title = f"{col_2_name} by {col_1_name}"
        bar_lookup = {
            "Stacked": "stack",
            "Grouped": "group",
        }
        data = [
            go.Bar(name=col, x=df_cross.index, y=df_cross[col])
            for col in df_cross.columns
        ]
        layout = go.Layout(
            title=title,
            template="simple_white", # changed from plotly-dark
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=px.colors.qualitative.Antique,
            height=600,
            width=820,
            barmode=bar_lookup[bar_type],
            yaxis={"tickformat": ",", "title": col_2_name}, # changed from People
            xaxis={'title': col_1_name}
        )
        figure = go.Figure(data, layout)
        # thinking only need to return graph_json???
        return figure.to_json()

    # Receive data from backend and convert to dataframe
    # jsonstring = await Request.body()
    # jsondata = json.loads(jsonstring)['data']
    # df = pd.DataFrame.from_dict(jsondata)

    # chart_1 = get_stacked_bar_chart(df, 'protected_grounds')
    # chart_2 = get_stacked_bar_chart(df, 'gender')
    # chart_3 = get_stacked_bar_chart(df, 'country_of_origin')

    # charts_dict = {'bar_protected_grounds': chart_1,
    #                'bar_gender': chart_2,
    #                'bar_country_of_origin': chart_3}

    # return json.dumps(charts_dict)


@app.get("/vis/circuits/{circuit_id}")
def vis_circuits(circuit_id: str):
    pass


@app.get("/vis/correlations/")
def correlations():
    """ Correlation Matrix Heat Map """
    pass
