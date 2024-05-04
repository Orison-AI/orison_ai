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
from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.core.query_engine.retriever_query_engine import (
    RetrieverQueryEngine,
)
from collections import defaultdict
from openai import OpenAI

PERSIST_DIR = "/app/vault/research/"

with open("/app/templates/prompts.json") as file:
    questions = json.load(file)["prompt"]["research"]["question"]
    file.close()

storage_dir = os.path.join(PERSIST_DIR, "vector")
if not os.path.exists(storage_dir):
    documents = SimpleDirectoryReader(PERSIST_DIR).load_data()
    index = VectorStoreIndex.from_documents(documents)
    # store it for later
    index.storage_context.persist(persist_dir=storage_dir)
else:
    # load the existing index
    storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
    index = load_index_from_storage(storage_context)

retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=10,
)
# nodes = retriever.retrieve(questions[0])

# from IPython import embed

# embed()

query_engine = RetrieverQueryEngine(retriever)


def log_query(query_engine, query):
    print(query)
    print("\n")
    response = query_engine.query(query)
    print(response)
    print("\n\n")


for query in questions:
    log_query(query_engine, query)


"""
Screwed up response

The candidate has received the Academic Excellence Award in the Department of Astronautical Engineering and the Rocket Scientist of the Year award in the Department of Biomedical Engineering.


The publications associated with the mentioned candidates are related to student awards and achievements in various engineering departments. These publications highlight the outstanding achievements of students in fields such as electrical engineering, industrial and systems engineering, mechanical engineering, and chemical engineering. The papers detail the recognition received by students for their exceptional performance and contributions in their respective areas of study.


The candidate has published content on the ROS-I blog, specifically related to ICRA (International Conference on Robotics and Automation). The content highlights the ICRA event held on June 20, 2019, in Montreal, Canada. The candidate has associations with ROS-Industrial and has contributed content for publication on the ROS-I blog related to ICRA.


The candidate has evidence of significant contributions to the industry through projects involving the evaluation of international competitiveness at the industry level, the evaluation of the competitiveness of the South African agribusiness sector, and the development of new compacts for Canadian competitiveness. These projects demonstrate the candidate's involvement in assessing and enhancing the competitive positions of various sectors within the industry. The impact of the candidate's work can be seen in the scalability of their evaluations, which can be applied across different industries to improve competitiveness and performance. The candidate's contributions have relevance not only in the sectors directly studied but also in related industries where competitiveness and performance evaluation are crucial for success.
"""


"""
Better response: Cost: $0.01
The candidate has evidence of receiving lesser nationally or internationally recognized prizes or awards for excellence based on the following details:

1. Angela Merkel, Chancellor of Germany, walked past the candidate's booth at an event.
2. Visitors were present at the candidate's booth at Hannover Messe.
3. The candidate's picture was taken at an awards ceremony.
4. The candidate attended the 2018 Viterbi Master's Student Awards dinner and was part of the event.



I'm sorry, but based on the provided context information, I am unable to list the publications or provide detailed summaries of the papers as the context does not contain any specific publication titles or abstracts.



The candidate has publications associated with the following publishers:
1. University of Southern California

The candidate has published papers in the following conferences or events:
1. Additive Manufacturing - November 2019



The candidate's evidence of original scientific, scholarly, artistic, athletic, or business-related contributions of major significance to the field in the industry includes:

1. Development of a pioneering method for automating the composite prepreg layup process in composites manufacturing, which was a significant contribution to the industry.
2. Invention of a groundbreaking method that automates the layup process, making it more efficient, cost-effective, and time-saving.
3. Rigorous research on motion planning and coordination of a multi-robot setup for manipulating and forming viscoelastic prepreg sheets, showcasing innovation in the field.
4. Publication of work in Robotics and Computer-Integrated Manufacturing, leading to a patent application filed by the University of Southern California.
5. Impactful results in attracting funding from organizations like the National Science Foundation and Advanced Robotics for Manufacturing, demonstrating the practical application and scalability of the candidate's work.
6. Opening doors for the aerospace industry to implement robotics in composite manufacturing, indicating cross-industry applicability and potential for growth.
7. The aerospace industry, currently worth $66 billion and expected to grow to $130 billion by 2024, is one of the industries benefiting from the candidate's work, showcasing the broad impact and scalability of the contributions.
"""
