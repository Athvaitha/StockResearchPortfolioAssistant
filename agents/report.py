import datetime
from rag.knowledge_base import get_rag_context

MANDATORY_DISCLAIMER = (
    "\n\n---\n"
    "### ⚠️ Regulatory Guardrail & Mandatory Disclaimer\n"
    "**Disclaimer**: This research note is strictly for **educational and informational purposes only** "
    "and does **not** constitute financial advice, investment recommendations, or buy/sell instructions. "
    "All financial ratios, news sentiment indicators, and portfolio risk calculations are based on historical and "
    "publicly available data. Retail investors should perform independent due diligence and consult a SEBI-registered "
    "financial advisor before making investment decisions.\n"
    f"**Data Reference Date**: {datetime.date.today().strftime('%Y-%m-%d')}"
)

def report_agent(state: dict) -> dict:
    """
    Report Agent (LangGraph Node):
    Combines findings into a structured educational research note with required disclaimer.
    """
    logs = ["Report Agent: Compiling final educational research note..."]

    intent = state.get("intent", "single_stock")
    query = state.get("query", "")
    tickers = state.get("parsed_tickers", ["INFY.NS"])
    fundamental_data = state.get("fundamental_data", {})
    sentiment_data = state.get("sentiment_data", {})
    risk_data = state.get("risk_data", {})
    as_of_date = datetime.date.today().strftime("%Y-%m-%d")

    # If pure conceptual RAG query
    if intent == "conceptual_rag":
        rag_text = get_rag_context(query)
        report = (
            f"# 📖 Educational Financial Concept Note\n"
            f"**Query**: {query}\n"
            f"**Data Reference Date**: {as_of_date}\n\n"
            f"## Key Definitions & SEBI Investor Framework\n\n"
            f"{rag_text}\n\n"
            f"## Analytical Context\n"
            f"Understanding fundamental financial metrics helps investors evaluate risk and valuation objectively "
            f"without relying on market rumors or speculative tips."
            f"{MANDATORY_DISCLAIMER}"
        )
        return {"final_report": report, "logs": logs}

    # Standard Research Note compilation
    sections = []
    sections.append(f"# 📊 Stock & Portfolio Educational Research Note")
    sections.append(f"**Target Securities**: {', '.join(tickers)}")
    sections.append(f"**Analysis Date**: {as_of_date}\n")

    # 1. Executive Summary & Overview
    sections.append("## 1. Business & Fundamental Financial Overview")
    for t in tickers:
        f_info = fundamental_data.get(t, {}).get("financials", {})
        if f_info:
            sections.append(
                f"### {f_info.get('company_name', t)} (`{t}`)\n"
                f"- **Sector / Industry**: {f_info.get('sector', 'N/A')} | {f_info.get('industry', 'N/A')}\n"
                f"- **Current Market Price**: ₹{f_info.get('current_price', 'N/A')}\n"
                f"- **P/E Ratio**: `{f_info.get('pe_ratio', 'N/A')}` *(Price to Earnings)*\n"
                f"- **P/B Ratio**: `{f_info.get('pb_ratio', 'N/A')}` *(Price to Book)*\n"
                f"- **Debt-to-Equity Ratio**: `{f_info.get('debt_to_equity', 'N/A')}`\n"
                f"- **Return on Equity (ROE)**: `{f_info.get('roe_percentage', 'N/A')}%`\n"
                f"- **Revenue Growth (YoY)**: `{f_info.get('revenue_growth', 'N/A')}%`\n"
            )

    # 2. News & Sentiment Analysis
    sections.append("\n## 2. Recent News & Sentiment Profile")
    for t in tickers:
        s_info = sentiment_data.get(t, {})
        if s_info:
            sections.append(f"### Sentiment for {t}: **{s_info.get('overall_sentiment', 'Neutral')}**")
            sections.append("Key Recent News Drivers & Evidence:")
            for art in s_info.get("articles", [])[:3]:
                sections.append(f"- **{art['title']}** [{art['sentiment']}]\n  *{art['snippet']}*")

    # 3. Portfolio & Risk Metrics
    sections.append("\n## 3. Risk Assessment & Volatility Analysis")
    p_risk = risk_data.get("portfolio_metrics", {})
    if p_risk:
        sections.append(
            f"- **Portfolio Weighted Beta**: `{p_risk.get('portfolio_weighted_beta', 'N/A')}` "
            f"*(> 1.0 indicates higher volatility than market benchmark)*\n"
            f"- **Estimated Annualized Volatility**: `{p_risk.get('annualized_volatility_pct', 'N/A')}%`\n"
            f"- **Concentration Rating**: `{p_risk.get('concentration_level', 'N/A')}`\n"
            f"- **Overall Risk Rating**: `{p_risk.get('overall_risk_rating', 'N/A')}`\n"
        )
        if "holdings_breakdown" in p_risk:
            sections.append("**Asset Allocation Breakdown**:")
            for h in p_risk["holdings_breakdown"]:
                sections.append(f"  - `{h['ticker']}`: {h['weight_pct']}% allocation | Beta: {h['beta']}")

    # 4. Educational Insights & Open Questions
    sections.append("\n## 4. Educational Insights & Investor Questions")
    sections.append(
        "**Key Questions for Investor Reflection**:\n"
        "1. Is the P/E ratio aligned with historical industry averages or justified by earnings growth?\n"
        "2. Does the company maintain sufficient liquidity and manageable Debt-to-Equity leverage?\n"
        "3. Is the portfolio adequately diversified across non-correlated sectors (e.g. Banking, Tech, Energy)?\n"
    )

    # Guardrail Check
    raw_report = "\n".join(sections)
    sanitized_report = raw_report.replace("buy instructions", "educational notes").replace("sell instructions", "educational notes")
    final_report = sanitized_report + MANDATORY_DISCLAIMER

    logs.append("Report Agent: Final educational research note generated successfully with mandatory SEBI guardrails.")

    return {
        "final_report": final_report,
        "logs": logs
    }
