import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from agent import run_auto_analysis, run_chat

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="Data Analysis Agent",
    page_icon="📊",
    layout="wide",
)

# ── STYLING ──
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3 {
            font-family: 'Syne', sans-serif;
        }
        .main { background-color: #0f0f0f; color: #f0f0f0; }
        .block-container { padding: 2rem 3rem; }

        .stat-card {
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            text-align: center;
        }
        .stat-label {
            font-size: 0.75rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }
        .stat-value {
            font-family: 'Syne', sans-serif;
            font-size: 1.6rem;
            font-weight: 800;
            color: #f0f0f0;
            margin-top: 0.3rem;
        }
        .chat-user {
            background: #f0f0ff;
            border-radius: 10px;
            padding: 0.8rem 1rem;
            margin: 0.5rem 0;
            border-left: 3px solid #6c63ff;
            color: #1a1a1a;
        }
        .chat-agent {
            background: #f0faf6;
            border-radius: 10px;
            padding: 0.8rem 1rem;
            margin: 0.5rem 0;
            border-left: 3px solid #00c896;
            color: #1a1a1a;
        }
        .section-title {
            font-family: 'Syne', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            color: #aaa;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)


# ── SESSION STATE INIT ──
# Session state = Streamlit's memory. Without it, everything resets on each interaction.
if "df" not in st.session_state:
    st.session_state.df = None
if "auto_results" not in st.session_state:
    st.session_state.auto_results = None
if "auto_summary" not in st.session_state:
    st.session_state.auto_summary = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_display" not in st.session_state:
    st.session_state.chat_display = []


# ── HEADER ──
st.markdown("<h1 style='font-size:2.5rem; margin-bottom:0'>📊 Data Analysis Agent</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#888; margin-top:0.3rem'>Upload a CSV or use the default sales dataset. The agent will analyze it automatically.</p>", unsafe_allow_html=True)
st.divider()


# ── SIDEBAR: DATA SOURCE ──
with st.sidebar:
    st.markdown("### 📁 Data Source")
    data_source = st.radio("Choose data source:", ["Use default dataset", "Upload your own CSV"])

    if data_source == "Upload your own CSV":
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            if not df.equals(st.session_state.df if st.session_state.df is not None else pd.DataFrame()):
                st.session_state.df = df
                st.session_state.auto_results = None
                st.session_state.chat_history = []
                st.session_state.chat_display = []
    else:
        try:
            df = pd.read_csv("default_dataset.csv")
            if st.session_state.df is None:
                st.session_state.df = df
        except FileNotFoundError:
            st.error("default_dataset.csv not found. Please place it in the same folder as app.py.")
            st.stop()

    if st.session_state.df is not None:
        st.success(f"✅ {len(st.session_state.df)} rows loaded")
        st.markdown("**Columns:**")
        for col in st.session_state.df.columns:
            st.markdown(f"- `{col}`")

    st.divider()
    if st.button("🔄 Reset Analysis", use_container_width=True):
        st.session_state.auto_results = None
        st.session_state.auto_summary = ""
        st.session_state.chat_history = []
        st.session_state.chat_display = []
        st.rerun()


# ── MAIN: AUTO ANALYSIS ──
if st.session_state.df is not None:

    # Run auto analysis only once per dataset load
    if st.session_state.auto_results is None:
        with st.spinner("🤖 Agent is analyzing your data..."):
            results, summary = run_auto_analysis(st.session_state.df)
            st.session_state.auto_results = results
            st.session_state.auto_summary = summary

    # ── STATS CARDS ──
    stats = None
    for r in st.session_state.auto_results:
        if r["tool"] == "get_summary_stats":
            stats = r["output"]
            break

    if stats:
        st.markdown("<div class='section-title'>Key Metrics</div>", unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        cards = [
            (c1, "Total Sales", f"₹{stats['total_sales']:,}"),
            (c2, "Total Profit", f"₹{stats['total_profit']:,}"),
            (c3, "Best Product", stats["best_product"]),
            (c4, "Best Region", stats["best_region"]),
            (c5, "Profit Margin", f"{stats['avg_profit_margin_percent']}%"),
        ]
        for col, label, value in cards:
            with col:
                st.markdown(f"""
                    <div class='stat-card'>
                        <div class='stat-label'>{label}</div>
                        <div class='stat-value'>{value}</div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CHARTS ──
    charts = [r for r in st.session_state.auto_results if r["tool"] != "get_summary_stats"]

    if charts:
        st.markdown("<div class='section-title'>Charts</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        for i, r in enumerate(charts):
            fig = r["output"]
            if i % 2 == 0:
                with col1:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                with col2:
                    st.plotly_chart(fig, use_container_width=True)

    # ── AGENT SUMMARY ──
    if st.session_state.auto_summary:
        st.markdown("<div class='section-title'>Agent Summary</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-agent'>🤖 {st.session_state.auto_summary}</div>", unsafe_allow_html=True)

    st.divider()

    # ── CHAT ──
    st.markdown("<div class='section-title'>Ask the Agent</div>", unsafe_allow_html=True)

    # Display chat history
    for msg in st.session_state.chat_display:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-agent'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
            if "charts" in msg:
                for fig in msg["charts"]:
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#f0f0f0",
                    )
                    st.plotly_chart(fig, use_container_width=True)

    # Chat input
    user_input = st.chat_input("Ask something about your data...")

    if user_input:
        # Add user message to display and history
        st.session_state.chat_display.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("🤖 Thinking..."):
            results, response_text = run_chat(
                st.session_state.df,
                st.session_state.chat_history,
                user_input,
            )

        # Collect any charts from this response
        charts_in_response = [r["output"] for r in results if r["tool"] != "get_summary_stats"]

        # Add agent response to display
        st.session_state.chat_display.append({
            "role": "assistant",
            "content": response_text,
            "charts": charts_in_response,
        })

        # Add to history (text only — charts aren't part of OpenAI message history)
        st.session_state.chat_history.append({"role": "assistant", "content": response_text})

        st.rerun()

else:
    st.info("👈 Select a data source from the sidebar to get started.")