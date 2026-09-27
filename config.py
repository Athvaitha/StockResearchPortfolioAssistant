import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Ticker mapping for common names to Yahoo Finance standard symbols
TICKER_MAP = {
    "INFOSYS": "INFY.NS",
    "INFY": "INFY.NS",
    "TCS": "TCS.NS",
    "TATA CONSULTANCY SERVICES": "TCS.NS",
    "RELIANCE": "RELIANCE.NS",
    "RELIANCE INDUSTRIES": "RELIANCE.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "HDFC": "HDFCBANK.NS",
    "TATA MOTORS": "TATAMOTORS.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "ICICI BANK": "ICICIBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "WIPRO": "WIPRO.NS",
    "STATE BANK OF INDIA": "SBIN.NS",
    "SBIN": "SBIN.NS",
    "SBI": "SBIN.NS",
    "BHARTI AIRTEL": "BHARTIARTL.NS",
    "AIRTEL": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "L&T": "LT.NS",
    "LARSEN & TOUBRO": "LT.NS",
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
    "GOOGLE": "GOOGL",
    "NVIDIA": "NVDA",
    "TESLA": "TSLA"
}

def normalize_ticker(symbol: str) -> str:
    clean = symbol.strip().upper()
    if clean in TICKER_MAP:
        return TICKER_MAP[clean]
    if clean.endswith(".NS") or clean.endswith(".BO") or "^" in clean or "." in clean:
        return clean
    # Default to .NS if purely alphabetic for Indian market context unless standard US
    us_tickers = {"AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"}
    if clean in us_tickers:
        return clean
    return f"{clean}.NS"
