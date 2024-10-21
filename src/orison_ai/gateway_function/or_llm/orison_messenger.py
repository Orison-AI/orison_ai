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

import uuid
import numpy as np
import logging
import tiktoken
from typing import Union
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain.retrievers.multi_query import MultiQueryRetriever
from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client import QdrantClient
from langchain_qdrant import Qdrant
from langchain_openai import OpenAIEmbeddings
from dataclasses import dataclass
from enum import Enum
from qdrant_client.http import models

# Internal

from or_store.models import QandA
from or_store.firebase import OrisonSecrets
from exceptions import (
    LLM_INITIALIZATION_FAILED,
    RateLimiter_INITIALIZATION_FAILED,
    QDrant_INITIALIZATION_FAILED,
    Retriever_INITIALIZATION_FAILED,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "gpt-4-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"
RETRIEVAL_DOC_LIMIT = 10


@dataclass
class Prompt:
    question: list
    detail_level: str
    tag: Union[list, str]  # vector DB tag
    filename: Union[list, str]  # vector DB filename
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


class OrisonEmbeddings(OpenAIEmbeddings):
    rate_limiter: InMemoryRateLimiter

    class Config:
        # Allow arbitrary types like InMemoryRateLimiter to be used
        arbitrary_types_allowed = True

    def embed_query(self, text: str):
        try:
            token_acquired = True
            if self.rate_limiter:
                token_acquired = self.rate_limiter.acquire()
            if token_acquired:
                embeddings = super().embed_query(text)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to get embeddings for text: {text}. Error: {e}")
            raise e

    async def aembed_query(self, text: str):
        try:
            token_acquired = True
            if self.rate_limiter:
                token_acquired = await self.rate_limiter.aacquire()
            if token_acquired:
                embeddings = await super().aembed_query(text)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to get embeddings for text: {text}. Error: {e}")
            raise e


class OrisonMessenger:
    ROLE = """
    You are a helpful, respectful and honest assistant.\
    Always answer as helpfully as possible and follow ALL given instructions.\
    Do not speculate or make up information.\
    Use bullet points to list multiple items using numbers.\
    Break your response into paragraphs for better readability.\
    """

    def __init__(
        self,
        secrets: OrisonSecrets,
        model: str = MODEL_NAME,
        embedding_model: str = EMBEDDING_MODEL,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        max_retries: int = 5,
        **kwargs,
    ):
        try:
            self._rate_limiter = InMemoryRateLimiter(
                requests_per_second=7,  # Value which throttles the requests
                check_every_n_seconds=0.1,
                max_bucket_size=1,  # Controls the maximum burst size. We don't want to allow burst requests.
            )
        except Exception as e:
            raise RateLimiter_INITIALIZATION_FAILED(exception=e)

        try:
            self._system_prompt = ChatPromptTemplate(
                messages=[("system", self.ROLE), ("user", "{text}")]
            )
            self._chat_bot = ChatOpenAI(
                api_key=secrets.openai_api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=90.0,
                rate_limiter=self._rate_limiter,
                **kwargs,
            )
            self._parser = StrOutputParser()
            self._system_chain = self._system_prompt | self._chat_bot | self._parser
            self._embeddings = OrisonEmbeddings(
                model=embedding_model,
                api_key=secrets.openai_api_key,
                max_retries=max_retries,
                rate_limiter=self._rate_limiter,
            )
            self._tokenizer = tiktoken.encoding_for_model(MODEL_NAME)
            self._tokenizer_model_name = MODEL_NAME
            self._embedding_model_name = EMBEDDING_MODEL
        except Exception as e:
            raise LLM_INITIALIZATION_FAILED(exception=e)

        try:
            # There is a bug in langchain Qdrant which checks for both regular client
            # and async client. It is not possible to use only async client.
            self.qdrant_client = QdrantClient(
                url=secrets.qdrant_url,
                api_key=secrets.qdrant_api_key,
                port=6333,
                grpc_port=6333,
                https=True,
                timeout=10.0,
            )
            self.async_qdrant_client = AsyncQdrantClient(
                url=secrets.qdrant_url,
                api_key=secrets.qdrant_api_key,
                port=6333,
                grpc_port=6333,
                https=True,
                timeout=10.0,
            )
            # Define the name of the collection
            collection_name = secrets.collection_name
            self.vectordb = Qdrant(
                client=self.qdrant_client,
                collection_name=collection_name,
                embeddings=self._embeddings,
                async_client=self.async_qdrant_client,
            )
        except Exception as e:
            raise QDrant_INITIALIZATION_FAILED(exception=e)

    @staticmethod
    def number_tokens(text: str) -> int:
        """
        Calculate the number of tokens in the input text
        :param text: Input text
        :return: Number of tokens
        """
        # Initialize the tokenizer for the specific model
        tokenizer = tiktoken.encoding_for_model(MODEL_NAME)
        # Tokenize the input text
        tokens = tokenizer.encode(text)
        return len(tokens)

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

    @staticmethod
    def dict_to_string(dict: dict[str, list]) -> str:
        """
        Convert a dictionary to a string
        :param dict: Dictionary
        :return: String representation of the dictionary
        """

        # Create a list of key-value pairs formatted as "key: [values]"
        pairs = [
            f"{key}. Pages: [{', '.join(map(str, np.array(np.unique(values), dtype=int)))}]"
            for key, values in dict.items()
        ]
        # Join the pairs with " and "
        result = " and ".join(pairs)
        return result

    async def request(
        self,
        prompt: Prompt,
    ):
        """
        Request the LLM to answer a question
        :param prompt: Prompt object
        :return: Answer to the question
        :rtype: QandA
        """

        query = prompt.question
        detail_level = prompt.detail_level
        filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="tag",
                    match=models.MatchAny(
                        any=[tag_name.lower() for tag_name in prompt.tag]
                    ),
                ),
                models.FieldCondition(
                    key="filename",
                    match=models.MatchAny(
                        any=[filename.lower() for filename in prompt.filename]
                    ),
                ),
            ],
        )
        try:
            retriever = MultiQueryRetriever.from_llm(
                retriever=self.vectordb.as_retriever(
                    search_kwargs={"k": RETRIEVAL_DOC_LIMIT, "filter": filter},
                ),
                llm=self._chat_bot,
            )
        except Exception as e:
            raise Retriever_INITIALIZATION_FAILED(exception=e)

        if isinstance(detail_level, str):
            detail_level = DetailLevel.from_keyword(detail_level)

        retrieved_docs = await retriever.ainvoke(query)
        logger.info(
            f"Retrieved {len(retrieved_docs)} documents from the query: {query}"
        )
        context = "\n".join([doc.page_content for doc in retrieved_docs])
        source = {}
        for doc in retrieved_docs:
            if doc.metadata["source"] not in source:
                source[doc.metadata["source"]] = []
            source[doc.metadata["source"]].append(doc.metadata["page"])
        source = self.dict_to_string(source)

        logger.info("Checking if context exceeds max tokens. Truncating if required")
        context = await OrisonMessenger.truncate_to_max_tokens(context)
        logger.info(
            "Checking if context exceeds max tokens. Truncating if required...DONE"
        )
        text = f"Given the context: \n{context}, \n answer the following: {query} in {detail_level.value}."
        response = await self._system_chain.ainvoke(text)
        return QandA(question=prompt.question, answer=response, source=source)
