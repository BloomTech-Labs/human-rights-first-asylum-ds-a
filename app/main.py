from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import grandoldfunction

description = """
Takes in a PDF, converts it to plaintext, inserts PDF and plaintext to database
"""

app = FastAPI(
    title='HRF Aslyum B API',
    description=description,
    docs_url='/',
)

app.include_router(grandoldfunction.router, tags=['Inserter'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    uvicorn.run(app)