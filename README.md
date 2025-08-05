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
- **Secret Management**: Google Secret Manager integration for secure configuration
- **Firebase Integration**: Comprehensive Firestore and Firebase Storage support

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
│   ├── environment.py          # Centralized configuration with Secret Manager
│   ├── config.py               # Application configuration
│   └── tests/                  # Unit tests
├── 📦 storage/                  # Vector operations and document processing
│   ├── vector_store.py         # Qdrant vector database operations
│   ├── document_processor.py   # PDF processing and text extraction
│   ├── vectorize_files.py      # File vectorization service
│   └── utils.py                # Storage utilities
├── 📦 database/                 # Database operations and Firebase integration
│   ├── firebase_config.py      # Firebase configuration and Secret Manager
│   ├── firestore_clients.py    # Firestore client operations
│   ├── firebase_storage.py     # Firebase Storage operations
│   ├── schema.py               # Database schemas and models
│   └── secrets.py              # Secret management utilities
├── 📦 services/                 # Business logic services
│   └── scholar/                # Scholar network services
├── 📦 scripts/                  # Utility scripts
└── 📦 templates/                # Template files
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

### 5. Secure Configuration Management
- **Google Secret Manager**: Secure storage of sensitive configuration
- **Environment Fallback**: Graceful fallback to environment variables
- **Centralized Configuration**: Single source of truth for all settings
- **Liberal Validation**: Flexible configuration loading with warnings

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

### Configuration Management
- **Secret Manager Integration**: Secure, centralized secret management
- **Environment Hierarchy**: Secret Manager → Environment Variables → Defaults
- **Graceful Degradation**: System continues to work with missing configuration
- **Comprehensive Logging**: Detailed logging for configuration loading

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

#### Required Environment Variables
```bash
# Core services
export OPENAI_API_KEY="sk-..."
export QDRANT_URL="https://..."
export QDRANT_API_KEY="..."
export FIREBASE_CREDENTIALS_JSON='{"type": "service_account", ...}'

# Optional Scholar configuration
export SCHOLAR_REQUESTS_PER_MINUTE=10    # Default: 10
export SCHOLAR_MAX_DEPTH=3               # Default: 3
export SCHOLAR_MAX_NETWORK_SIZE=20       # Default: 20

# Optional LangSmith configuration
export LANGCHAIN_API_KEY="..."           # For LangSmith tracing
export LANGCHAIN_PROJECT="orison-ai"     # Project name for LangSmith
export LANGCHAIN_TRACING="true"          # Enable LangSmith tracing

# Optional SerpAPI configuration
export SERPAPI_KEY="..."                 # For web search capabilities
```

#### Google Secret Manager Integration
The system automatically integrates with Google Secret Manager for secure configuration management:

1. **Automatic Fallback**: If environment variables are not set, the system will attempt to fetch secrets from Google Secret Manager
2. **Project Configuration**: Uses the project prefix `projects/685108028813/secrets/`
3. **Graceful Degradation**: System continues to work with missing configuration, logging warnings
4. **Liberal Validation**: Flexible configuration loading that doesn't fail on missing optional values

#### Configuration Loading Hierarchy
1. **Environment Variables**: First priority for configuration values
2. **Google Secret Manager**: Fallback for missing environment variables
3. **Default Values**: Final fallback for optional configuration

## 🔍 LangSmith Integration

Orison AI includes comprehensive LangSmith integration for LLM observability, tracing, and monitoring. All LLM operations are automatically traced and can be viewed in the LangSmith dashboard.

### LangSmith Features
- **Automatic Tracing**: All LLM calls are automatically traced and logged
- **Project Organization**: Separate projects for different environments
- **Performance Monitoring**: Track response times, token usage, and costs
- **Error Tracking**: Monitor failed requests and debugging information
- **Custom Endpoints**: Support for self-hosted LangSmith instances

### Environment Variables
```bash
# Required for LangSmith tracing
export LANGCHAIN_API_KEY="lsv2_..."              # Your LangSmith API key
export LANGCHAIN_PROJECT="orison-ai"             # Project name in LangSmith

# Optional LangSmith configuration
export LANGCHAIN_TRACING="true"                  # Enable tracing (default: true)
```

