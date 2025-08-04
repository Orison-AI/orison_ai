#! /usr/bin/env python3.11

# ==========================================================================
#  Copyright (c) Orison AI, 2025.
#
#  All rights reserved. All hardware and software names used are registered
#  trade names and/or registered trademarks of the respective manufacturers.
#
#  The user of this computer program acknowledges that the above copyright
#  notice, which constitutes the Universal Copyright Convention, will be
#  attached at the position in the function of the computer program which the
#  author has deemed to sufficiently express the reservation of copyright.
#  It is prohibited for customers, users and/or third parties to remove,
#  modify or move this copyright notice.
# ==========================================================================

# External

import os
import asyncio
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import functions_framework

# Internal

from workflows.docassist_workflow import DocAssistWorkflow
from workflows.summarize_workflow import SummarizeWorkflow
from storage.vectorize_files import VectorizeFiles, DeleteFileVectors
from services.scholar.scholar_service import ScholarService
from services.scholar.utils import extract_scholar_id
from database.firebase_config import FireStoreDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Orison AI API",
    description="AI-powered document assistance and scholar network API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CORS headers for preflight requests
CORS_PREFLIGHT_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "3600",
}

# CORS headers for main requests
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
}


class GatewayRequest(BaseModel):
    or_request_type: str
    or_request_payload: Dict[str, Any]


# Initialize workflow instances (lightweight - actual initialization happens when needed)
logger.info("Initializing workflow instances...")
try:
    docassist_workflow = DocAssistWorkflow()
    summarize_workflow = SummarizeWorkflow()
    scholar_service = ScholarService()
    firestore_db = FireStoreDB()
    vectorize_files_service = VectorizeFiles()
    delete_file_vectors_service = DeleteFileVectors()
    logger.info("All workflow instances initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize workflow instances: {e}")
    raise


