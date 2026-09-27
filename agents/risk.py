from mcp_server.tools import calc_portfolio_risk
from rag.knowledge_base import get_rag_context

def risk_agent(state: dict) -> dict:
    """
    Risk Agent (LangGraph Node):
    Runs portfolio risk calculations via MCP tool and explains volatility, beta, concentration.
    """
    weights = state.get("portfolio_weights", {})
    tickers = state.get("parsed_tickers", ["INFY.NS"])
    logs = ["Risk Agent: Computing risk profile..."]

    if not weights:
        n = len(tickers)
        weights = {t: round(1.0 / n, 2) for t in tickers}

    risk_result = calc_portfolio_risk(weights)
    rag_risk_info = get_rag_context("Beta Coefficient Systematic Risk Portfolio Concentration")

    risk_data = {
        "portfolio_metrics": risk_result,
        "rag_risk_explanation": rag_risk_info
    }

    logs.append(f"Risk Agent: Calculated weighted beta = {risk_result['portfolio_weighted_beta']} and concentration rating = '{risk_result['concentration_level']}'.")

    return {
        "risk_data": risk_data,
        "logs": logs
    }
