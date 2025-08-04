#! /usr/bin/env python3.11

# ==========================================================================
#  Copyright (c) Orison AI, 2025.
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

# Disable LangSmith before any imports
import os
import warnings

# Suppress LangSmith warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langsmith")
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGCHAIN_PROJECT"] = ""
os.environ["LANGCHAIN_TRACING"] = "false"
os.environ["LANGCHAIN_SESSION"] = ""
os.environ["LANGCHAIN_DISABLE_TRACING"] = "true"

# External

import asyncio
import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, END

# Internal

from workflows.base import BaseWorkflow, WorkflowState
from workflows.models import Prompt
from database.firestore_clients import GoogleScholarClient, ScreeningClient
from database.firebase_config import FireStoreDB
from database.schema import ScreeningBuilder
from core.environment import get_env
from core.config import VectorConfig, LLMConfig, AppConfig
from database.secrets import OrisonSecrets
from core.client import LLMClient
from storage.vector_store import VectorStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Disable langsmith logging
logging.getLogger("langsmith").setLevel(logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)


class SummarizeWorkflow(BaseWorkflow):
    """Enhanced LangGraph workflow for questionnaire summarization with PDF and Scholar data integration"""

    def __init__(self):
        """Initialize the workflow - actual initialization happens when IDs are provided"""
        self.graph = None
        self.attorney_id = None
        self.applicant_id = None
        self.llm_client = None
        self.vector_store = None
        self.scholar_client = None
        self.screening_client = None

    def _initialize(self, attorney_id: str, applicant_id: str):
        """Initialize all components with proper attorney/applicant IDs"""
        self.attorney_id = attorney_id
        self.applicant_id = applicant_id

        env = get_env()

        # Create collection name using the same pattern as the API router
        collection_name = f"{attorney_id}_{applicant_id}"

        config = VectorConfig(
            collection_name=collection_name,
            url=env.qdrant_url,
            api_key=env.qdrant_api_key,
        )

        secrets = OrisonSecrets(
            openai_api_key=env.openai_api_key,
            qdrant_url=env.qdrant_url,
            qdrant_api_key=env.qdrant_api_key,
            collection_name=config.collection_name,
        )

        # Initialize components
        llm_config = LLMConfig()
        app_config = AppConfig()
        self.llm_client = LLMClient(secrets, llm_config, app_config)
        self.vector_store = VectorStore(config, self.llm_client)

        # Initialize base class
        super().__init__(self.llm_client, self.vector_store)

        # Initialize clients
        self.scholar_client = GoogleScholarClient()
        self.screening_client = ScreeningClient()

    def build_graph(self) -> StateGraph:
        """Build the enhanced summarization workflow graph"""

        workflow = StateGraph(WorkflowState)

        workflow.add_node("load_prompts", self._load_prompts)
        workflow.add_node("retrieve_pdf_context", self._retrieve_pdf_context)
        workflow.add_node("retrieve_scholar_context", self._retrieve_scholar_context)
        workflow.add_node("merge_contexts", self._merge_contexts)
        workflow.add_node("generate_answers", self._generate_answers)
        workflow.add_node("validate_answers", self._validate_answers)
        workflow.add_node("build_screening", self._build_screening)

        workflow.set_entry_point("load_prompts")
        workflow.add_edge("load_prompts", "retrieve_pdf_context")
        workflow.add_edge("retrieve_pdf_context", "retrieve_scholar_context")
        workflow.add_edge("retrieve_scholar_context", "merge_contexts")
        workflow.add_edge("merge_contexts", "generate_answers")
        workflow.add_edge("generate_answers", "validate_answers")
        workflow.add_edge("validate_answers", "build_screening")
        workflow.add_edge("build_screening", END)

        return workflow.compile()

    async def _load_prompts(self, state: WorkflowState) -> WorkflowState:
        """Load questionnaire prompts from Firestore - matches original behavior"""
        try:
            logger.info(
                f"Loading prompts for attorney: {self.attorney_id}, applicant: {self.applicant_id}"
            )

            client = FireStoreDB().client
            doc_ref = client.collection("templates").document("eb1_a_questionnaire")
            doc = doc_ref.get()

            if not doc.exists:
                state["error"] = "No questionnaire found for applicant."
                return state

            js = doc.to_dict()
            tasks = js.get("task")

            # Store prompts using original Prompt dataclass
            prompts = [
                Prompt(
                    question=task.get("question"),
                    detail_level=task.get("detail_level"),
                    tag=task.get("tag"),
                    attorney_id=self.attorney_id,
                    applicant_id=self.applicant_id,
                )
                for task in tasks
            ]

            state["prompts"] = prompts
            logger.info(f"Loaded {len(prompts)} prompts and stored in state")
            logger.info(f"State keys: {list(state.keys())}")
            logger.info(f"State prompts length: {len(state.get('prompts', []))}")

        except Exception as e:
            logger.error(f"Error loading prompts: {e}")
            state["error"] = f"Error fetching questionnaire for applicant. {e}"

        return state

    async def _retrieve_pdf_context(self, state: WorkflowState) -> WorkflowState:
        """Retrieve context from vectorized PDF documents"""
        if state.get("error"):
            return state

        try:
            prompts = state.get("prompts", [])
            logger.info(f"Retrieving PDF context for {len(prompts)} prompts")
            logger.info(f"State keys in retrieve_pdf_context: {list(state.keys())}")
            logger.info(
                f"First prompt question: {prompts[0].question if prompts else 'No prompts'}"
            )

            # Parallel retrieval tasks for document context
            async def retrieve_document_for_prompt(prompt):
                # Start with no filters to get all documents
                filters = {}

                # Handle tag - can be string or list according to Prompt model
                if prompt.tag:
                    if isinstance(prompt.tag, list):
                        filters["tag"] = prompt.tag
                    else:
                        filters["tag"] = [prompt.tag]

                # Handle filename - can be string or list according to Prompt model
                if prompt.filename:
                    if isinstance(prompt.filename, list):
                        filters["filename"] = prompt.filename
                    else:
                        filters["filename"] = [prompt.filename]

                logger.info(f"Searching with filters: {filters}")
                logger.info(f"Question: {prompt.question}")

                # Use multi-query search for better results
                results = await self.vector_store.multi_query_search(
                    prompt.question, filters
                )

                logger.info(
                    f"Found {len(results)} results for question: {prompt.question[:50]}..."
                )

                # Store document context and sources
                prompt.document_context = self.vector_store.format_context(results)
                prompt.document_sources = self.vector_store.format_sources(results)

                logger.info(f"Document sources: {prompt.document_sources}")
                return prompt

            # Execute all document retrievals in parallel
            document_tasks = [
                retrieve_document_for_prompt(prompt) for prompt in prompts
            ]
            updated_prompts = await asyncio.gather(*document_tasks)

            state["prompts"] = updated_prompts

        except Exception as e:
            logger.error(f"Error retrieving document context: {e}")
            state["error"] = f"Error retrieving document context: {e}"

        return state

    async def _retrieve_scholar_context(self, state: WorkflowState) -> WorkflowState:
        """Retrieve Google Scholar context for the applicant"""
        if state.get("error"):
            return state

        try:
            logger.info(
                f"Retrieving Google Scholar context for {self.attorney_id}/{self.applicant_id}"
            )

            # Retrieve scholar data from Firestore
            scholar_data = await self.scholar_client.find_top_k(
                attorney_id=self.attorney_id, applicant_id=self.applicant_id, k=1
            )

            if not scholar_data:
                logger.warning("No Google Scholar data found")
                # Continue without scholar data
                prompts = state.get("prompts", [])
                for prompt in prompts:
                    prompt.scholar_context = ""
                    prompt.scholar_sources = ""
                # Make sure prompts are still in state
                state["prompts"] = prompts
                return state

            # Extract relevant scholar information - find_top_k returns (document, doc_id) tuples
            scholar_info = scholar_data[0][0] if scholar_data else None

            # Build comprehensive scholar context
            scholar_context_parts = []

            if hasattr(scholar_info, "author") and scholar_info.author:
                author = scholar_info.author
                scholar_context_parts.append(f"Author: {author.name}")
                if hasattr(author, "scholar_id") and author.scholar_id:
                    scholar_context_parts.append(f"Scholar ID: {author.scholar_id}")
                if hasattr(author, "affiliation") and author.affiliation:
                    scholar_context_parts.append(f"Affiliation: {author.affiliation}")
                if hasattr(author, "interests") and author.interests:
                    scholar_context_parts.append(
                        f"Research Interests: {', '.join(author.interests)}"
                    )

            if hasattr(scholar_info, "publications") and scholar_info.publications:
                pub_context = "Publications:\n"
                for i, pub in enumerate(
                    scholar_info.publications[:20]
                ):  # Limit to top 20 for context
                    pub_context += f"{i+1}. {pub.title}\n"
                    if hasattr(pub, "citations") and pub.citations:
                        pub_context += f"   Citations: {pub.citations}\n"
                    if hasattr(pub, "year") and pub.year:
                        pub_context += f"   Year: {pub.year}\n"
                    pub_context += "\n"
                scholar_context_parts.append(pub_context)

            if hasattr(scholar_info, "metrics") and scholar_info.metrics:
                metrics = scholar_info.metrics
                metrics_context = "Research Metrics:\n"
                if hasattr(metrics, "citations") and metrics.citations:
                    metrics_context += f"Total Citations: {metrics.citations}\n"
                if hasattr(metrics, "h_index") and metrics.h_index:
                    metrics_context += f"H-index: {metrics.h_index}\n"
                if hasattr(metrics, "i10_index") and metrics.i10_index:
                    metrics_context += f"I10-index: {metrics.i10_index}\n"
                scholar_context_parts.append(metrics_context)

            # Combine all scholar context
            combined_scholar_context = "\n\n".join(scholar_context_parts)

            # Add scholar context to all prompts
            prompts = state.get("prompts", [])
            for prompt in prompts:
                prompt.scholar_context = combined_scholar_context
                prompt.scholar_sources = f"Google Scholar Profile: {scholar_info.author.name if hasattr(scholar_info, 'author') and scholar_info.author else 'Unknown'}"

            # Make sure prompts are still in state
            state["prompts"] = prompts
            logger.info(
                f"Successfully retrieved Google Scholar context for {len(prompts)} prompts"
            )

        except Exception as e:
            logger.error(f"Error retrieving scholar context: {e}")
            # Continue without scholar data
            for prompt in state.get("prompts", []):
                prompt.scholar_context = ""
                prompt.scholar_sources = ""

        return state

    async def _merge_contexts(self, state: WorkflowState) -> WorkflowState:
        """Merge PDF and Scholar contexts for comprehensive answers"""
        if state.get("error"):
            return state

        try:
            prompts = state.get("prompts", [])
            logger.info(f"Merging contexts for {len(prompts)} prompts")

            for prompt in prompts:
                # Combine document and Scholar contexts
                contexts = []
                sources = []

                if hasattr(prompt, "document_context") and prompt.document_context:
                    contexts.append(f"DOCUMENT CONTEXT:\n{prompt.document_context}")
                    if hasattr(prompt, "document_sources") and prompt.document_sources:
                        sources.append(f"Documents: {prompt.document_sources}")

                if hasattr(prompt, "scholar_context") and prompt.scholar_context:
                    contexts.append(f"RESEARCHER PROFILE:\n{prompt.scholar_context}")
                    if hasattr(prompt, "scholar_sources") and prompt.scholar_sources:
                        sources.append(f"Scholar: {prompt.scholar_sources}")

                # Merge contexts
                prompt.context = (
                    "\n\n".join(contexts) if contexts else "No context available"
                )
                prompt.sources = (
                    " | ".join(sources) if sources else "No sources available"
                )

        except Exception as e:
            logger.error(f"Error merging contexts: {e}")
            state["error"] = f"Error merging contexts: {e}"

        return state

    async def _generate_answers(self, state: WorkflowState) -> WorkflowState:
        """Generate comprehensive answers using both PDF and Scholar contexts"""
        if state.get("error"):
            return state

        try:
            prompts = state.get("prompts", [])

            # Parallel answer generation
            async def generate_for_prompt(prompt):
                # Enhanced system prompt for comprehensive answers
                system_prompt = f"""You are an expert immigration consultant helping to prepare EB-1A visa applications. 
                
Your task is to provide comprehensive, detailed answers based on the provided context from both research documents and the applicant's Google Scholar profile.

Guidelines:
1. Use specific examples and citations from the provided documents
2. Reference the applicant's research metrics, publications, and impact
3. Provide {prompt.detail_level} level of detail as requested
4. Be factual and evidence-based
5. Connect the research to broader field impact and significance
6. Use professional, academic language appropriate for immigration applications

Answer the question using the provided context."""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Context:\n{prompt.context}\n\nQuestion: {prompt.question}\n\nPlease provide a {prompt.detail_level} answer based on the context provided.",
                    },
                ]

                answer = await self.llm_client.generate_response(messages)
                prompt.answer = answer if answer else "No response generated"

                logger.info(f"Generated answer for prompt: {prompt.question[:50]}...")
                return prompt

            # Execute all generations in parallel
            answer_tasks = [generate_for_prompt(prompt) for prompt in prompts]
            updated_prompts = await asyncio.gather(*answer_tasks)

            state["prompts"] = updated_prompts

        except Exception as e:
            logger.error(f"Error generating answers: {e}")
            state["error"] = (
                f"Error generating summary. Error code: {type(e).__name__}. Error message: {e}"
            )

        return state

    async def _validate_answers(self, state: WorkflowState) -> WorkflowState:
        """Validate all answers - matches original validation logic"""
        if state.get("error"):
            return state

        try:
            prompts = state.get("prompts", [])

            # Parallel validation
            async def validate_prompt(prompt):
                # Original validation prompt
                validation_prompt = f"Here is a question: {prompt.question}.\nHere is the answer: {prompt.answer}.\nIs this answer even a little bit appropriate response to the question? Respond in true or false. no additional text."

                messages = [{"role": "user", "content": validation_prompt}]
                validation_response = await self.llm_client.generate_response(messages)

                # Original validation logic
                if "false" in validation_response.lower():
                    prompt.answer = "Invalid response from AI. Either data is missing or question is not applicable to you."
                    prompt.source = "N/A"
                    logger.warning(
                        f"Answer validation failed for: {prompt.question[:50]}..."
                    )

                return prompt

            # Execute all validations in parallel
            validation_tasks = [validate_prompt(prompt) for prompt in prompts]
            validated_prompts = await asyncio.gather(*validation_tasks)

            state["prompts"] = validated_prompts

        except Exception as e:
            logger.error(f"Error validating answers: {e}")
            state["error"] = (
                f"Error validating answers. Error code: {type(e).__name__}. Error message: {e}"
            )

        return state

    async def _build_screening(self, state: WorkflowState) -> WorkflowState:
        """Build ScreeningBuilder object and save to Firestore - matches original behavior"""
        if state.get("error"):
            return state

        try:
            prompts = state.get("prompts", [])
            logger.info("Building screening object")

            # Create ScreeningBuilder with prompts
            screening = ScreeningBuilder()
            screening.attorney_id = self.attorney_id
            screening.applicant_id = self.applicant_id

            # Add each prompt as a QandA object to the summary
            for prompt in prompts:
                from database.schema import QandA

                qanda = QandA(
                    question=prompt.question,
                    answer=prompt.answer,
                    source=prompt.sources if hasattr(prompt, "sources") else "N/A",
                )
                screening.summary.append(qanda)

            # Save to Firestore
            logger.info("Storing screening in Firestore")
            doc_id = await self.screening_client.insert(
                attorney_id=self.attorney_id,
                applicant_id=self.applicant_id,
                doc=screening,
            )
            logger.info(f"Screening stored in Firestore with ID: {doc_id}")

            state["screening"] = screening
            state["screening_id"] = doc_id

        except Exception as e:
            logger.error(f"Error building screening: {e}")
            state["error"] = f"Error building screening: {e}"

        return state

    async def execute_with_ids(
        self, attorney_id: str, applicant_id: str, prompt: Prompt = None
    ) -> Dict[str, Any]:
        """Execute workflow with specific attorney and applicant IDs"""
        self._initialize(attorney_id, applicant_id)

        if prompt:
            prompt.attorney_id = attorney_id
            prompt.applicant_id = applicant_id

        result = await self.execute(prompt)
        return result


async def main():
    logger.info("Starting enhanced summarize workflow")

    try:
        attorney_id = "test_orison_attorney"
        applicant_id = "test_orison_applicant"

        # Create and run workflow - it handles all initialization internally
        workflow = SummarizeWorkflow()
        result = await workflow.execute_with_ids(attorney_id, applicant_id)

        if result.get("error"):
            logger.error(f"Workflow failed: {result['error']}")
            return

        # Display results
        prompts = result.get("prompts")
        screening_id = result.get("screening_id")

        logger.info(
            f"Workflow completed successfully! Generated {len(prompts)} answers"
        )
        logger.info(
            f"Screening saved with ID: {screening_id if screening_id else 'None'}"
        )

        for i, prompt in enumerate(prompts, 1):
            logger.info(f"\n--- Question {i} ---")
            logger.info(f"Question: {prompt.question}")
            logger.info(f"Detail Level: {prompt.detail_level}")
            logger.info(f"Answer: {prompt.answer}")
            logger.info(
                f"Sources: {prompt.sources if hasattr(prompt, 'sources') else 'N/A'}"
            )

        logger.info("\nEnhanced summarize workflow completed successfully!")

    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
