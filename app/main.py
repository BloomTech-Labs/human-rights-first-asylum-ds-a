from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import app.ocr

description = """
Right now this just connects to the database on AWS. It'll do more later!
"""

app = FastAPI(
    title='HRF Aslyum B API',
    description=description,
    docs_url='/',
)

app.include_router(app.ocr.router, tags=['PDF Converter'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    uvicorn.run(app)