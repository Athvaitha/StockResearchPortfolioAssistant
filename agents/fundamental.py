from mcp_server.tools import get_financials, get_price
from rag.knowledge_base import get_rag_context

def fundamental_agent(state: dict) -> dict:
    """
    Fundamental Agent (LangGraph Node):
    Pulls financials via MCP tools and interprets ratios using RAG definitions.
    """
    tickers = state.get("parsed_tickers", ["INFY.NS"])
    logs = [f"Fundamental Agent: Fetching financial data for {tickers}"]

    fundamental_data = {}
    for ticker in tickers:
        fin = get_financials(ticker)
        price_info = get_price(ticker)
        
        rag_pe = get_rag_context("Price to Earnings Ratio P/E valuation")
        rag_de = get_rag_context("Debt to Equity Ratio leverage")
        
        fundamental_data[ticker] = {
            "financials": fin,
            "price_metrics": price_info,
            "rag_insights": {
                "pe_explanation": rag_pe,
                "de_explanation": rag_de
            }
        }

    logs.append(f"Fundamental Agent: Successfully extracted financial statements and metrics for {len(tickers)} companies.")

    return {
        "fundamental_data": fundamental_data,
        "logs": logs
    }
