"""
Local Docker Setup:
docker build . -t <name>

Run Docker Locally:
docker run -it -p 5000:5000 <name> uvicorn app.main:app --host=0.0.0.0 --port=5000
Run Locally using Windows:
winpty docker run -it -p 5000:5000 <name> uvicorn app.main:app --host=0.0.0.0 --port=5000

"""
import os

from boto3.session import Session
from botocore.exceptions import ClientError, ConnectionError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.ocr import make_fields

import plotly.graph_objects as go
import pandas as pd
import json


app = FastAPI(
    title="DS API for HRF Asylum",
    description="PDF OCR",
    docs_url="/"
)

load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post("/pdf-ocr/{uuid}")
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


@app.post("/vis/judges/{judge_id}")
def vis_judges(judge_data: str):
    """
    Takes judge_data from BE and stores it in a dataframe.
    Creates a fig object with the bar chart info and returns it in json format.
    Features: protected grounds
    """

    jsondata = json.loads(judge_data)['data']

    df = pd.DataFrame.from_dict(jsondata)
    # keep_cols = [
    #     'case_outcome',
    #     'country_of_origin',
    #     'protected_grounds',
    #     'gender',
    # ]
    # df = df[keep_cols]

    # creating df for graphing
    outcomes_list = ['Denied', 'Granted', 'Remanded', 'Sustained', 'Terminated']

    df_protected_grounds = df.groupby('case_outcome').protected_grounds.value_counts().unstack(0)
    df_protected_grounds = df_protected_grounds.fillna(0)

    # creating new column with an outcome a judge might not have had
    for outcome in outcomes_list:
        if outcome not in df_protected_grounds.columns:
            df_protected_grounds[outcome] = 0.0

    # rearranging for same order, but might be unnessessary bc of go object
    df_protected_grounds = df_protected_grounds[outcomes_list]

    # creating the graph
    fig = go.Figure(data=[
        go.Bar(name='Denied',
               x=list(df_protected_grounds.index),
               y=df_protected_grounds['Denied']),
        go.Bar(name='Granted',
               x=list(df_protected_grounds.index),
               y=df_protected_grounds['Granted']),
        go.Bar(name='Remanded',
               x=list(df_protected_grounds.index),
               y=df_protected_grounds['Remanded']),
        go.Bar(name='Sustained',
               x=list(df_protected_grounds.index),
               y=df_protected_grounds['Sustained']),
        go.Bar(name='Terminated',
               x=list(df_protected_grounds.index),
               y=df_protected_grounds['Terminated'])
    ])

    # Change the bar mode - stack vs group
    fig.update_layout(barmode='stack')
    # fig.show()

    return fig.to_json()


@app.get("/vis/circuits/{circuit_id}")
def vis_circuits(circuit_name: str):
    pass


@app.get("/vis/correlations")
def correlations():
    """ Correlation Matrix Heat Map """
    pass
