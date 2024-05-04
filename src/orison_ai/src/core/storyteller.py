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

import os.path
import json
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.settings import Settings
from collections import defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

Settings.chunk_size = 6144
Settings.chunk_overlap = 1024
Settings.context_window = 11700
Settings.num_output = 4096


class StoryTeller:
    def __init__(self):
        self._query_engine = None

    def _get_response(self, key, indexes, prompt_template):
        index = indexes[prompt_template["prompt"][key]["index"]]
        self._query_engine = index.as_query_engine()
        response = "\n\n"
        for question in prompt_template["prompt"][key]["question"]:
            query = question + prompt_template["prompt"][key]["postscript"]
            response = "\n\n".join(
                [response, query, self._query_engine.query(query).response]
            )
        response = response + "\n"
        return response

    def summarize(self, indexes, prompt_template):
        response = ""
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self._get_response, key, indexes, prompt_template)
                for key in prompt_template["prompt"]
            ]
            for future in as_completed(futures):
                try:
                    result = future.result()
                except Exception as exc:
                    print(f"Error loading response: {exc}")
                else:
                    response = "\n".join([response, result])
        return response