### Automatic Integration
LangSmith is automatically configured when the `LLMClient` is initialized. The integration covers:

- **Document Q&A Workflows**: All question-answer operations
- **Document Summarization**: Complete summarization workflows
- **Vector Embeddings**: Document embedding operations
- **Scholar Network Analysis**: LLM operations in scholar services
- **Script Operations**: All utility scripts using LLM operations

### Testing LangSmith Integration
```python
# Test script to verify LangSmith integration
from src.orison_ai.test_langsmith import test_langsmith_integration
import asyncio

# Run the test
asyncio.run(test_langsmith_integration())
```

### LangSmith Dashboard
Once configured, you can view all LLM operations in the LangSmith dashboard:
1. **Traces**: View individual request traces with inputs, outputs, and metadata
2. **Projects**: Organize traces by project (e.g., "orison-ai")
3. **Analytics**: Monitor performance metrics and costs
4. **Debugging**: Inspect failed requests and error details

### Self-Hosted LangSmith
For enterprise deployments, you can use a self-hosted LangSmith instance:

### Integration Points
LangSmith tracing is automatically enabled for:
- ✅ **Core LLM Client**: All OpenAI API calls
- ✅ **Document Workflows**: DocAssist and Summarize workflows
- ✅ **Vector Operations**: Embedding generation and storage
- ✅ **Scholar Services**: LLM operations in scholar analysis
- ✅ **Script Operations**: All utility scripts
- ✅ **API Endpoints**: All FastAPI endpoints using LLM operations

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
cd src/orison_ai/orison_ai
functions-framework --target gateway_function --port=5004 --debug
OR
functions-framework --source=path/orison_ai/main.py --target=gateway_function --port=5004 --debug
```
- You can run the python curl program again by changing url to localhost:5004

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

### Testing Configuration Loading
```python
from src.orison_ai.core.environment import get_env

# Get the global environment configuration
env = get_env()

# Access configuration values
print(f"OpenAI API Key configured: {env.openai_api_key is not None}")
print(f"Scholar rate limit: {env.scholar_requests_per_minute} req/min")
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

### Google Secret Manager Setup
For production deployments, configure secrets in Google Secret Manager:

```bash
# Create secrets in Secret Manager
echo "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
echo "your-qdrant-url" | gcloud secrets create QDRANT_URL --data-file=-
echo "your-qdrant-api-key" | gcloud secrets create QDRANT_API_KEY --data-file=-
echo '{"type": "service_account", ...}' | gcloud secrets create FIREBASE_CREDENTIALS --data-file=-
```

## 🚀 Deployment

### Gcloud Deployment
- Be in the directory containing gateway_function directory or change source accordingly
```
gcloud functions deploy gateway_function --runtime python311 --memory 1024 --trigger-http --allow-unauthenticated --entry-point=gateway_function --source=orison_ai --no-gen2 --max-instances 100 --timeout 540
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

## 🔧 Dependencies

### Core Dependencies
- **FastAPI**: Modern web framework for API development
- **OpenAI**: Latest OpenAI API client for LLM integration
- **LangChain**: Framework for LLM application development
- **LangGraph**: Workflow orchestration and state management
- **LangSmith**: LLM observability and tracing platform
- **Qdrant**: Vector database for semantic search
- **Firebase Admin**: Firebase integration for authentication and storage
- **Google Cloud**: Secret Manager and Firestore integration

### Development Dependencies
- **Pytest**: Testing framework with async support
- **Functions Framework**: Google Cloud Functions development
- **Uvicorn**: ASGI server for FastAPI applications

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
- ✅ **Secure Configuration**: Google Secret Manager integration
- ✅ **Graceful Degradation**: System continues to work with missing configuration
- ✅ **Comprehensive Logging**: Detailed logging for debugging and monitoring
- ✅ **LangSmith Integration**: Complete LLM observability and tracing

**Ready for deployment! 🚀**