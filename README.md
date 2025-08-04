# Orison AI
LLM Powered Achievement Based Case Assistant

## 🚀 Overview

Orison AI is a sophisticated AI-powered document assistance system that provides intelligent Q&A capabilities for legal documents, academic research, and case management. The system leverages advanced LLM technology, vector databases, and LangGraph workflows to deliver context-aware responses with source attribution.

## 🏗️ System Architecture

### Core Components
- **LangGraph Workflows**: Modern async workflow orchestration for document processing
- **Vector Database**: Qdrant-based storage for document embeddings and semantic search
- **LLM Integration**: OpenAI GPT with streaming responses for real-time interaction
- **Document Processing**: Advanced PDF parsing and text extraction capabilities
- **Scholar Network**: Google Scholar integration for academic research and networking

### Repository Structure
```
src/orison_ai/
├── 🎯 workflows/                 # LangGraph workflow definitions
│   ├── docassist_workflow.py    # Document Q&A workflow
│   ├── summarize_workflow.py    # Document summarization
│   ├── base.py                  # Base workflow classes
│   └── models.py                # Data models and schemas
├── 📦 core/                     # Core functionality
│   ├── client.py               # LLM client with streaming
│   ├── environment.py          # Centralized configuration
│   ├── config.py               # Application configuration
│   └── tests/                  # Unit tests
├── 📦 storage/                  # Vector operations and document processing
│   ├── vector_store.py         # Qdrant vector database operations
│   ├── document_processor.py   # PDF processing and text extraction
│   ├── vectorize_files.py      # File vectorization service
│   └── utils.py                # Storage utilities
├── 📦 services/                 # Business logic services
├── 📦 database/                 # Database operations
└── 📦 scripts/                  # Utility scripts
```

## 🎯 Key Features

### 1. Document Q&A System
- **Intelligent Context Retrieval**: Multi-query search for relevant document sections
- **Streaming Responses**: Real-time response generation with chunk-by-chunk output
- **Source Attribution**: Automatic linking of responses to source documents
- **Smart Filtering**: Filter by document tags, filenames, or content types
- **Context-Aware Answers**: Responses based on actual document content

### 2. Document Processing Pipeline
- **PDF Processing**: Advanced text extraction and formatting
- **Vector Embeddings**: OpenAI embeddings for semantic search
- **Efficient Storage**: Optimized vector database storage and retrieval
- **Batch Processing**: Handle multiple documents simultaneously

### 3. Scholar Network Building
- **Google Scholar Integration**: Fetch academic profiles and citations
- **Rate Limiting**: Smart 10 requests/minute with parallel processing
- **Network Analysis**: Build academic networks up to depth=5, size=1000+
- **Intelligent Caching**: 80%+ reduction in API calls through smart caching

### 4. Advanced Workflow Orchestration
- **LangGraph Workflows**: Modern async workflow management
- **Error Handling**: Comprehensive logging and error recovery
- **Scalable Architecture**: Designed for production-scale workloads
- **Real-time Processing**: Streaming responses for better user experience

## 🚀 Performance & Optimization

### Document Processing
- **Async Operations**: Non-blocking document processing
- **Streaming Responses**: Real-time output generation
- **Smart Chunking**: Efficient token management for large documents
- **Parallel Processing**: Batch operations for improved throughput

### Scholar Network Building
- **Before**: 2+ hours for moderate networks, frequent rate limit hits
- **After**: Build 1000-person networks at depth=5 efficiently
- **Rate Limiting**: Smart 10 req/min with parallel batch processing
- **Caching**: Intelligent in-memory cache reduces API calls by 80%+

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

## 🛠️ Development Setup

### Installing Hooks For Successful Push
- In the directory containing pre-commit config use the following commands
```
pre-commit install
pre-commit run --all-files
```

### Environment Configuration
```bash
# Required environment variables
export OPENAI_API_KEY="sk-..."
export QDRANT_URL="https://..."
export QDRANT_API_KEY="..."
export FIREBASE_CREDENTIALS_JSON='{"type": "service_account", ...}'

# Optional Scholar configuration
export SCHOLAR_REQUESTS_PER_MINUTE=10    # Default: 10
export SCHOLAR_MAX_DEPTH=3               # Default: 3
export SCHOLAR_MAX_NETWORK_SIZE=100      # Default: 100
```

## 🧪 Testing & Development

### Running the system locally for testing

#### Frontend
- Docker build should start the frontend as part of orison-frontend service
- Frontend initiates on port 3000 and can be accessed from a browser using:
```
localhost:3000
```
Frontend presently sends requests to the actual google cloud function