async def get_applicant_name(applicant_id: str) -> str:
    """Get applicant name from Firestore applicants collection"""
    logger.info(f"Fetching applicant name for ID: {applicant_id}")
    try:
        doc_ref = firestore_db.client.collection("applicants").document(applicant_id)
        logger.info(
            f"Firestore document reference created for applicant: {applicant_id}"
        )

        doc = doc_ref.get()
        logger.info(f"Firestore document retrieved, exists: {doc.exists}")

        if doc.exists:
            data = doc.to_dict()
            logger.info(f"Document data keys: {list(data.keys()) if data else 'None'}")
            name = data.get("name")
            if name:
                logger.info(f"Successfully retrieved applicant name: {name}")
                return name
            else:
                logger.error(
                    f"Name field not found in document data for applicant {applicant_id}"
                )
                raise HTTPException(
                    status_code=404,
                    detail=f"Name field not found for applicant {applicant_id}",
                )
        else:
            logger.error(f"Applicant document not found in Firestore: {applicant_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Applicant {applicant_id} not found in Firestore",
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            logger.error(f"HTTPException in get_applicant_name: {e}")
            raise e
        logger.error(f"Unexpected error fetching applicant name: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch applicant name: {str(e)}"
        )


async def router(request_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Route requests to appropriate handlers"""
    logger.info(f"Router called with request_type: {request_type}")
    logger.info(f"Router payload keys: {list(payload.keys()) if payload else 'None'}")

    try:
        logger.info(f"Processing request: {request_type}")

        if request_type == "process-scholar-link":
            logger.info("Processing scholar link request")
            # Get applicant name from Firestore
            applicant_name = await get_applicant_name(payload["applicantId"])
            logger.info(f"Retrieved applicant name: {applicant_name}")

            await scholar_service.get_scholar_info(
                attorney_id=payload["attorneyId"],
                applicant_id=payload["applicantId"],
                scholar_link=payload["scholarLink"],
                author_name=applicant_name,
            )
            logger.info("Scholar link processing completed successfully")
            return {
                "status": 200,
                "message": "Scholar data processed and stored successfully",
            }

        elif request_type == "process-scholar-network":
            logger.info("Processing scholar network request")
            # Get applicant name from Firestore
            applicant_name = await get_applicant_name(payload["applicantId"])
            logger.info(f"Retrieved applicant name: {applicant_name}")

            scholar_id = extract_scholar_id(payload["scholarLink"])
            logger.info(f"Extracted scholar ID: {scholar_id}")
            if not scholar_id:
                logger.error("Invalid scholar URL - could not extract scholar ID")
                return {"status": 400, "message": "Invalid scholar URL"}

            await scholar_service.build_network_database(
                root_scholar_id=scholar_id,
                author_name=applicant_name,
                attorney_id=payload["attorneyId"],
                applicant_id=payload["applicantId"],
                max_depth=payload.get("max_depth", 3),
                max_size=payload.get("max_size", 20),
            )
            logger.info("Scholar network processing completed successfully")
            return {
                "status": 200,
                "message": "Scholar network processed and stored successfully",
            }

        elif request_type == "vectorize-files":
            logger.info("Processing vectorize files request")
            result = await vectorize_files_service.vectorize_file(
                attorney_id=payload["attorneyId"],
                applicant_id=payload["applicantId"],
                file_id=payload["fileId"],
                tag=payload["tag"],
            )
            logger.info("File vectorization completed successfully")
            return {"status": 200, "message": result}

        elif request_type == "delete-file-vectors":
            logger.info("Processing delete file vectors request")
            result = await delete_file_vectors_service.delete_vectors(
                attorney_id=payload["attorneyId"],
                applicant_id=payload["applicantId"],
                file_id=payload["fileId"],
                tag=payload["tag"],
            )
            logger.info("File vectors deletion completed successfully")
            return {"status": 200, "message": result}

        elif request_type == "summarize":
            logger.info("Processing summarize request")
            result = await summarize_workflow.execute_with_ids(
                attorney_id=payload["attorneyId"], applicant_id=payload["applicantId"]
            )
            logger.info("Summarization completed successfully")
            # Return simple confirmation - UI will retrieve data from Firestore
            return {
                "status": 200,
                "message": "Summarization completed successfully. Data available in Firestore.",
            }

        elif request_type == "docassist":
            logger.info("Processing docassist request")
            result = await docassist_workflow.execute_with_ids(
                attorney_id=payload["attorneyId"],
                applicant_id=payload["applicantId"],
                question=payload["message"],
                tag=payload["tag"],
                filename=payload["filename"],
            )
            logger.info("Docassist processing completed successfully")
            # Return simple confirmation - UI will retrieve data from Firestore
            return {
                "status": 200,
                "message": "Docassist processing completed successfully. Data available in Firestore.",
            }

        else:
            logger.error(f"Unknown request type: {request_type}")
            return {"status": 400, "message": f"Unknown request type: {request_type}"}

    except Exception as e:
        logger.error(f"Error in router: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception details: {str(e)}")
        return {"status": 500, "message": str(e)}


@app.get("/")
async def root():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return {"message": "Orison AI API is running", "status": "healthy"}


@functions_framework.http
def gateway_function(request):
    """
    Google Cloud Function HTTP entry point.
    This function wraps the FastAPI app to work with Google Cloud Functions.
    """
    logger.info(f"Gateway function called with method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")

    # Handle CORS preflight requests
    if request.method == "OPTIONS":
        logger.info("Handling CORS preflight request")
        return ("", 204, CORS_PREFLIGHT_HEADERS)

    # Set CORS headers for main request
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

    try:
        logger.info("Parsing request body...")
        # Parse the request body
        request_data = request.get_json()
        logger.info(f"Request data received: {request_data}")

        if not request_data:
            logger.error("Invalid JSON payload - request_data is None or empty")
            return ({"error": "Invalid JSON payload"}, 400, headers)

        # Handle Firebase Functions wrapper - Firebase Functions wraps data in a 'data' field
        if isinstance(request_data, dict) and "data" in request_data:
            logger.info("Detected Firebase Functions wrapper, extracting data field")
            request_data = request_data["data"]

        # Validate request using GatewayRequest model
        try:
            logger.info("Validating request using GatewayRequest model...")
            gateway_request = GatewayRequest(**request_data)
            logger.info(
                f"Request validation successful. Type: {gateway_request.or_request_type}"
            )
            logger.info(
                f"Request payload keys: {list(gateway_request.or_request_payload.keys())}"
            )
        except Exception as validation_error:
            logger.error(f"Request validation failed: {validation_error}")
            return (
                {"error": f"Invalid request format: {str(validation_error)}"},
                400,
                headers,
            )

        # Route the request
        logger.info("Routing request to async router...")
        result = asyncio.run(
            router(gateway_request.or_request_type, gateway_request.or_request_payload)
        )
        code = result["status"]
        logger.info(f"Router returned status: {code}, result: {result}")

        return (
            {
                "data": (
                    {"message": result["message"]}
                    if code == 200
                    else {"Internal Server Error": result["message"]}
                )
            },
            code,
            headers,
        )

    except Exception as e:
        logger.error(f"ERROR in gateway_function: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception details: {str(e)}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        return ({"error": str(e)}, 500, headers)


# Keep the original FastAPI endpoints for local development/testing
if __name__ == "__main__":
    logger.info("Starting FastAPI app in development mode...")
    app = functions_framework.create_app(gateway_function)
    app.run(port=int(os.environ.get("PORT", 5004)), host="0.0.0.0", debug=True)
