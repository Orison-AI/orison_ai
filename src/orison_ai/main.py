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

from orison_ai.workflows.docassist_workflow import DocAssistWorkflow
from orison_ai.workflows.summarize_workflow import SummarizeWorkflow
from orison_ai.storage.vectorize_files import VectorizeFiles, DeleteFileVectors
from orison_ai.services.scholar.scholar_service import ScholarService
from orison_ai.services.scholar.utils import extract_scholar_id
from orison_ai.database.firebase_config import FireStoreDB

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
docassist_workflow = DocAssistWorkflow()
summarize_workflow = SummarizeWorkflow()
scholar_service = ScholarService()
firestore_db = FireStoreDB()
vectorize_files_service = VectorizeFiles()
delete_file_vectors_service = DeleteFileVectors()


async def get_applicant_name(applicant_id: str) -> str:
    """Get applicant name from Firestore applicants collection"""
    try:
        doc_ref = firestore_db.client.collection("applicants").document(applicant_id)
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            name = data.get("name")
            if name:
                return name
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Name field not found for applicant {applicant_id}",
                )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Applicant {applicant_id} not found in Firestore",
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error fetching applicant name: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch applicant name: {str(e)}"
        )


async def router(request_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Route requests to appropriate handlers"""
    try:
        logger.info(f"Routing request: {request_type}")

        if request_type == "process-scholar-link":
            # Get applicant name from Firestore
            applicant_name = await get_applicant_name(payload["applicantId"])

            # result = await scholar_service.get_scholar_info(
            #     attorney_id=payload["attorneyId"],
            #     applicant_id=payload["applicantId"],
            #     scholar_link=payload["scholarLink"],
            #     author_name=applicant_name,
            # )
            result = {}
            return {
                "status": 200,
                "message": result.__dict__ if hasattr(result, "__dict__") else result,
            }

        elif request_type == "process-scholar-network":
            # Get applicant name from Firestore
            applicant_name = await get_applicant_name(payload["applicantId"])

            scholar_id = extract_scholar_id(payload["scholarLink"])
            if not scholar_id:
                return {"status": 400, "message": "Invalid scholar URL"}

            # result = await scholar_service.build_network_database(
            #     root_scholar_id=scholar_id,
            #     author_name=applicant_name,
            #     max_depth=payload.get("max_depth", 1),
            #     max_size=payload.get("max_size", 10),
            # )
            result = {}
            return {
                "status": 200,
                "message": result.__dict__ if hasattr(result, "__dict__") else result,
            }

        elif request_type == "vectorize-files":
            result = await vectorize_files_service.vectorize_file(
                attorney_id=payload["attorneyId"],
                applicant_id=payload["applicantId"],
                file_id=payload["fileId"],
                tag=payload["tag"],
            )
            return {"status": 200, "message": result}

        elif request_type == "delete-file-vectors":
            result = await delete_file_vectors_service.delete_vectors(
                attorney_id=payload["attorneyId"],
                applicant_id=payload["applicantId"],
                file_id=payload["fileId"],
                tag=payload["tag"],
            )
            return {"status": 200, "message": result}

        elif request_type == "summarize":
            result = await summarize_workflow.execute_with_ids(
                attorney_id=payload["attorneyId"], applicant_id=payload["applicantId"]
            )
            return {"status": 200, "message": result}

        elif request_type == "docassist":
            result = await docassist_workflow.execute_with_ids(
                attorney_id=payload["attorneyId"],
                applicant_id=payload["applicantId"],
                question=payload["message"],
                tag=payload["tag"],
                filename=payload["filename"],
            )
            return {"status": 200, "message": result}

        else:
            return {"status": 400, "message": f"Unknown request type: {request_type}"}

    except Exception as e:
        logger.error(f"Error in router: {e}")
        return {"status": 500, "message": str(e)}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Orison AI API is running", "status": "healthy"}


@functions_framework.http
def gateway_function(request):
    """
    Google Cloud Function HTTP entry point.
    This function wraps the FastAPI app to work with Google Cloud Functions.
    """
    # Handle CORS preflight requests
    if request.method == "OPTIONS":
        return ("", 204, CORS_PREFLIGHT_HEADERS)

    # Set CORS headers for main request
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

    try:
        # Parse the request body
        request_data = request.get_json()

        if not request_data:
            return ({"error": "Invalid JSON payload"}, 400, headers)

        # Validate request using GatewayRequest model
        try:
            gateway_request = GatewayRequest(**request_data)
        except Exception as validation_error:
            return (
                {"error": f"Invalid request format: {str(validation_error)}"},
                400,
                headers,
            )

        # Route the request
        result = asyncio.run(
            router(gateway_request.or_request_type, gateway_request.or_request_payload)
        )
        code = result["status"]

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
        logger.error(f"ERROR: {e}")
        return ({"error": str(e)}, 500, headers)


# Keep the original FastAPI endpoints for local development/testing
if __name__ == "__main__":
    app = functions_framework.create_app(gateway_function)
    app.run(port=int(os.environ.get("PORT", 5004)), host="0.0.0.0", debug=True)
