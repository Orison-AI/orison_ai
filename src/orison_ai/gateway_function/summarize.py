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

import logging
import re
import uuid
import os
import asyncio
import tiktoken
import json
from typing import Union, List
from enum import Enum
from dataclasses import dataclass
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI
from langchain_qdrant import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Internal

from request_handler import RequestHandler, OKResponse, ErrorResponse
from exceptions import (
    LLM_INITIALIZATION_FAILED,
    QDrant_INITIALIZATION_FAILED,
    Retriever_INITIALIZATION_FAILED,
)
from or_store.models import ScreeningBuilder, StoryBuilder, QandA
from or_store.story_client import ScreeningClient
from or_store.firebase import OrisonSecrets
from utils import async_generator_from_list, ThrottleRequest, OPENAI_SLEEP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "gpt-4-turbo"


@dataclass
class Prompt:
    question: list
    detail_level: str
    id: str = uuid.uuid4().hex


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


class OrisonMessenger(ChatOpenAI):
    ROLE = """
    You are a helpful, respectful and honest assistant.\
    Always answer as helpfully as possible and follow ALL given instructions.\
    Do not speculate or make up information.\
    """

    MULTI_QUERY_ROLE = """
    You are an AI language model assistant. \
    Your task is to generate 3 different versions of the given user question. \
    The questions will be used to retrieve relevant documents from a vector database. \
    By generating multiple perspectives on the user question, your goal is to help the user overcome some of the limitations of distance-based similarity search. \
    Provide these alternative questions separated by newlines.
    """

    def __init__(
        self,
        api_key: str,
        model: str = MODEL_NAME,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **kwargs,
    ):
        super().__init__(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=90.0,
            **kwargs,
        )

    @staticmethod
    async def truncate_to_max_tokens(text: str, max_tokens: int = 120000) -> str:
        """
        Truncate the input text to the maximum allowed tokens
        :param text: Input text
        :param max_tokens: Maximum allowed tokens
        :return: Truncated text
        """

        # Initialize the tokenizer for the specific model
        tokenizer = tiktoken.encoding_for_model(MODEL_NAME)
        # Tokenize the input text
        tokens = tokenizer.encode(text)
        logger.info(f"Token count: {len(tokens)}. Allowed: {max_tokens}")
        # Check if the token count exceeds the maximum allowed tokens
        if len(tokens) > max_tokens:
            # Calculate the number of tokens to remove
            tokens_to_remove = len(tokens) - max_tokens
            # Truncate the tokens from the end
            truncated_tokens = tokens[:-tokens_to_remove]
            # Decode the tokens back to a string
            truncated_text = tokenizer.decode(truncated_tokens)
            return truncated_text
        else:
            return text

    async def generate_queries(
        self, prompts: List[Prompt]
    ) -> List[tuple[Prompt, List[str]]]:
        """
        Generate multiple queries for each prompt
        :param prompts: List of prompts
        :return: List of tuples containing prompt and multi-query
        """

        queries = []

        async def process_prompt(prompt: Prompt):
            logger.info(
                f"Generating multi-query chunks through retriever invocation for prompt: {prompt.question}"
            )
            request = [
                (
                    "system",
                    self.MULTI_QUERY_ROLE,
                ),
                (
                    "human",
                    f"Original question: {prompt.question}.",
                ),
            ]
            result = await ThrottleRequest.athrottle_call(self.ainvoke, request)
            questions = [
                q.strip() for q in re.split(r"\d+\.\s+", result.content) if q.strip()
            ]
            questions.append(prompt.question)
            logger.info(
                f"Generated multi-queries for prompt: {prompt.question} \n{questions}"
            )
            queries.append((prompt, questions))

        tasks = [process_prompt(prompt) for prompt in prompts]
        await asyncio.gather(*tasks)
        return queries

    async def request(
        self,
        query: str,
        context: str = "",
        detail_level: Union[str, DetailLevel] = DetailLevel.LIGHT,
    ):
        """
        Request the LLM to answer a question
        :param query: Question to ask
        :param context: Context to provide
        :param detail_level: Level of detail
        :return: Answer to the question
        """

        if isinstance(detail_level, str):
            detail_level = DetailLevel.from_keyword(detail_level)

        logger.info("Checking if context exceeds max tokens. Truncating if required")
        context = await OrisonMessenger.truncate_to_max_tokens(context)
        logger.info(
            "Checking if context exceeds max tokens. Truncating if required...DONE"
        )
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
        result = await ThrottleRequest.athrottle_call(self.ainvoke, prompt)
        return result.content


class OrisonEmbeddings(OpenAIEmbeddings):
    def __init__(self, model: str, api_key: str, max_retries: int = 5):
        super().__init__(model=model, api_key=api_key, max_retries=max_retries)

    def embed_query(self, text: str) -> List[float]:
        return ThrottleRequest.throttle_call(super().embed_query, text)


