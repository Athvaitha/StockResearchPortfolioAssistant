"""
FastMCP / standard Python MCP server entry point.
Exposes get_price, get_financials, and calc_portfolio_risk over stdin/stdout or FastMCP.
"""
from mcp.server.fastmcp import FastMCP
from mcp_server.tools import get_price as tool_get_price
from mcp_server.tools import get_financials as tool_get_financials
from mcp_server.tools import calc_portfolio_risk as tool_calc_portfolio_risk

mcp = FastMCP("stock-research-mcp-server")

@mcp.tool()
def get_price(ticker_symbol: str, period: str = "1y") -> dict:
    """Returns current and historical price metrics for a stock ticker."""
    return tool_get_price(ticker_symbol, period)

@mcp.tool()
def get_financials(ticker_symbol: str) -> dict:
    """Returns fundamental financial ratios, valuation, revenue growth, and ROE for a ticker."""
    return tool_get_financials(ticker_symbol)

@mcp.tool()
def calc_portfolio_risk(holdings: dict) -> dict:
    """Computes volatility, weighted beta, and concentration metrics for a set of holdings and weights."""
    return tool_calc_portfolio_risk(holdings)

if __name__ == "__main__":
    mcp.run()
