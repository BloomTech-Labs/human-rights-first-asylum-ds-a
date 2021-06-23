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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.db_ops import insert_case
from app.ocr import make_fields


app = FastAPI(
    title="DS API for HRF Asylum",
    description="PDF OCR",
    docs_url="/",
    version="0.35.4",
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
    004dcaad-8c41-403f-96cc-ff4db68c45d7<br>
    00c46a50-84ee-4717-97bf-929d3a767501<br>
    00c76f3f-c4e2-49b8-9adf-c1044302627d<br>
    00ef179e-ad1d-474f-bd36-97b18aac452e<br>
    01108e14-b94a-4f59-9a76-9f8cb2f002c2<br>
    012604c9-fdf5-4452-8cb2-de7a594354fa<br>
    013a6a6a-40d1-4c29-97c4-5aa865ca5a42<br>
    01881766-7409-43a9-a6bd-fa392c87cbe4<br>
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
        insert_case(fields)
        return {"status": "Success"}
    except ConnectionError:
        return {"status": "Connection refused!"}
    except ClientError:
        return {"status": f"File not found: {uuid}.pdf"}
