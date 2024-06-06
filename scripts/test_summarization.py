from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant

# Set logging for the queries
import logging
import json

logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

import numpy as np
from openai import OpenAI

ROLE = """\
    You are a helpful, respectful and honest assistant. \
    Always answer as helpfully as possible and follow ALL given instructions. \
    Do not speculate or make up information. \
    """

client = OpenAI(api_key="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")
# Initialize Qdrant client
qdrant_client = QdrantClient(
    url="https://e3cab25a-ad09-4bdd-a2bd-720b5f920bf1.us-east4-0.gcp.cloud.qdrant.io",
    api_key="av5ELn6DMe66WLg8wH8LYk4FDPxUTDrPf24FJ4WhurCu9vAVjRtLtA",
)

# Define the name of the collection
collection_name = "orison_vdb"


# Function to get embeddings from OpenAI
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
    retriever=vectordb.as_retriever(search_typ="mmr", search_kwargs={"k": 10}),
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
    print(response.content)
    print("\n\n")


from IPython import embed

embed()


# vector_set = []
# chunks = []
# # Get embedding for the query
# for query_text in queries:
#     query_embedding = get_openai_embedding(query_text)
#     # Search for the most relevant chunks
#     search_results = qdrant_client.search(
#         collection_name=collection_name,
#         query_vector=query_embedding,
#         limit=10,  # Number of top results to retrieve
#     )
#     # Display the results
#     for result in search_results:
#         print(f"Score: {result.score}, Chunk: {result.payload['page_content']}")