#### Emulated Frontend via Curl Python
- Make sure you set the standard Orison password as environment variable ORISON_PASSWORD
- Run the send_curl_request script with your payload and url corresponding to the cloud function. Below is an example:
```
python send_curl_request --url https://us-central1-orison-ai-visa-apply.cloudfunctions.net/gateway_function --data '{
    "data":{
      "or_request_type": "vectorize-files",
      "or_request_payload": {
        "attorneyId": "<attorney_hash>",
        "applicantId": "<applicant_hash>", 
        "fileId" : "<filename>.pdf",
        "bucket_name": "<bucket_name>"
      }
  }}' 
```

#### Backend
- Firing up the backend is feasible from exec ing into the container
- docker exec -ti orison /bin/bash
Now, you can run the following command to start the gateway function within the container:
```
cd src/orison_ai/gateway_function
functions-framework --target gateway_function --port=3000 --debug
OR
functions-framework --source=path/gateway_function/main.py --target=gateway_function --port=3000 --debug
```
- You can run the python curl program again by changing url to localhost:3000

### Testing Document Q&A Workflow
```python
from src.orison_ai.workflows.docassist_workflow import DocAssistWorkflow

# Initialize workflow
workflow = DocAssistWorkflow()

# Test document Q&A
result = await workflow.execute_with_prompt(
    question="What are the key requirements for this case?",
    tag=["immigration", "visa"],
    filename=["case_documents.pdf"]
)

print(result["response"])
```

## ☁️ Google Cloud Configuration
- Make sure gcloud is installed and configured on HOST Machine
Install the following packages:
https://cloud.google.com/sdk/docs/install#deb

You should be able to run the following command:
```
gcloud auth application-default login
```
- Enter the orison standard email and password for admins
The above command will authorize your local machine to access the google cloud services.
```
gcloud config list --all # List all config parameters
```
- Check the following:
```
gcloud config get-value project # Should be orison project name
# If project name is not set correctly then use the following
gcloud config set project orison-ai-visa-apply
gcloud auth list # Authorized service account should be correct
                # Make sure there is an * present before service account that is the same as
                # listed in details tab of the google function.
                # The service account credentials as part of JSON file should be set as
                # FIREBASE_CREDENTIALS environment variable within the container
# If incorrect service account is present, first set the new account using:
gcloud config set account <account name>
# Then change authentication credentials using following commands
gcloud auth activate-service-account --key-file=/path_to_key_downloaded_from_service_account
# Check again to make sure correct account is listed.
gcloud auth list
```

## 🚀 Deployment

### Gcloud Deployment
- Be in the directory containing gateway_function directory or change source accordingly
```
gcloud functions deploy gateway_function --runtime python311 --memory 1024 --trigger-http --allow-unauthenticated --entry-point gateway_function --source=gateway_function --no-gen2 --max-instances 100 --timeout 540
```

### Firebase CLI for frontend deployment
- Install using:
```
https://firebase.google.com/docs/cli
```
Make sure node is installed to version 22
- Commands for running dev environments
```
npm start # application
npm run dev # website
npm run build # Building production grade application and website
```
- Deployment commands:
```
npm run build
firebase logout
firebase login (use admin@orison.ai)
firebase deploy --project orison-ai-visa-apply --only hosting:orison-ai-visa-apply # For application
firebase deploy --project orison-ai-visa-apply --only hosting:orison-ai-landing # For website
```

## 📊 API Examples

### Document Q&A Request
```json
{
  "type": "DOCASSIST",
  "message": "What are the key requirements for this case?",
  "tag": ["immigration", "visa"],
  "filename": ["case_documents.pdf"],
  "attorneyId": "test_orison_attorney",
  "applicantId": "test_orison_applicant"
}
```

### Scholar Network Request
```json
{
  "type": "FETCH_SCHOLAR_NETWORK",
  "scholar_link": "https://scholar.google.com/citations?user=abc",
  "max_depth": 5,
  "max_size": 1000,
  "attorneyId": "test",
  "applicantId": "test"
}
```

## 🎯 Production Status

The Orison AI system is **production-ready** with:
- ✅ **Clean Architecture**: Well-organized, maintainable codebase
- ✅ **High Performance**: Optimized for scale and speed
- ✅ **Full Functionality**: Document Q&A, vectorization, scholar networks
- ✅ **Error Handling**: Comprehensive logging and error management
- ✅ **Streaming Support**: Real-time response generation
- ✅ **Source Attribution**: Proper citation of document sources
- ✅ **Google Cloud Integration**: Fully integrated with GCP services
- ✅ **Frontend Integration**: React-based UI with Firebase hosting

**Ready for deployment! 🚀**