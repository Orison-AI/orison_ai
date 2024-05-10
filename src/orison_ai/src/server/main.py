#! /usr/bin/env python3.10

# ==========================================================================
#  Copyright (c) Orison AI, 2024.
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

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import logging

# Internal

from orison_ai.src.server.helpers import (
    download_scholar_helper,
    ingest_helper,
    analysis_helper,
)
from orison_ai.src.server.models import DownloadRequest, IngestRequest, AnalysisRequest

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
DEMO:

curl -X POST "http://127.0.0.1:5004/download_scholar"      -H "Content-Type: application/json"      -d '{"business_id" : "demo_v2", "user_id": "rmalhan", "database" : "orison_ai", "category": "preliminary", "parameters" : {"scholar_link" : "https://scholar.google.com/citations?user=QW93AM0AAAAJ&hl=en&oi=ao", "file_name" : "scholar_profile"}}'

curl -X POST "http://127.0.0.1:5004/ingest"      -H "Content-Type: application/json"      -d '{"category" : "preliminary"}'

curl -X POST "http://127.0.0.1:5004/analyze"      -H "Content-Type: application/json"      -d '{"business_id" : "demo_v2", "user_id" : "rmalhan", "category" : "preliminary"}'
"""


@app.post("/download_scholar")
async def download_scholar(request: DownloadRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        download_scholar_helper,
        request.business_id,
        request.user_id,
        request.database,
        request.category,
        request.parameters,
    )
    return {
        "message": "Google scholar download task created",
        "user_id": request.user_id,
    }


@app.post("/ingest")
async def ingest(request: IngestRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(ingest_helper, request.category)
    return {
        "message": "Ingestion task created",
    }


@app.post("/analyze")
async def analyze(request: AnalysisRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        analysis_helper, request.business_id, request.user_id, request.category
    )
    return {
        "message": "Analysis task created",
    }
