from typing import TypedDict, List, Dict, Any, Annotated
import operator
from langgraph.graph import StateGraph, END
from agents.supervisor import supervisor_agent
from agents.fundamental import fundamental_agent
from agents.sentiment import sentiment_agent
from agents.risk import risk_agent
from agents.report import report_agent

class AgentState(TypedDict):
    query: str
    intent: str
    parsed_tickers: List[str]
    portfolio_weights: Dict[str, float]
    fundamental_data: Dict[str, Any]
    sentiment_data: Dict[str, Any]
    risk_data: Dict[str, Any]
    final_report: str
    logs: Annotated[List[str], operator.add]

def route_after_supervisor(state: AgentState):
    """
    Routing logic after Supervisor Agent:
    - conceptual_rag -> Direct to Report Node (RAG mode)
    - stock_research / portfolio_risk / sentiment_query -> Parallel fan-out execution
    """
    intent = state.get("intent", "single_stock")
    if intent == "conceptual_rag":
        return "report"
    return ["fundamental", "sentiment", "risk"]

def create_stock_assistant_graph():
    """
    Constructs the LangGraph orchestration workflow for Stock Research & Portfolio Assistant.
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("fundamental", fundamental_agent)
    workflow.add_node("sentiment", sentiment_agent)
    workflow.add_node("risk", risk_agent)
    workflow.add_node("report", report_agent)

    # Set Entrypoint
    workflow.set_entry_point("supervisor")

    # Conditional Edges from Supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "report": "report",
            "fundamental": "fundamental",
            "sentiment": "sentiment",
            "risk": "risk"
        }
    )

    # Converge parallel branches into Report node
    workflow.add_edge("fundamental", "report")
    workflow.add_edge("sentiment", "report")
    workflow.add_edge("risk", "report")
    
    # End workflow after Report
    workflow.add_edge("report", END)

    return workflow.compile()

# Instantiated graph executable
stock_research_graph = create_stock_assistant_graph()

def run_research_pipeline(user_query: str) -> dict:
    """
    Executes the full LangGraph research workflow for a given user query.
    """
    initial_state = {
        "query": user_query,
        "intent": "",
        "parsed_tickers": [],
        "portfolio_weights": {},
        "fundamental_data": {},
        "sentiment_data": {},
        "risk_data": {},
        "final_report": "",
        "logs": []
    }
    
    final_state = stock_research_graph.invoke(initial_state)
    return final_state
