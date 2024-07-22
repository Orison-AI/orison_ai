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
import numpy as np
import asyncio
import json
from or_store.firebase_storage import FirebaseStorage
from typing import Union, List
from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client import QdrantClient
from langchain_qdrant import Qdrant
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
from utils import async_generator_from_list, ThrottleRequest
from or_llm.openai_interface import (
    OrisonMessenger,
    OrisonEmbeddings,
    EMBEDDING_MODEL,
    Prompt,
)

RETRIEVAL_DOC_LIMIT = 10


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
            self.embedding = OrisonEmbeddings(
                model=EMBEDDING_MODEL,
                api_key=secrets.openai_api_key,
                max_retries=5,
            )
            self.vectordb = Qdrant(
                client=self.qdrant_client,
                collection_name=collection_name,
                embeddings=self.embedding,
                async_client=self.async_qdrant_client,
            )
        except Exception as e:
            message = f"Error initializing Qdrant. Error: {e}"
            self.logger.error(message)
            raise QDrant_INITIALIZATION_FAILED(message)

        try:
            self.retriever = self.vectordb.as_retriever(
                search_kwargs={"k": RETRIEVAL_DOC_LIMIT}
            )
        except Exception as e:
            message = f"Error initializing Retriever. Error: {e}"
            self.logger.error(message)
            raise Retriever_INITIALIZATION_FAILED(message)
        self._screening_client = ScreeningClient()

    @staticmethod
    async def _download_file(remote_file_path: str, local_file_path: str, logger):
        # Download file from Firebase Storage
        await FirebaseStorage.download_file(
            remote_file_path=remote_file_path, local_file_path=local_file_path
        )
        if os.path.exists(local_file_path):
            logger.debug(f"File written to {local_file_path}")
        else:
            logger.error(f"Could not download file to {local_file_path}")

    @staticmethod
    async def prompts(attorney_id: str, logger) -> List[Prompt]:
        """
        Load prompts from a JSON file
        :param file_path: Path to the JSON file
        :param logger: Logger object
        :return: List of prompts
        """

        firestore_file_path: str = os.path.join(
            "documents",
            "attorneys",
            attorney_id,
            "eb1_a_questionnaire.json",
        )
        local_path = "/tmp/eb1_a_questionnaire.json"
        await Summarize._download_file(firestore_file_path, local_path, logger)

        prompts = []
        with open(file=local_path, mode="r") as file:
            js = json.load(file)
            for question, detail_level in zip(
                js["question"],
                js["detail_level"],
            ):
                prompts.append(
                    Prompt(
                        question=question, detail_level=detail_level, tag=js["bucket"]
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
                result = await self.retriever.ainvoke(query)
                retrieved_docs.extend(result)
            prompt_docs.append((prompt, retrieved_docs))

        tasks = [process_query(prompt, multi_query) for prompt, multi_query in queries]
        await asyncio.gather(*tasks)
        return prompt_docs

    @staticmethod
    def dict_to_string(dict: dict[str, list]) -> str:
        # Create a list of key-value pairs formatted as "key: [values]"
        pairs = [
            f"{key}. Pages: [{', '.join(map(str, np.array(np.unique(values), dtype=int)))}]"
            for key, values in dict.items()
        ]
        # Join the pairs with " and "
        result = " and ".join(pairs)
        return result

    async def generate_story(
        self,
        prompt_docs: List[tuple[Prompt, List[Document]]],
        class_type: Union[ScreeningBuilder, StoryBuilder],
    ):
        story = class_type()

        async def process_result(prompt, retrieved_docs):
            context = "\n".join([doc.page_content for doc in retrieved_docs])
            source = {}
            for doc in retrieved_docs:
                if doc.metadata["source"] not in source:
                    source[doc.metadata["source"]] = []
                source[doc.metadata["source"]].append(doc.metadata["page"])
            source = Summarize.dict_to_string(source)
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

        self.logger.info("Retrieving chunks for prompts")
        prompt_docs = await self.retrieve_chunks(queries)
        self.logger.info("Retrieving chunks for prompts...DONE")

        self.logger.info("Generating screening")
        screening = await self.generate_story(prompt_docs, class_type=ScreeningBuilder)
        self.logger.info("Generating screening...DONE")
        return screening

    async def handle_request(self, request_json):
        try:
            self.logger.info(f"Handling summarize request: {request_json}")
            attorney_id = request_json["attorneyId"]
            applicant_id = request_json["applicantId"]
            secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
            self.logger.info("Initializing summarizer with secrets")
            self.initialize(secrets)
            prompts = await self.prompts(attorney_id=attorney_id, logger=self.logger)
            self.logger.info("Initializing summarizer with secrets...done")
            screening = await self.summarize(prompts)
            screening.attorney_id = attorney_id
            screening.applicant_id = applicant_id
            self.logger.info("Storing screening in Firestore")
            id = await self._screening_client.insert(
                attorney_id=attorney_id, applicant_id=applicant_id, doc=screening
            )
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
    }
    summarize = Summarize()
    asyncio.run(summarize.handle_request(request_json))
