"""Converts local JSON Response into a .txt file"""
import json
import io

# Make json list from bloblist
json_list = []
txt_list = []

# File containing all objects in the gcp bucket- only need '.json' files
# On Windows: 'gsutil ls gs://$BUCKET_NAME/*.json > blob_list.txt' to save file list, 'gsutil -m cp -r gs://$BUCKET_NAME/* "%userprofile%/Downloads" ' to download all files in a bucket
blob_text = open('blob_all.txt', 'r')
for line in blob_text:
    temp_obj = line.strip()
    if(temp_obj[-5:] == '.json'):
        json_list.append(temp_obj) 
        txt_list.append(temp_obj[0:-5]+'.txt') 
blob_text.close()

#Extracts text-only response from the Google Vision API response; exculdes data like bounding boxes, language detected, and % confidence. Use UTF-8 encoding for reading & writing 
for i in range(0, len(json_list)):
    with io.open(json_list[i], encoding='utf-8') as json_values:
        myRecord = json.load(json_values)
        with io.open(txt_list[i], "w+", encoding='utf-8') as txt_values:
            print(txt_list[i])

            # Single page's response located in myRecord['responses'][j]['fullTextAnnotation']['text']
            for j in range(0, len(myRecord['responses'])):
                temp_page = myRecord['responses'][j]['fullTextAnnotation']['text'].encode('utf-8')
                txt_values.write(str(temp_page, encoding='utf-8'))
            txt_values.close() 