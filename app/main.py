from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from app import ocr
from app import db
#exit

app = FastAPI(
    title='HRF Aslyum B API',
    description='Asylum Case Hearing Analysis',
    docs_url='/'
)

app.include_router(db.router, tags=['DataBase'])
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
