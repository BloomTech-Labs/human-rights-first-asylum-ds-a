"""
Local Docker Setup:
docker build . -t asylum

Run Docker Locally:
docker run -it -p 3000:3000 asylum uvicorn app.main:app --host=0.0.0.0 --port=3000

docker run -it -p 5000:5000 asylum uvicorn app.main:app --host=0.0.0.0 --port=5000

Run Locally using Windows:
winpty docker run -it -p 5000:5000 asylum uvicorn app.main:app --host=0.0.0.0 --port=5000
"""
import os
import json 

from boto3.session import Session
from botocore.exceptions import ClientError, ConnectionError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.db_ops import insert_case
from app.ocr import make_fields
from app.visualizations import get_judge_vis, get_judge_feature_vis

app = FastAPI(
    title="DS API for HRF Asylum",
    description="PDF OCR",
    docs_url="/",
    version="0.39.3",
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
    Endpoint for uploading cases and passing scraped data to the ds_case 
    table. Also passes uuid to the case table that front-end and back-end use
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
        fields = make_fields(uuid, response['Body'].read())
        insert_case(fields)
        return {"status": "Success"}
    except ConnectionError:
        return {"status": "Connection refused!"}
    except ClientError:
        return {"status": f"File not found: {uuid}.pdf"}


@app.get("/vis/judge/{judge_id}")
async def outcome_by_judge(judge_id: int):
    """
    Endpoint for visualizations on outcome by protected grounds by judge using plotly
    """
    return json.loads(get_judge_vis(judge_id).to_json())


@app.get("/vis/judge/{judge_id}/{feature}")
async def outcome_by_judge_and_feature(judge_id: int, feature: str):
    """
    Endpoint for visualizations on outcome by protected grounds by judge using plotly
    """
    return json.loads(get_judge_feature_vis(judge_id, feature).to_json())
