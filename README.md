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