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

from orison_ai.workflows.base import BaseWorkflow, WorkflowState
from orison_ai.workflows.models import Prompt, DetailLevel
from orison_ai.core.environment import get_env
from orison_ai.core.config import VectorConfig, LLMConfig, AppConfig
from orison_ai.database.secrets import OrisonSecrets
from orison_ai.core.client import LLMClient
from orison_ai.storage.vector_store import VectorStore
from orison_ai.database.firestore_clients import ChatMemoryClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Disable langsmith logging
logging.getLogger("langsmith").setLevel(logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)


class DocAssistWorkflow(BaseWorkflow):
    """LangGraph workflow for document assistance - matches original behavior"""

    def __init__(self):
        """Initialize the workflow - actual initialization happens when IDs are provided"""
        self.graph = None
        self.llm_client = None
        self.vector_store = None

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
        self.chat_memory_client = ChatMemoryClient()

        # Initialize base class
        super().__init__(self.llm_client, self.vector_store)

    def build_graph(self) -> StateGraph:
        """Build the document assistance workflow graph"""

        workflow = StateGraph(WorkflowState)

        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("generate_response", self._generate_response)

        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("retrieve_context", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    async def _retrieve_context(self, state: WorkflowState) -> WorkflowState:
        """Retrieve relevant document context - matches original behavior"""
        try:
            # Extract question from messages
            question = state["messages"][-1]["content"]

            # Build filters from prompt if available
            filters = {}
            prompt_data = state.get("prompt_data", {})

            if prompt_data.get("tag") and prompt_data["tag"]:
                filters["tag"] = prompt_data["tag"]
            if prompt_data.get("filename") and prompt_data["filename"]:
                filters["filename"] = prompt_data["filename"]

            # Use multi-query search for better retrieval
            results = await self.vector_store.multi_query_search(question, filters)

            # Store context and sources
            context = self.vector_store.format_context(results)
            sources = self.vector_store.format_sources(results)

            logger.info(f"Retrieved {len(results)} results for docassist query")

            state["context"] = context
            state["sources"] = sources

        except Exception as e:
            state["error"] = (
                f"Error generating response from DocAssist. Error code: {type(e).__name__}. Error message: {e}"
            )

        return state

    async def _generate_response(self, state: WorkflowState) -> WorkflowState:
        """Generate response using context - matches original behavior"""
        if state.get("error"):
            return state

        try:
            question = state["messages"][-1]["content"]
            context = state.get("context", "")

            # Prepare the final prompt exactly as original
            user_message = f"Given the context: \n{context}, \n answer the following: {question} in light detail."

            # Generate response using the LLM client
            messages = [
                {"role": "system", "content": self.llm_client.SYSTEM_ROLE},
                {"role": "user", "content": user_message},
            ]

            # Use plain response instead of streaming
            response = await self.llm_client.generate_response(messages)

            # Format response with source information exactly as original
            sources = state.get("sources", "N/A")
            output_message = response + f" (Source: {sources})"

            # Store the final response
            state["response"] = output_message

            # Save conversation to chat memory
            try:
                await self.chat_memory_client.store_conversation(
                    attorney_id=self.attorney_id,
                    applicant_id=self.applicant_id,
                    user_message=question,
                    assistant_response=output_message,
                )
                logger.info("Conversation saved to chat memory")
            except Exception as e:
                logger.error(f"Error saving conversation to memory: {e}")
                # Don't fail the main operation if memory save fails

        except Exception as e:
            state["error"] = (
                f"Error generating response from DocAssist. Error code: {type(e).__name__}. Error message: {e}"
            )

        return state

    async def execute_with_ids(
        self,
        attorney_id: str,
        applicant_id: str,
        question: str,
        tag=None,
        filename=None,
    ) -> Dict[str, Any]:
        """Execute the workflow with specific attorney and applicant IDs"""
        self._initialize(attorney_id, applicant_id)

        try:
            logger.info(f"Executing docassist with question: {question}")

            # Handle tag and filename as lists for the workflow
            tag_list = tag if isinstance(tag, list) else [tag] if tag else []
            filename_list = (
                filename
                if isinstance(filename, list)
                else [filename] if filename else []
            )

            # Create prompt
            prompt = Prompt(
                question=question,
                tag=tag_list,
                filename=filename_list,
                detail_level=DetailLevel.LIGHT,
            )

            # Execute the workflow
            result = await self.execute(prompt)

            if result.get("error"):
                error_message = f"Error generating response from DocAssist. Error code: {type(result['error']).__name__}. Error message: {result['error']}"
                logger.error(error_message)
                return {"error": error_message}

            output_message = result.get("response", "No response generated")

            return {"success": True, "response": output_message}

        except Exception as e:
            message = f"Error generating response from DocAssist. Error code: {type(e).__name__}. Error message: {e}"
            logger.error(message, exc_info=True)
            return {"error": message}

    async def execute(self, prompt: Prompt) -> Dict[str, Any]:
        """Execute the workflow with a prompt"""
        self.graph = self.build_graph()

        # Initialize state with prompt data
        initial_state = WorkflowState(
            messages=[{"role": "user", "content": prompt.question}],
            context="",
            sources="",
            error=None,
            prompt_data={"tag": prompt.tag, "filename": prompt.filename},
        )

        result = await self.graph.ainvoke(initial_state)
        return result


async def main():
    """Main function to run the docassist workflow"""
    logger.info("Starting docassist workflow")

    try:
        # Test request matching the original
        request_json = {
            "attorneyId": "test_orison_attorney",
            "applicantId": "test_orison_applicant",
            "message": "Give me a summary of Rishi's skills",
            "tag": [],
            "filename": ["MalhanCV.pdf"],
        }

        # Create and run workflow
        workflow = DocAssistWorkflow()
        result = await workflow.execute_with_ids(
            attorney_id=request_json["attorneyId"],
            applicant_id=request_json["applicantId"],
            question=request_json["message"],
            tag=request_json["tag"],
            filename=request_json["filename"],
        )

        if result.get("error"):
            logger.error(f"Workflow failed: {result['error']}")
            return

        logger.info(f"Workflow completed successfully!")
        logger.info(f"Response: {result.get('response', 'No response')}")

    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
