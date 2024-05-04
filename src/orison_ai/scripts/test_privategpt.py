#! /usr/bin/env python3.9

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

from orison_ai.src.core.storyteller import StoryTeller
from orison_ai.src.utils.constants import CATEGORIES, VAULT_PATH
from orison_ai.src.utils.ingest_utils import ingest_folder, Source
from orison_ai.src.database.mongo import MongoDB
from private_gpt.components.ingest.ingest_component import PipelineIngestComponent
from private_gpt.server.ingest.ingest_service import IngestService
from private_gpt.components.llm.llm_component import LLMComponent
from private_gpt.components.vector_store.vector_store_component import (
    VectorStoreComponent,
)
from private_gpt.components.node_store.node_store_component import NodeStoreComponent
from private_gpt.components.embedding.embedding_component import EmbeddingComponent
from private_gpt.di import global_injector
from private_gpt.settings.settings import Settings
from private_gpt.server.chunks.chunks_service import ChunksService, ContextFilter
import logging
import json
import os
from pathlib import Path
from IPython import embed
from openai import OpenAI
from collections import defaultdict

client = OpenAI()
mongo_client = MongoDB("orison_db", "demo_v1")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RESEARCH_PATH = Path(os.path.join(VAULT_PATH, "research"))
ROLE = """\
    You are a helpful, respectful and honest assistant. \
    Always answer as helpfully as possible and follow ALL given instructions. \
    Do not speculate or make up information. \
    """

if __name__ == "__main__":
    """
    NOTES:
    check ui.py
    IngestService uses settings to configure ingest_mode and worker count
    ingest service can upload, check if doc exists, delete and replace doc, etc
    Use ingest service instance for everything related to documents
    They are using some kind of python injectory mechanism to get Settings class anywhere
    One of the observations made is that AI got severly confused with so much data on other awards
    and research that it actually rated those chunks higher
    """
    logger.info("Initializing story teller")
    story_teller = StoryTeller()
    settings = global_injector.get(Settings)
    logger.info(f"Settings obtained: {settings}")

    llm_component = LLMComponent(settings=settings)
    vector_store_component = VectorStoreComponent(settings=settings)
    node_store_component = NodeStoreComponent(settings=settings)
    embedding_component = EmbeddingComponent(settings=settings)
    # ingest_service = IngestService(
    #     llm_component=llm_component,
    #     vector_store_component=vector_store_component,
    #     node_store_component=node_store_component,
    #     embedding_component=embedding_component,
    # )
    # ingest_folder(
    #     RESEARCH_PATH,
    #     ignored=["private_gpt", "private_gpt.zip"],
    #     ingest_service=ingest_service,
    # )

    chunks_service = ChunksService(
        llm_component=llm_component,
        vector_store_component=vector_store_component,
        embedding_component=embedding_component,
        node_store_component=node_store_component,
    )
    from IPython import embed

    embed()

    with open("/app/templates/prompts.json") as file:
        js = json.load(file)
        questions = js["prompt"]["research"]["question"]
        detail_number = js["prompt"]["research"]["detail_number"]
        file.close()

    summary_dict = defaultdict()
    for i, message in enumerate(questions):
        response = chunks_service.retrieve_relevant(
            text=message, limit=detail_number[i], prev_next_chunks=6
        )

        sources = Source.curate_sources(response)

        context = "\n".join(
            f"{source.text}" for index, source in enumerate(sources, start=1)
        )
        prompt = f"Given the context: \n{context}, \n answer the following: {message}"

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

        source_list = []
        logger.info("Sources from:")
        for index, source in enumerate(sources, start=1):
            source_info = f"{index}. **{source.file} " f"(page {source.page})**"
            source_list.append(source_info)
            logger.info(source_info)
        chat_response = completion.choices[0].message.content
        logger.info(f"\nQuestion: {message}. \nResponse:\n {chat_response}")
        summary_dict[message] = f'{chat_response}\n\n{" | ".join(source_list)}'

    mongo_client.insert_data({"Summary": summary_dict})
    # embed()
