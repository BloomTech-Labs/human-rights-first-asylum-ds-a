import requests


file_names = [
    "00c76f3f-c4e2-49b8-9adf-c1044302627d",
    "00ef179e-ad1d-474f-bd36-97b18aac452e",
    "03d8f05d-f60a-4f31-b2cc-5a3da5c3c59b",
]

for file in file_names:
    requests.get(f"http://labs35-hrf-asylum-dev.us-east-1.elasticbeanstalk.com/pdf-ocr/{file}")
    print(f"Inserted {file}")
