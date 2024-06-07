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

"""
Setup these env vars before use
OPENAI_API_KEY
QDRANT_URL
QDRANT_API_KEY
"""

from qdrant_client import QdrantClient
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import Qdrant

# Set logging for the queries
import logging
import json
import os

logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

import numpy as np
from openai import OpenAI

ROLE = """\
    You are a helpful, respectful and honest assistant. \
    Always answer as helpfully as possible and follow ALL given instructions. \
    Do not speculate or make up information. \
    """

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

# Define the name of the collection
collection_name = "orison_vdb"


# Function to get embeddings from OpenAI
# ToDo: We should evaluate langchain embeddings instead. They should be identical
def get_openai_embedding(text):
    response = client.embeddings.create(
        input=[text], model="text-embedding-ada-002"
    )  # Use the appropriate OpenAI model)
    return response.data[0].embedding


# VectorDB
embedding = OpenAIEmbeddings(model="text-embedding-ada-002")
vectordb = Qdrant(
    client=qdrant_client,
    collection_name=collection_name,
    embeddings=embedding,
)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, max_tokens=4096)
retriever = MultiQueryRetriever.from_llm(
    # retriever=vectordb.as_retriever(
    #     search_type="mmr", search_kwargs={"k": 10, "fetch_k": 50}
    # ),
    retriever=vectordb.as_retriever(search_kwargs={"k": 10}),
    llm=llm,
    include_original=True,
)

# Example query and its perspectives
query = "Overall, what impact does the research/work have and why is it necessary in their field? For example, is there a problem you are trying to solve? Please provide facts and specific examples as applicable."
perspectives = [
    "What are the main contributions of Rishi Malhan's research in their field?",
    "How has Rishi Malhan's work impacted their field of study?",
    "What specific problem is Rishi Malhan's research addressing?",
    "Why is Rishi Malhan's research necessary in their field?",
    "Can you provide examples of how Rishi Malhan's research has been applied in real-world scenarios?",
    "What innovative solutions has Rishi Malhan proposed in their research?",
    "In what ways has Rishi Malhan's work advanced their field?",
    "What are the significant outcomes of Rishi Malhan's research?",
    "Why is Rishi Malhan's research considered significant in their domain?",
    "Are there any case studies or factual examples illustrating the impact of Rishi Malhan's work?",
]

with open("/app/templates/eb1_a_questionnaire.json") as file:
    js = json.load(file)
    questions = js["prompt"]["research"]["question"]
    detail_level = js["prompt"]["research"]["detail_level"]
    file.close()

for i, message in enumerate(questions):
    retrieved_docs = retriever.invoke(message)
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    # ToDo: Check that context is within openAI limits and accordingly reduce it.
    prompt = [
        (
            "system",
            ROLE,
        ),
        (
            "human",
            f"Given the context: \n{context}, \n answer the following: {message} in {detail_level[i]}.",
        ),
    ]
    response = llm.invoke(prompt)
    # We need mapping from source chunk to the response generated
    # To begin with aggregate all sources from chunks
    # All this gets dumped into or_store.models.ScreeningBuilder for screening
    print(response.content)
    print("\n\n")


from IPython import embed

embed()
