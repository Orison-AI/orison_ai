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

from pydantic import BaseModel


class IngestRequest(BaseModel):
    category: str


class DownloadRequest(BaseModel):
    attorney_id: str
    applicant_id: str
    database: str
    category: str
    parameters: dict


class AnalysisRequest(BaseModel):
    attorney_id: str
    applicant_id: str
    category: str
