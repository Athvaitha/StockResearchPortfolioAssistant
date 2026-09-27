import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from graph import run_research_pipeline
from mcp_server.tools import get_price, get_financials, calc_portfolio_risk
from config import normalize_ticker

# Set Page Config
st.set_page_config(
    page_title="Stock Research & Portfolio Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Neat & Clean modern UI)
st.markdown("""
<style>
    /* Dark glassmorphic theme styling */
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 18px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        text-align: center;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #8b9bb4;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #00e676;
        margin-top: 4px;
    }
    .disclaimer-box {
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 4px solid #ff9800;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.9rem;
        color: #ffb74d;
        margin-top: 15px;
    }
    .agent-log-box {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
        font-family: monospace;
        font-size: 0.85rem;
        color: #58a6ff;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/isometric-folders/100/line-chart.png", width=64)
    st.title("Stock Analyst AI")
    st.caption("Powered by LangGraph, MCP & SEBI RAG")
    
    st.divider()
    st.markdown("### 🔍 Presets & Quick Queries")
    
    if st.button("📈 Research summary of Infosys"):
        st.session_state["user_query"] = "Give me a research summary of Infosys."
    
    if st.button("⚖️ Analyze Portfolio Risk (40% TCS, 30% HDFC, 30% Reliance)"):
        st.session_state["user_query"] = "My portfolio is 40% TCS, 30% HDFC Bank and 30% Reliance. How risky is it?"
    
    if st.button("💡 What does P/E ratio of 35 mean?"):
        st.session_state["user_query"] = "What does a P/E ratio of 35 mean for this company?"
    
    if st.button("📰 Recent sentiment around Tata Motors"):
        st.session_state["user_query"] = "What is the recent news sentiment around Tata Motors?"

    st.divider()
    st.markdown("### 🛡️ Guardrails")
    st.success("✅ SEBI Compliance Filter Active")
    st.info("🚫 Strictly NO Buy / Sell Advice")

# Title Header
st.title("📊 Stock Research & Portfolio Assistant")
st.markdown("Educational fundamental analysis, news sentiment, and portfolio risk evaluation.")

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 AI Research Assistant", 
    "💼 Portfolio Risk Builder", 
    "📚 Financial RAG Glossary", 
    "🛠️ MCP Tools Inspector"
])

# TAB 1: AI Research Assistant (LangGraph Multi-Agent Workflow)
with tab1:
    st.subheader("Interactive Research Note Generator")
    
    default_q = st.session_state.get("user_query", "Give me a research summary of Infosys.")
    query_input = st.text_input("Enter stock or portfolio question:", value=default_q, key="main_q_input")
    
    col_btn, col_blank = st.columns([1, 4])
    with col_btn:
        run_btn = st.button("🚀 Run Agentic Analysis", type="primary", use_container_width=True)

    if run_btn or "last_result" in st.session_state:
        if run_btn:
            with st.spinner("LangGraph Multi-Agent Workflow Executing... (Supervisor -> Fundamental, Sentiment, Risk -> Report)"):
                result = run_research_pipeline(query_input)
                st.session_state["last_result"] = result

        res = st.session_state.get("last_result")
        if res:
            st.markdown("---")
            
            # Agent Logs Accordion
            with st.expander("🤖 View LangGraph Orchestration & Agent Trace Logs", expanded=False):
                st.markdown("<div class='agent-log-box'>", unsafe_allow_html=True)
                for log_line in res.get("logs", []):
                    st.write(f"• {log_line}")
                st.markdown("</div>", unsafe_allow_html=True)

            # Display stock price chart if tickers analyzed
            tickers = res.get("parsed_tickers", [])
            if tickers and res.get("intent") != "conceptual_rag":
                st.subheader("📈 Historical Price Movement (Last 60 Days)")
                chart_cols = st.columns(min(len(tickers), 3))
                for idx, t_sym in enumerate(tickers[:3]):
                    with chart_cols[idx]:
                        price_data = get_price(t_sym)
                        if price_data.get("dates"):
                            df_chart = pd.DataFrame({
                                "Date": pd.to_datetime(price_data["dates"]),
                                "Price": price_data["prices"]
                            })
                            fig = px.line(
                                df_chart, x="Date", y="Price", 
                                title=f"{t_sym} Price (Current: ₹{price_data['current_price']})",
                                color_discrete_sequence=["#00e676"]
                            )
                            fig.update_layout(template="plotly_dark", height=260, margin=dict(l=20, r=20, t=40, b=20))
                            st.plotly_chart(fig, use_container_width=True)

            # Render Research Note
            st.markdown(res.get("final_report", ""))

# TAB 2: Portfolio Risk Builder
with tab2:
    st.subheader("💼 Interactive Portfolio Weight Builder & Risk Analysis")
    st.write("Construct custom stock weight allocations to compute weighted beta, volatility, and concentration index.")

    col_holdings, col_chart = st.columns([2, 2])
    
    with col_holdings:
        st.markdown("#### Set Allocation Percentage (%)")
        w_tcs = st.slider("TCS (Tata Consultancy Services)", 0, 100, 40)
        w_hdfc = st.slider("HDFC Bank", 0, 100, 30)
        w_rel = st.slider("Reliance Industries", 0, 100, 30)
        w_infy = st.slider("Infosys", 0, 100, 0)
        w_tatamotors = st.slider("Tata Motors", 0, 100, 0)
        
        portfolio_dict = {
            "TCS.NS": w_tcs,
            "HDFCBANK.NS": w_hdfc,
            "RELIANCE.NS": w_rel,
            "INFY.NS": w_infy,
            "TATAMOTORS.NS": w_tatamotors
        }
        # Filter non-zero
        active_portfolio = {k: v for k, v in portfolio_dict.items() if v > 0}

    with col_chart:
        if active_portfolio:
            df_port = pd.DataFrame({
                "Stock": list(active_portfolio.keys()),
                "Weight": list(active_portfolio.values())
            })
            fig_pie = px.pie(df_port, values="Weight", names="Stock", title="Portfolio Asset Allocation", hole=0.4)
            fig_pie.update_layout(template="plotly_dark", height=320)
            st.plotly_chart(fig_pie, use_container_width=True)

    if active_portfolio:
        risk_res = calc_portfolio_risk(active_portfolio)
        st.markdown("---")
        st.subheader("⚡ Portfolio Risk Metrics Summary")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Weighted Beta</div><div class='metric-value'>{risk_res['portfolio_weighted_beta']}</div></div>", unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Est. Annualized Volatility</div><div class='metric-value'>{risk_res['annualized_volatility_pct']}%</div></div>", unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>HHI Concentration Index</div><div class='metric-value'>{risk_res['hhi_concentration_index']}</div></div>", unsafe_allow_html=True)
        with m_col4:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Overall Risk Level</div><div class='metric-value' style='color:#ff9800;'>{risk_res['overall_risk_rating']}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"**Concentration Analysis**: {risk_res['concentration_level']}. {risk_res['summary_notes']}")

# TAB 3: Financial RAG Glossary
with tab3:
    st.subheader("📚 SEBI Investor Education & Financial RAG Knowledge Base")
    rag_query = st.text_input("Search educational term or SEBI rule (e.g. 'P/E Ratio', 'Beta', 'Diversification'):", value="Price to Earnings Ratio P/E valuation")
    
    if rag_query:
        from rag.knowledge_base import kb_instance
        docs = kb_instance.search(rag_query, top_k=4)
        for doc in docs:
            with st.container():
                st.markdown(f"### 📌 {doc['topic']}")
                st.caption(f"Category: {doc['category']} | Source: {doc['source']}")
                st.write(doc['content'])
                st.divider()

# TAB 4: MCP Tools Inspector
with tab4:
    st.subheader("🛠️ Model Context Protocol (MCP) Server Tool Tester")
    st.write("Inspect raw outputs returned directly by the MCP tools (`get_price`, `get_financials`, `calc_portfolio_risk`).")

    mcp_col1, mcp_col2 = st.columns(2)
    with mcp_col1:
        selected_ticker = st.selectbox("Select Stock Ticker:", ["INFY.NS", "TCS.NS", "RELIANCE.NS", "HDFCBANK.NS", "TATAMOTORS.NS"])
        if st.button("Run `get_price` MCP Tool"):
            res = get_price(selected_ticker)
            st.json(res)

        if st.button("Run `get_financials` MCP Tool"):
            res = get_financials(selected_ticker)
            st.json(res)

    with mcp_col2:
        st.write("Test `calc_portfolio_risk` MCP Tool")
        if st.button("Run `calc_portfolio_risk` for 40% TCS, 30% HDFC, 30% Reliance"):
            res = calc_portfolio_risk({"TCS.NS": 0.40, "HDFCBANK.NS": 0.30, "RELIANCE.NS": 0.30})
            st.json(res)
