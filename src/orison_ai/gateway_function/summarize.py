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
import os
from typing import Union
from enum import Enum
import logging

# from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI

# from langchain_openai import OpenAIEmbeddings
# from langchain_qdrant import Qdrant
# from langchain.retrievers.multi_query import MultiQueryRetriever

# Internal
from request_handler import (
    RequestHandler,
    OKResponse,
)
from or_store.firebase import (
    build_secret_url,
    read_remote_secret_url_as_string,
    CREDENTIALS_NOT_FOUND,
)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class DetailLevel(Enum):
    LIGHT = "light details"
    MODERATE = "moderate details"
    LENGTHY = "lengthy details"
    HEAVY = "very heavyily detailed"

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


class OpenAIPostman(ChatOpenAI):
    ROLE = """
    You are a helpful, respectful and honest assistant.\
    Always answer as helpfully as possible and follow ALL given instructions.\
    Do not speculate or make up information.\
    """

    def __init__(
        self,
        openai_api_key: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm = super().__init__(
            api_key=openai_api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=30.0,
        )

    def request(
        self,
        query: str,
        context: str = "",
        detail_level: Union[str, DetailLevel] = DetailLevel.LIGHT,
    ):
        if isinstance(detail_level, str):
            detail_level = DetailLevel.from_keyword(detail_level)

        prompt = [
            (
                "system",
                self.ROLE,
            ),
            (
                "human",
                f"Given the context: \n{context}, \n answer the following: {query} in {detail_level.value}.",
            ),
        ]
        return self.llm.invoke(prompt).content


class Summarize(RequestHandler):
    def __init__(self):
        openai_api_key = os.getenv("FIREBASE_CREDENTIALS")
        if openai_api_key is None:
            _logger.info(
                "Missing OPENAI_API_KEY in environment variable. Attempting secret manager"
            )
            try:
                # Getting secrets
                openai_api_key = read_remote_secret_url_as_string(
                    build_secret_url("openai_api_key")
                )
            except Exception as e:
                raise CREDENTIALS_NOT_FOUND(
                    "OPENAI_API_KEY not found in secret manager"
                )
        try:
            self.open_ai = OpenAIPostman(openai_api_key=openai_api_key)
        except Exception as e:
            _logger.error(f"Error initializing OpenAIPostman: {e}")
        super().__init__(str(self.__class__.__qualname__))

    async def handle_request(self, request_json):
        self.logger.info(f"Handling summarize request: {request_json}")
        _logger.info(self.open_ai.request(query="Hello World"))
        return OKResponse("Success!")
