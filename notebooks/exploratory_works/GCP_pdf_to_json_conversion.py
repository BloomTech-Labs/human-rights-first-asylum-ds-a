"""Performs OCR on PDF/TIFF where the source files are located within a GCS bucket- runtime is a little under 1 minute per file"""
# Requires GCP suite to be installed and have a ServiceAccount.json file containing your GCP account details
# Watch this video & read the docs to get these keys set up for your Google account: https://www.youtube.com/watch?v=wfyDiLMGqDM
# https://cloud.google.com/iam/docs/creating-managing-service-account-keys
import json
import re
from google.cloud import vision
from google.cloud import storage

# Make json & pdf lists from bloblist of all files in GCP bucket
json_list = []
pdf_list = []

# Upload all the PDFs to a GCP bucket, create blob_list.txt to get the GCP location on each line and save to expected json response
# On Windows: 'gsutil ls gs://$BUCKET_NAME/*.pdf > blob_list.txt' to save file list
file1 = open('blob_list.txt', 'r')
for line in file1:
    temp_obj = line.strip()
    pdf_list.append(temp_obj)
    json_list.append(temp_obj[0:-4]+'-') 
file1.close()

# Supported mime_types are: 'application/pdf' and 'image/tiff'
mime_type = 'application/pdf'

# Number of pages grouped into each json output file - Make this greater than the max document length so it fits in 1 json response. 
batch_size = 100
client = vision.ImageAnnotatorClient()
feature = vision.Feature(
    type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

# Loops over all the items in the pdf_list
for i in range(0, len(pdf_list)):
    # Example gcs_source_uri = 'gs://BUCKET_NAME/225423441-Roberson-Joseph-A078-360-606-BIA-Nov-18-2013.pdf'
    gcs_source_uri = pdf_list[i]
    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(
        gcs_source=gcs_source, mime_type=mime_type)

    # Example gcs_destination_uri = 'gs://BUCKET_NAME/225423441-Roberson-Joseph-A078-360-606-BIA-Nov-18-2013-output-X-to-Y.json'
    gcs_destination_uri = json_list[i]
    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size)
    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config,
        output_config=output_config)
    operation = client.async_batch_annotate_files(
        requests=[async_request])
    print('Waiting for', json_list[i], 'to finish.')
    operation.result(timeout=420)

    # Displays progress of all PDFs being cleaned, takes a little under a minute per PDF to be converted. 
    print('PDF Number:', i+1, 'out of', len(json_list), 'completed.')