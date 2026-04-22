from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class WorkflowState(TypedDict):
    workflow_run_id: str
    user_request: str
    research_complete: bool
    research_summary: str
    final_response: str


def research_agent(state: WorkflowState) -> dict[str, object]:
    return {
        "research_complete": True,
        "research_summary": f"Research complete for: {state['user_request']}",
    }


def reviewer_agent(state: WorkflowState) -> dict[str, object]:
    approved = bool(state["research_summary"])
    return {"research_complete": approved}


def finalize_agent(state: WorkflowState) -> dict[str, object]:
    return {"final_response": f"Final answer: {state['research_summary']}"}


def route_after_review(state: WorkflowState) -> Literal["finalize", "research"]:
    if state["research_complete"]:
        return "finalize"
    return "research"


def build_workflow(checkpointer):
    """
    The checkpointer should be backed by PostgreSQL in production so the graph
    can resume from durable checkpoints after worker failure.
    """

    graph = StateGraph(WorkflowState)
    graph.add_node("research", research_agent)
    graph.add_node("review", reviewer_agent)
    graph.add_node("finalize", finalize_agent)

    graph.add_edge(START, "research")
    graph.add_edge("research", "review")
    graph.add_conditional_edges(
        "review",
        route_after_review,
        {"research": "research", "finalize": "finalize"},
    )
    graph.add_edge("finalize", END)

    return graph.compile(checkpointer=checkpointer)
