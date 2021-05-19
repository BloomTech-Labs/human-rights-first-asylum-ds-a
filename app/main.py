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


@app.get("/vis/correlations")
def correlations():
    """ Correlation Matrix Heat Map """
    pass


@app.post("/vis/judges/{judge_id}")
def vis_judges(judge_name: str):
    pass


@app.get("/vis/circuits/{circuit_id}")
def vis_circuits(circuit_name: str):
    pass
