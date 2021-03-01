FROM python:3.8-slim-buster
RUN apt-get update
RUN apt-get -y install poppler-utils --fix-missing
RUN apt-get -y install tesseract-ocr
RUN python -m pip install --upgrade pip && pip install pipenv
COPY Pipfile* ./
RUN pipenv install --system --deploy
COPY ./app ./app
CMD uvicorn app.main:app --host 0.0.0.0