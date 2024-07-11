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

import re
import asyncio
import uuid
import logging
import tiktoken
from typing import Union, List
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from utils import ThrottleRequest
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "gpt-4-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"


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
    Use bullet points to list multiple items using numbers.\
    Break your response into paragraphs for better readability.\
    """

    MULTI_QUERY_ROLE = """
    You are an AI language model assistant. \
    Your task is to generate 5 different versions of the given user question. \
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
    async def number_tokens(text: str) -> int:
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
