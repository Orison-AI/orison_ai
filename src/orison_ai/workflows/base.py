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

# External

from typing import TypedDict, Annotated, List, Dict, Any, Optional
import operator
from langgraph.graph import StateGraph
from langchain_core.messages import BaseMessage, HumanMessage


class WorkflowState(TypedDict):
    """Base state for all workflows"""

    messages: Annotated[List[BaseMessage], operator.add]
    context: str
    sources: str
    error: Optional[str]
    prompts: Optional[List]
    response: Optional[str]


class BaseWorkflow:
    """Base class for LangGraph workflows"""

    def __init__(self, llm_client, vector_store):
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.graph = None

    def build_graph(self) -> StateGraph:
        """Override in subclasses to build the specific workflow graph"""
        raise NotImplementedError

    async def execute(self, prompt=None) -> Dict[str, Any]:
        """Execute the workflow"""
        if not self.graph:
            self.graph = self.build_graph()

        initial_state = WorkflowState(
            messages=[HumanMessage(content=prompt.question if prompt else "")],
            context="",
            sources="",
            error=None,
            prompts=[],
            response=None,
        )

        result = await self.graph.ainvoke(initial_state)
        return result
