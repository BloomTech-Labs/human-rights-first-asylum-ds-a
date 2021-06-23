import requests


arr = [
    "00c76f3f-c4e2-49b8-9adf-c1044302627d",
    "00ef179e-ad1d-474f-bd36-97b18aac452e",
    "03d8f05d-f60a-4f31-b2cc-5a3da5c3c59b",
    "0333dc84-ea98-4be8-85dc-5c8f0410af20",
    "0563a753-aefd-4026-8d22-a24169132933",
    "01881766-7409-43a9-a6bd-fa392c87cbe4",
]

for uuid in arr:
    requests.get(f"http://0.0.0.0:5001/pdf-ocr/{uuid}")
    print(f"Inserted {uuid}")
