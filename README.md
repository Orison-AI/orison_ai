# orison_ai
LLM Powered Visa Petitioner

## Local Debugging
Install the following packages:
https://cloud.google.com/sdk/docs/install#deb

You should be able to run the following command:
```
gcloud auth application-default login
```
The above command will authorize your local machine to access the google cloud services.

Now, you can run the following command to start the gateway function:
```
cd src/orison_ai/gateway_function
functions-framework --target gateway_function --debug
```

## Using the GUNICORN server and sending requests
- Go the the directory that contains src/server/main.py and execute the following command
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5004 --timeout 240

- A server should sping up and from a different docker bash send requests like:

1. Retrieving google scholar info:
```
curl -X POST "http://127.0.0.1:5004/download_scholar"      -H "Content-Type: application/json"      -d '{"attorney_id" : "demo_v2", "applicant_id": "rmalhan", "database" : "orison_ai", "category": "preliminary", "parameters" : {"scholar_link" : "https://scholar.google.com/citations?user=QW93AM0AAAAJ&hl=en&oi=ao", "file_name" : "scholar_profile"}}'

2. Ingesting files (Currently folder paths are stored as constants under utils)
curl -X POST "http://127.0.0.1:5004/ingest"      -H "Content-Type: application/json"      -d '{"category" : "preliminary"}'

3. Asking for preliminary analysis on the ingested files
curl -X POST "http://127.0.0.1:5004/analyze"      -H "Content-Type: application/json"      -d '{"attorney_id" : "demo_v2", "applicant_id" : "rmalhan", "category" : "preliminary"}'
```

## Running Streamlit app
- Command line argument to run streamlit
```
streamlit run path/to/api/server.py --server.port 5004
```

- Enter "rmalhan" as user id and login.
- Navigate to different radio buttons to see results pulled from mongo

## UI Mocks
https://app.diagrams.net/#G1aSTaQyNfZddZbYDaOraN6fZ3naUI6_or#%7B%22pageId%22%3A%22G5q3h0-aANIR-RvPyDPR%22%7D
