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
import json
from typing import Union, List
from enum import Enum
import traceback
import logging
from dataclasses import dataclass
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import Qdrant
from langchain.retrievers.multi_query import MultiQueryRetriever

# Internal

from request_handler import RequestHandler, OKResponse, ErrorResponse
from exceptions import (
    LLM_INITIALIZATION_FAILED,
    QDrant_INITIALIZATION_FAILED,
    Retriever_INITIALIZATION_FAILED,
)
from or_store.models import ScreeningBuilder, QandA, StoryBuilder
from or_store.story_client import ScreeningClient, StoryClient
from or_store.firebase import OrisonSecrets
from utils import async_generator_from_list

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


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


class OpenAIPostman(ChatOpenAI):
    ROLE = """
    You are a helpful, respectful and honest assistant.\
    Always answer as helpfully as possible and follow ALL given instructions.\
    Do not speculate or make up information.\
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=30.0,
            **kwargs,
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
        return self.invoke(prompt).content


@dataclass
class Prompt:
    question: list
    detail_level: str


class Summarize(RequestHandler):
    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))

    def initialize(self, secrets):
        try:
            self.postman = OpenAIPostman(api_key=secrets.openai_api_key)
        except Exception as e:
            message = f"Error initializing OpenAIPostman. Error: {e}"
            _logger.error(message)
            raise LLM_INITIALIZATION_FAILED(message)

        try:
            self.qdrant_client = QdrantClient(
                url=os.getenv("QDRANT_URL"),
                api_key=os.getenv("QDRANT_API_KEY"),
            )

            # Define the name of the collection
            collection_name = secrets.collection_name
            # ToDo: Include embedding as part of Postman
            # Use Postman in vectorization
            embedding = OpenAIEmbeddings(
                model="text-embedding-ada-002", api_key=secrets.openai_api_key
            )
            self.vectordb = Qdrant(
                client=self.qdrant_client,
                collection_name=collection_name,
                embeddings=embedding,
            )
        except Exception as e:
            message = f"Error initializing Qdrant. Error: {e}"
            _logger.error(message)
            raise QDrant_INITIALIZATION_FAILED(message)

        try:
            self.retriever = MultiQueryRetriever.from_llm(
                retriever=self.vectordb.as_retriever(search_kwargs={"k": 10}),
                llm=self.postman,
                include_original=True,
            )
        except Exception as e:
            message = f"Error initializing Retriever. Error: {e}"
            _logger.error(message)
            raise Retriever_INITIALIZATION_FAILED(message)
        self._screening_client = ScreeningClient()

    @staticmethod
    def prompts(
        file_path: str = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "templates",
            "eb1_a_questionnaire.json",
        ),
    ):
        prompts = []
        with open(file=file_path, mode="r") as file:
            js = json.load(file)
            for question, detail_level in zip(
                js["prompt"]["research"]["question"],
                js["prompt"]["research"]["detail_level"],
            ):
                prompts.append(
                    Prompt(
                        question=question,
                        detail_level=detail_level,
                    )
                )
            file.close()
        return prompts

    async def get_multi_query_screening(self, prompts: List[Prompt]):
        screening = ScreeningBuilder()
        async for prompt in async_generator_from_list(prompts):
            retrieved_docs = self.retriever.invoke(prompt.question)
            context = "\n".join([doc.page_content for doc in retrieved_docs])
            source = "\n".join(
                [
                    f'Page: {doc.metadata["page"]} and Source:{doc.metadata["source"]}'
                    for doc in retrieved_docs
                ]
            )
            response = self.postman.request(
                prompt.question, context, prompt.detail_level
            )
            qna = QandA(question=prompt.question, answer=response, source=source)
            screening.summary.append(qna)
        return screening

    async def handle_request(self, request_json):
        self.logger.info(f"Handling summarize request: {request_json}")
        attorney_id = request_json["attorneyId"]
        applicant_id = request_json["applicantId"]
        # ToDo: Use bucket with qdrant tag
        bucket_name = request_json["bucketName"]
        try:
            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            _logger.info("Initializing summarizer with secrets")
            self.initialize(secrets)
            prompts = self.prompts()
            _logger.info("Initializing summarizer with secrets...done")
            screening = await self.get_multi_query_screening(prompts)
            screening.attorney_id = attorney_id
            screening.applicant_id = applicant_id
            screening.bucket_name = bucket_name
            _logger.info("Storing screening in Firestore")
            id = await self._screening_client.insert(screening)
            _logger.info(f"Screening stored in Firestore with ID: {id}")
            return OKResponse("Success!")
        except Exception as e:
            message = f"Error processing files: {e}"
            self.logger.error(message)
            return ErrorResponse(message)
