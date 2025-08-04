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

import uuid
from typing import Union, List
from dataclasses import dataclass
from enum import Enum


@dataclass
class Prompt:
    question: str
    detail_level: str
    tag: Union[List[str], str] = None  # vector DB tag
    filename: Union[List[str], str] = None  # vector DB filename
    id: str = None
    # Used if memory is True
    applicant_id: str = None
    attorney_id: str = None
    answer: str = None
    source: str = None

    def __post_init__(self):
        if self.id is None:
            self.id = uuid.uuid4().hex


class DetailLevel(Enum):
    LIGHT = "light detail"
    MODERATE = "moderate detail"
    LENGTHY = "lengthy detail"
    HEAVY = "very heavy detail"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def from_keyword(cls, keyword):
        keyword = keyword.lower()
        for member in cls:
            if keyword in member.value.lower():
                return member
        raise ValueError(f"No matching DetailLevel for keyword: {keyword}")
