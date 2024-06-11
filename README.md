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


Requires to kick off backend and frontend
- Backend can be started using functions-framework package
- We can use the port 5004 and localhost which is exposed by default in the docker container
- Port and host are subject to change
```
functions-framework --source=path/to/gateway_function/main.py --target=gateway_function --port=XXXX --host=<HOSTNAME>
```
- Frontend can be emulated using curl request
- Authentication ToDo
```
ToDo: Add curl format
```