# Orison AI
LLM Powered Achievement Based Case Assistant

## Navigating the repo
- Structure of the repository is based on integratability with google cloud platform
- Front end is react based hosted on google Firebase and located under /frontend
- The user stories governing frontend application is located within doc
- API details can be found under /api/orison_api.md. Front end sends one gateway request
    to the backend which gets routed to corresponding business logic for processing.
- Business logic is present under src/
    Main is the entry point that checks for authentication and validity of the gateway request
    Gateway function routes the request to corresponding business logic
    API yaml is blueprint for structure of these requests and responses
    The structure gets converted to python dataclasses by backend
- Docker files run bare minimum dependencies required and are assigned package versions for consistency
- devcontainer is recommend for using development IDEs like VScode

## UI Mockups
https://app.diagrams.net/#G1XuFSqzs4L6TMyR-XOJId8UXAsaoEyrx4#%7B%22pageId%22%3A%22G5q3h0-aANIR-RvPyDPR%22%7D

## Installing Hooks For Successful Push
- In the directory containing pre-commit config use the following commands
```
pre-commit install
pre-commit run --all-files
```

## Running the system locally for testing
## Frontend
- Docker build should start the frontend as part of orison-frontend service
- Frontend initiates on port 3000 and can be accessed from a browser using:
```
localhost:3000
```
Frontend presently sends requests to the actual google cloud function

## Emulated Frontend via Curl
- Run the send_curl_request script with your payload. Below is an example:
```
curl -m 70 -X POST https://us-central1-orison-ai-visa-apply.cloudfunctions.net/gateway_function_staging \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
    "data":{
      "or_request_type": "vectorize-files",
      "or_request_payload": {
        "attorneyId": "<attorney_hash>",
        "applicantId": "<applicant_hash>", 
        "fileIds" : ["<filename>.pdf"],
        "bucketName": "<bucketName>"
      }
  }}' 
```

## Backend
- Firing up the backend is feasible from exec ing into the container
- docker exec -ti orison /bin/bash
Now, you can run the following command to start the gateway function within the container:
```
cd src/orison_ai/gateway_function
functions-framework --target gateway_function --port=3000 --debug
OR
functions-framework --source=path/gateway_function/main.py --target=gateway_function --port=3000 --debug
```

## GCloud Configuration
- Make sure gcloud is installed and configured on HOST Machine
Install the following packages:
https://cloud.google.com/sdk/docs/install#deb

You should be able to run the following command:
```
gcloud auth application-default login
```
- Enter the orison standard email and password for admins
The above command will authorize your local machine to access the google cloud services.
- Check the following:
```
gcloud config get-value project # Should be orison project name
gcloud auth list # Authorized service account should be correct
                Credential JSON corresponding to service account should be FIREBASE_CREDENTIALS
                environment variable within the container
# If incorrect service account is present, change using following commands
gcloud auth activate-service-account --key-file=/path_to_key_downloaded_from_service_account
# Check again
gcloud auth list
```

## Gcloud Deployment
- Be in the directory containing gateway_function directory or change source accordingly
```
gcloud functions deploy gateway_function --runtime python310 --memory 512 --trigger-http --allow-unauthenticated --entry-point gateway_function --source=gateway_function --no-gen2 --max-instances 5 --timeout 60
```