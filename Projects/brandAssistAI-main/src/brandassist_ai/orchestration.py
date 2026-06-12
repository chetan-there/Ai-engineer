from __future__ import annotations

from typing import Any, List, Optional, TypedDict

from .models import AgentResponse


class GraphState(TypedDict):
    message: str
    image_id: Optional[str]
    history: Optional[List[Any]]
    image_bytes: Optional[bytes]
    image_mime: Optional[str]
    response: Optional[AgentResponse]


class GraphOrchestrator:
    """LangGraph wrapper for explicit state-machine execution."""

    def __init__(self, agent: object) -> None:
        self.agent = agent
        from langgraph.graph import END, StateGraph

        graph = StateGraph(GraphState)
        graph.add_node("run_agent_core", self._run_agent_core)
        graph.set_entry_point("run_agent_core")
        graph.add_edge("run_agent_core", END)
        self.graph = graph.compile()

    def _run_agent_core(self, state: GraphState) -> GraphState:
        response = self.agent._run_core(  # noqa: SLF001
            state["message"],
            state.get("image_id"),
            state.get("history"),
            state.get("image_bytes"),
            state.get("image_mime"),
        )
        return {
            "message": state["message"],
            "image_id": state.get("image_id"),
            "history": state.get("history"),
            "image_bytes": state.get("image_bytes"),
            "image_mime": state.get("image_mime"),
            "response": response,
        }

    def run(
        self,
        message: str,
        image_id: Optional[str] = None,
        history: Optional[List[Any]] = None,
        image_bytes: Optional[bytes] = None,
        image_mime: Optional[str] = None,
    ) -> AgentResponse:
        state = self.graph.invoke(
            {
                "message": message,
                "image_id": image_id,
                "history": history,
                "image_bytes": image_bytes,
                "image_mime": image_mime,
                "response": None,
            }
        )
        return state["response"]
