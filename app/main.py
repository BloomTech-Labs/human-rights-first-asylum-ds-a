from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import app.ocr as ocr
exit

app = FastAPI(
    title='HRF Aslyum B API',
    docs_url='/',
)

app.include_router(ocr.router, tags=['PDF Converter'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    uvicorn.run(app)
