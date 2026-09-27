import re
from config import normalize_ticker, TICKER_MAP

def supervisor_agent(state: dict) -> dict:
    """
    Supervisor Agent (LangGraph Node):
    Parses user query, determines query intent type, extracts tickers & weights,
    and sets execution plan for downstream agents.
    """
    query = state.get("query", "").strip()
    logs = [f"Supervisor Agent: Analyzing query intent for '{query}'"]

    query_lower = query.lower()
    intent = "single_stock" # default
    parsed_tickers = []
    portfolio_weights = {}

    # Check portfolio risk intent
    if "portfolio" in query_lower or "%" in query_lower or "risky" in query_lower:
        intent = "portfolio_risk"
        matches = re.findall(r'(\d+)%\s*([A-Za-z0-9&\s]+?)(?:,|$|\band\b)', query)
        if matches:
            for pct, name in matches:
                clean_name = name.strip()
                norm = normalize_ticker(clean_name)
                try:
                    portfolio_weights[norm] = float(pct) / 100.0
                    parsed_tickers.append(norm)
                except ValueError:
                    pass

    # Check conceptual / educational questions
    elif any(q_word in query_lower for q_word in ["what does", "what is", "meaning", "definition", "explain", "glossary", "how to read"]):
        if not any(ticker_kw in query_lower for ticker_kw in ["infosys", "tcs", "reliance", "tatamotors", "hdfc"]):
            intent = "conceptual_rag"

    # Check news sentiment query
    elif "sentiment" in query_lower or "news" in query_lower:
        intent = "sentiment_query"

    # Extract tickers if single stock or sentiment query
    if intent in ["single_stock", "sentiment_query"]:
        found_tickers = []
        for name in TICKER_MAP:
            if name.lower() in query_lower:
                found_tickers.append(TICKER_MAP[name])

        if not found_tickers:
            words = re.findall(r'\b[A-Z]{2,10}(?:\.NS)?\b', query)
            for w in words:
                if w.upper() not in ["WHAT", "HOW", "GIVE", "NEWS", "STOCK", "DATA", "THE", "FOR", "BUY", "SELL"]:
                    found_tickers.append(normalize_ticker(w))

        if not found_tickers:
            found_tickers = ["INFY.NS"]

        parsed_tickers = list(dict.fromkeys(found_tickers))

    logs.append(f"Supervisor Agent: Identified Intent = '{intent}', Parsed Tickers = {parsed_tickers}, Portfolio = {portfolio_weights}")

    return {
        "intent": intent,
        "parsed_tickers": parsed_tickers,
        "portfolio_weights": portfolio_weights,
        "logs": logs
    }
