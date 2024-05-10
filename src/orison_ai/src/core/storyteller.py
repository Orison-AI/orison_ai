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

from orison_ai.src.utils.constants import VAULT_PATH, ROLE, DB_NAME
from orison_ai.src.utils.ingest_utils import ingest_folder, Source
from orison_ai.src.database.story_client import StoryClient
from orison_ai.src.database.models import Story, QandA
from private_gpt.server.ingest.ingest_service import IngestService
from private_gpt.components.llm.llm_component import LLMComponent
from private_gpt.components.vector_store.vector_store_component import (
    VectorStoreComponent,
)
from private_gpt.components.node_store.node_store_component import NodeStoreComponent
from private_gpt.components.embedding.embedding_component import EmbeddingComponent
from private_gpt.di import global_injector
from private_gpt.settings.settings import Settings
from private_gpt.server.chunks.chunks_service import ChunksService
import logging
import json
import os
import asyncio
from pathlib import Path
from openai import OpenAI

client = OpenAI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ingest_documents(path: Path):
    """
    Ingest the documents from the path
    :param path: the path to the documents
    """
    logger.info(f"Ingesting documents from {path}")
    settings = global_injector.get(Settings)
    logger.info(f"Settings obtained: {settings}")
    llm_component = LLMComponent(settings=settings)
    vector_store_component = VectorStoreComponent(settings=settings)
    node_store_component = NodeStoreComponent(settings=settings)
    embedding_component = EmbeddingComponent(settings=settings)

    ingest_service = IngestService(
        llm_component=llm_component,
        vector_store_component=vector_store_component,
        node_store_component=node_store_component,
        embedding_component=embedding_component,
    )
    ingest_folder(
        path,
        ignored=["private_gpt", "private_gpt.zip"],
        ingest_service=ingest_service,
    )


async def analyze_documents(business_id: str, user_id: str, type_of_story: str):
    """
    Analyze the documents and generate a story
    :param business_id: the business id
    :param user_id: the user id
    :param type_of_story: the type of story
    :return: None
    """
    settings = global_injector.get(Settings)
    logger.info(f"Settings obtained: {settings}")

    story_client = StoryClient(db_name=DB_NAME)
    llm_component = LLMComponent(settings=settings)
    vector_store_component = VectorStoreComponent(settings=settings)
    node_store_component = NodeStoreComponent(settings=settings)
    embedding_component = EmbeddingComponent(settings=settings)

    chunks_service = ChunksService(
        llm_component=llm_component,
        vector_store_component=vector_store_component,
        embedding_component=embedding_component,
        node_store_component=node_store_component,
    )

    with open("/app/templates/prompts.json") as file:
        js = json.load(file)
        questions = js["prompt"]["research"]["question"]
        detail_number = js["prompt"]["research"]["detail_number"]
        file.close()

    async def get_response(message, limit):
        response = chunks_service.retrieve_relevant(
            text=message, limit=limit, prev_next_chunks=6
        )

        sources = Source.curate_sources(response)

        context = "\n".join(
            f"{source.text}" for index, source in enumerate(sources, start=1)
        )
        prompt = f"Given the context: \n{context}, \n Answer the following: {message}"

        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": ROLE,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        source_info = ""
        logger.info("Sources from:")
        for index, source in enumerate(sources, start=1):
            source_info = "\n".join(
                [
                    source_info,
                    f"{index}. **{source.file} " f"(page {source.page})**",
                ]
            )
        chat_response = completion.choices[0].message.content
        logger.info(
            f"\nQuestion: {message}. \nResponse:\n {chat_response}\n Sources: {source_info}"
        )
        q_and_a = QandA(question=message, answer=chat_response, source=source_info)
        return q_and_a

    async def get_story(questions, detail_number):
        story = Story()
        tasks = [
            asyncio.create_task(get_response(message, detail_number[i]))
            for i, message in enumerate(questions)
        ]
        for task in asyncio.as_completed(tasks):
            q_and_a = await task
            story.summary.append(q_and_a)
        return story

    story = await get_story(questions, detail_number)
    story.business_id = business_id
    story.user_id = user_id
    story.type_of_story = type_of_story
    await story_client.insert(story)


if __name__ == "__main__":
    RESEARCH_PATH = Path(os.path.join(VAULT_PATH, "research"))
    asyncio.run(ingest_documents(RESEARCH_PATH))
    asyncio.run(analyze_documents("detailed"))
