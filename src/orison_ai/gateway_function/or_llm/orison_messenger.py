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
from collections import defaultdict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
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
from typing import Annotated
from typing_extensions import TypedDict, Dict
from langgraph.graph import StateGraph, START, END, MessagesState

# Internal

from or_store.models import QandA
from or_store.firebase import OrisonSecrets
from exceptions import (
    LLM_INITIALIZATION_FAILED,
    RateLimiter_INITIALIZATION_FAILED,
    QDrant_INITIALIZATION_FAILED,
)
from or_store.db_interfaces import ChatMemoryClient, FirestoreLangGraph


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "gpt-4-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"
RETRIEVAL_DOC_LIMIT = 10
CHAT_HISTORY_LIMIT = 10


@dataclass
class Prompt:
    question: list
    detail_level: str
    tag: Union[list, str] = None  # vector DB tag
    filename: Union[list, str] = None  # vector DB filename
    id: str = uuid.uuid4().hex
    # Used if memory is True
    applicant_id: str = None
    attorney_id: str = None


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
        memory_window_size: int = CHAT_HISTORY_LIMIT,
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
            graph_builder = StateGraph(MessagesState)
            self._system_prompt = ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate.from_template(self.ROLE),
                    MessagesPlaceholder(variable_name="chat_history"),
                    HumanMessagePromptTemplate.from_template("{text}"),
                ]
            )
            self._chat_bot = ChatOpenAI(
                api_key=secrets.openai_api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=90.0,
                rate_limiter=self._rate_limiter,
                streaming=True,
                **kwargs,
            )
            parser = StrOutputParser()

            async def prompt_node(state: MessagesState) -> MessagesState:
                input_text = state["messages"][-1]["user"] if state["messages"] else ""
                # Prepare prompt using system prompt template
                prompt = self._system_prompt.format(
                    text=input_text, chat_history=state["messages"]
                )
                return state

            async def chatbot_node(state: MessagesState) -> MessagesState:
                prompt = None
                input_text = ""
                # Get response from LLM
                response = await self._chat_bot.ainvoke(
                    {"messages": prompt["messages"]}
                )
                parsed_response = parser.parse(response)
                # Append user input and assistant response to messages
                state["messages"].append(
                    {"user": input_text, "assistant": parsed_response}
                )
                return state

            graph_builder.add_node("chatbot", chatbot_node)
            graph_builder.add_edge(START, "chatbot")
            graph_builder.add_edge("chatbot", END)
            self._graph = graph_builder.compile()
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
    def dict_to_string(ip_dict: dict[str, list]) -> str:
        """
        Convert a dictionary to a string
        :param dict: Dictionary
        :return: String representation of the dictionary
        """

        # Create a list of key-value pairs formatted as "key: [values]"
        pairs = [
            (
                f"{key}. Pages: [{', '.join(map(str, np.array(np.unique(values), dtype=int)))}]"
                if "unknown" not in values
                else f"{key}: Pages: unknown"
            )
            for key, values in ip_dict.items()
        ]
        # Join the pairs with " and "
        result = " and ".join(pairs)
        return result

    async def _prepare_request(self, prompt: Prompt):
        """
        Shared setup for both streaming and non-streaming requests.
        """
        query = prompt.question
        detail_level = prompt.detail_level
        filter_conditions = []

        # Filtering logic
        if prompt.tag:
            filter_conditions.append(
                models.FieldCondition(
                    key="tag",
                    match=models.MatchAny(
                        any=[tag_name.lower() for tag_name in prompt.tag]
                    ),
                )
            )
        if prompt.filename:
            filter_conditions.append(
                models.FieldCondition(
                    key="filename",
                    match=models.MatchAny(
                        any=[filename for filename in prompt.filename]
                    ),
                )
            )

        filter = models.Filter(should=filter_conditions) if filter_conditions else None

        # Retriever setup
        retriever = MultiQueryRetriever.from_llm(
            retriever=self.vectordb.as_retriever(
                search_kwargs={"k": RETRIEVAL_DOC_LIMIT, "filter": filter},
            ),
            llm=self._chat_bot,
        )

        # Fetch documents and format context
        retrieved_docs = await retriever.ainvoke(query)
        context = "\n".join([doc.page_content for doc in retrieved_docs])
        source = defaultdict(list)
        for doc in retrieved_docs:
            source[doc.metadata.get("source", "unknown")].append(
                doc.metadata.get("page", "unknown")
            )
        source = self.dict_to_string(source)
        context = await OrisonMessenger.truncate_to_max_tokens(context)

        text = f"Given the context: \n{context}, \n answer the following: {query} in {detail_level.value}."

        return query, detail_level, text, source

    async def _load_memory_into_buffer(self, prompt: Prompt):
        """
        Load the memory into the buffer if required.
        """
        await self.chat_memory_client.load_memory_into_buffer(
            memory_buffer=self.memory,
            applicant_id=prompt.applicant_id,
            attorney_id=prompt.attorney_id,
            window_size=CHAT_HISTORY_LIMIT,
        )

    async def _save_to_memory(self, prompt: Prompt, query: str, response: str):
        """
        Save the query and response to memory if required.
        """
        await self.memory.asave_context(
            inputs={"question": query}, outputs={"answer": response}
        )
        await self.chat_memory_client.update_memory(
            applicant_id=prompt.applicant_id,
            attorney_id=prompt.attorney_id,
            user_message=query,
            assistant_response=response,
            window_size=CHAT_HISTORY_LIMIT,
        )

    async def request(
        self,
        prompt: Prompt,
        use_memory: bool = False,
    ):
        """
        Non-streaming request for the LLM to answer a question.
        :param prompt: Prompt object
        :param use_memory: Use memory to store the context
        :return: Answer to the question
        :rtype: QandA
        """

        # if use_memory:
        #     await self._load_memory_into_buffer(prompt)
        # Call a shared helper function to set up common parameters
        query, _, text, source = await self._prepare_request(prompt)
        # Non-streaming response
        messages = MessagesState(messages=[])
        chain_response = await self._graph.ainvoke(messages)
        response = chain_response["messages"][-1]["assistant"]
        # Optional memory handling
        # if use_memory:
        #     await self._save_to_memory(prompt, query, response)
        return QandA(question=prompt.question, answer=response, source=source)

    async def stream_request(
        self,
        prompt: Prompt,
        use_memory: bool = False,
    ):
        """
        Streaming request for the LLM to answer a question.
        :param prompt: Prompt object
        :param use_memory: Use memory to store the context
        :yield: Chunked responses as QandA objects
        """

        if use_memory:
            await self._load_memory_into_buffer(prompt)
        # Call the same shared helper function to set up common parameters
        query, _, text, source = await self._prepare_request(prompt)
        response = ""
        # Streaming response
        async for chunk in self._system_chain.astream({"text": text}):
            print("@@@@@")
            response += chunk.get("text")
            yield QandA(question=prompt.question, answer=response, source=source)

        # Optional memory handling
        if use_memory:
            await self._save_to_memory(
                prompt,
                query,
                response,
            )
