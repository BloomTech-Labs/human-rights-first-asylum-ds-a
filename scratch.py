import requests


arr = [
    # "004dcaad-8c41-403f-96cc-ff4db68c45d7",
    # "00c46a50-84ee-4717-97bf-929d3a767501",
    # "00c76f3f-c4e2-49b8-9adf-c1044302627d",
    # "00ef179e-ad1d-474f-bd36-97b18aac452e",
    # "01108e14-b94a-4f59-9a76-9f8cb2f002c2",
    # "012604c9-fdf5-4452-8cb2-de7a594354fa",
    # "013a6a6a-40d1-4c29-97c4-5aa865ca5a42",
    "01881766-7409-43a9-a6bd-fa392c87cbe4",
]

for uuid in arr:
    requests.get(f"http://0.0.0.0:5001/pdf-ocr/{uuid}")
    print(f"Inserted {uuid}")