class Summarize(RequestHandler):
    def __init__(self):
        super().__init__(str(self.__class__.__qualname__))
        ThrottleRequest.logger = self.logger

    def initialize(self, secrets):
        try:
            self.retriever_llm = OrisonMessenger(api_key=secrets.openai_api_key)
            self.prompter_llm = OrisonMessenger(api_key=secrets.openai_api_key)
        except Exception as e:
            message = f"Error initializing OrisonMessenger. Error: {e}"
            self.logger.error(message)
            raise LLM_INITIALIZATION_FAILED(message)

        try:
            # There is a bug in langchain Qdrant which checks for both regular client
            # and async client. It is not possible to use only async client.
            self.qdrant_client = QdrantClient(
                url=os.getenv("QDRANT_URL"),
                api_key=os.getenv("QDRANT_API_KEY"),
                port=6333,
                grpc_port=6333,
                https=True,
            )
            # Define the name of the collection
            collection_name = secrets.collection_name
            # ToDo: Include embedding as part of Postman
            # Use Postman in vectorization
            self.embedding = OrisonEmbeddings(
                model="text-embedding-ada-002",
                api_key=secrets.openai_api_key,
                max_retries=5,
            )
            self.vectordb = Qdrant(
                client=self.qdrant_client,
                collection_name=collection_name,
                embeddings=self.embedding,
            )
        except Exception as e:
            message = f"Error initializing Qdrant. Error: {e}"
            self.logger.error(message)
            raise QDrant_INITIALIZATION_FAILED(message)

        try:
            self.retriever = self.vectordb.as_retriever(search_kwargs={"k": 10})
        except Exception as e:
            message = f"Error initializing Retriever. Error: {e}"
            self.logger.error(message)
            raise Retriever_INITIALIZATION_FAILED(message)
        self._screening_client = ScreeningClient()

    @staticmethod
    def prompts(
        file_path: str = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "templates",
            "eb1_a_questionnaire.json",
        ),
    ) -> List[Prompt]:
        """
        Load prompts from a JSON file
        :param file_path: Path to the JSON file
        :return: List of prompts
        """

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

    async def retrieve_chunks(
        self, queries: List[tuple[Prompt, List[str]]]
    ) -> List[tuple[Prompt, List[Document]]]:
        prompt_docs = []

        async def process_query(prompt, multi_query):
            retrieved_docs = []
            async for query in async_generator_from_list(multi_query):
                # ToDo: Qdrant refuses connection so change this later.
                result = []
                # result = self.retriever.invoke(query)
                retrieved_docs.extend(result)
            prompt_docs.append((prompt, retrieved_docs))

        tasks = [process_query(prompt, multi_query) for prompt, multi_query in queries]
        await asyncio.gather(*tasks)
        return prompt_docs

    async def generate_story(
        self,
        prompt_docs: List[tuple[Prompt, List[Document]]],
        class_type: Union[ScreeningBuilder, StoryBuilder],
    ):
        story = class_type()

        async def process_result(prompt, retrieved_docs):
            context = "\n".join([doc.page_content for doc in retrieved_docs])
            source = "\n".join(
                [
                    f'Page: {doc.metadata["page"]} and Source:{doc.metadata["source"]}'
                    for doc in retrieved_docs
                ]
            )
            self.logger.info(
                f"Prompting llm with context for prompt: {prompt.question}"
            )
            response = await self.prompter_llm.request(
                prompt.question, context, prompt.detail_level
            )
            self.logger.info(
                f"Prompting llm with context for prompt: {prompt.question}....DONE"
            )
            qna = QandA(question=prompt.question, answer=response, source=source)
            story.summary.append(qna)

        tasks = [
            process_result(prompt, retrieved_docs)
            for prompt, retrieved_docs in prompt_docs
        ]
        await asyncio.gather(*tasks)
        return story

    async def summarize(self, prompts: List[Prompt]):
        self.logger.info("Generating queries for prompts")
        queries = await self.retriever_llm.generate_queries(prompts)
        self.logger.info("Generating queries for prompts...DONE")

        await asyncio.sleep(OPENAI_SLEEP * 5)

        self.logger.info("Retrieving chunks for prompts")
        prompt_docs = await self.retrieve_chunks(queries)
        self.logger.info("Retrieving chunks for prompts...DONE")

        await asyncio.sleep(OPENAI_SLEEP * 5)

        self.logger.info("Generating screening")
        screening = await self.generate_story(prompt_docs, class_type=ScreeningBuilder)
        self.logger.info("Generating screening...DONE")
        return screening

    async def handle_request(self, request_json):
        try:
            self.logger.info(f"Handling summarize request: {request_json}")
            attorney_id = request_json["attorneyId"]
            applicant_id = request_json["applicantId"]
            # ToDo: Use bucket with qdrant tag
            # bucket_name = request_json["bucket_name"]
            bucket_name = "research"  # Hardcoded for now
            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            self.logger.info("Initializing summarizer with secrets")
            self.initialize(secrets)
            prompts = self.prompts()
            self.logger.info("Initializing summarizer with secrets...done")
            screening = await self.summarize(prompts)
            screening.attorney_id = attorney_id
            screening.applicant_id = applicant_id
            screening.bucket_name = bucket_name
            self.logger.info("Storing screening in Firestore")
            id = await self._screening_client.insert(screening)
            self.logger.info(f"Screening stored in Firestore with ID: {id}")
        except Exception as e:
            message = f"Error processing files. Error code: {type(e).__name__}. Error message: {e}"
            self.logger.error(message, exc_info=True)
            return ErrorResponse(message)
        return OKResponse("Success!")


if __name__ == "__main__":
    request_json = {
        "attorneyId": "xlMsyQpatdNCTvgRfW4TcysSDgX2",
        "applicantId": "tYdtBdc7lJHyVCxquubj",
        "bucket_name": "research",
    }
    summarize = Summarize()
    asyncio.run(summarize.handle_request(request_json))
